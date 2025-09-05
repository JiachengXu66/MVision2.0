const express = require('express');
const router = express.Router();
const executeF= require('../execute_F.js');
const appendLogs = require('../monitoring.js')

/**
 * @description Attempts to create a new node or reconnect an existing node in the database.
 *              If the api key is not present it returns "missing"
 *              If the api key is already used by a different IP or incorrect it returns "different"
 *              If its a new node IP it returns "new"
 *              If its an existing node IP and the api matches it returns "existing"
 */
router.post('/connect',async(req,res,next)=>{
    const startTime = Date.now();
    const _node_key_value = req.body.node_key_value;
    const _node_id = req.body.node_id || null;
    const _node_name = req.body.node_name || null;
    let _creation_date;
    let _node_address;
    if (req.body.creation_date) {
        try {
            let tempDate = new Date(req.body.creation_date);
            if (!isNaN(tempDate.getTime())) { 
                _creation_date = tempDate.toISOString();
            } else {
                _creation_date = null; 
            }
        } catch (error) {
            _creation_date = null; 
        }
    } else {
        _creation_date = null; 
    }
    if(!_node_id){
        _node_address = req.ip;
    }
    else{
        _node_address = null;
    }

    const params = [_node_key_value,_node_id,_node_name,_node_address,_creation_date];
    const result = await executeF("vision_data","create_connection", params);
    const mapResult = result[0].create_connection.map;
    let duration;
    switch(mapResult){
        case "new":
            duration = Math.round((Date.now() - startTime) / 1000);
            await appendLogs(`Connected Node: ${result[0].create_connection.node_id} Successfully`,duration);
            res.status(200).json({status:"Connected",node_id: result[0].create_connection.node_id});
            break;
        case "existing":
            duration = Math.round((Date.now() - startTime) / 1000);
            await appendLogs(`Connected Node: ${result[0].create_connection.node_id} Successfully`,duration);
            res.status(200).json({status:"Connected",node_id: result[0].create_connection.node_id});
            break;
        case "different":
            duration = Math.round((Date.now() - startTime) / 1000);
            await appendLogs(`Key already assigned`,duration);
            res.status(500).json({error: "Key is already assigned to a different node"});
            break;
        case "missing":
            duration = Math.round((Date.now() - startTime) / 1000);
            await appendLogs(`Key invalid`,duration);
            res.status(500).json({error: "Key is invalid"});
            break;
        default:
            duration = Math.round((Date.now() - startTime) / 1000);
            await appendLogs(`Error`,duration);
            res.status(500).json({error: "Unknown error"});
            break;
    }
})

/**
 * @description Attempts to connect devices associated with the node.
 *              Will add devices that do not match existing IDs.
 *              Will add device IDs to nodedevice map that are not already associated with the node.
 *              Will set all devices listed to "connected" to the node in the nodedevice map
 */
router.post('/connect/devices',async(req,res,next)=>{
    const startTime = Date.now();
    const _node_id = req.body.node_id
    const _cameras = req.body.cameras     
    const _date = new Date().toISOString();
    let params = [JSON.stringify(_cameras),_date];
    try{    let result = await executeF("vision_data","insert_devices", params)
            const deviceIDs = result[0].insert_devices
            params = [_node_id,JSON.stringify(deviceIDs),"Connected"];
            result = await executeF("vision_data","update_node_device_map", params)
            const duration = Math.round((Date.now() - startTime) / 1000);
            await appendLogs(`Devices Synced For Node: ${_node_id} Successfully`,duration);
            res.status(200).json({status:"Synced"});
    }
    catch(err){
        const duration = Math.round((Date.now() - startTime) / 1000);
        await appendLogs(`Devices Synced For Node: ${_node_id} Unsuccessfully`,duration);
        res.status(500).json({status: err});
    }
})

/**
 * @description Inserts results into the datatotalentry table.
 */
router.post('/results',async(req,res,next)=>{
    console.log(req.body)
    const startTime = Date.now();
    const _deployment_id = req.body.deployment_id;
    const _data = req.body.data;
    const params = [_deployment_id, JSON.stringify(_data)]
    executeF("vision_data","insert_results", params)
    .then(result => {
        res.status(200).json(result);
    })
    .catch(err => {
        res.status(500).json({error: err});
    });
})

/**
 * @description Gets latest node data given a limit of items per page and the current page number 
 *              (works via the node index)
 */
router.get('/',(req,res,next)=>{
    const _item_limit = parseInt(req.query.itemLimit, 10) || 10; 
    const _current_page = parseInt(req.query.currentPage, 10) || 1;
    const params = [_item_limit,_current_page];
    executeF("vision_data","get_latest_nodes", params)
    .then(result => {
        res.status(200).json(result);
    })
    .catch(err => {
        res.status(500).json({error: err});
    });
})

/**
 * @description Gets number of active deployments given a node ID and device ID
 */
router.get('/deployments/active',(req,res,next)=>{
    const _node_id = parseInt(req.query.node_id);
    const _device_id = parseInt(req.query.device_id);
    const _current_date = new Date().toISOString();
    const params = [_node_id,_device_id, _current_date];
    executeF("vision_data","get_nodes_deployment_models", params)
    .then(result => {
        res.status(200).json(result);
    })
    .catch(err => {
        res.status(500).json({error: err});
    });
})

/**
 * @description Retrieves an existing API key via its ID key
 */
router.get('/key/:key_id',(req,res,next)=>{
    const _key_id = req.params.key_id
    const params = [_key_id];
    executeF("vision_data","get_key", params)
    .then(result => {
        res.status(200).json(result);
    })
    .catch(err => {
        res.status(500).json({error: err});
    });
})

/**
 * @description Get Device ID from its name in the database
 */
router.get('/device/name',(req,res,next)=>{
    const _device_name = req.query.deviceName
    const params = [_device_name];
    executeF("vision_data","get_device_from_name", params)
    .then(result => {
        res.status(200).json(result);
    })
    .catch(err => {
        res.status(500).json({error: err});
    });
})

/**
 * @description Gets latest device data given a limit of items per page and the current page number 
 *              (works via the device index and node ID)
 */
router.get('/id/:node_id/devices/connected',async(req,res,next)=>{
    const _node_id = req.params.node_id
    const _item_limit = parseInt(req.query.itemLimit, 10) || 10; 
    const _current_page = parseInt(req.query.currentPage, 10) || 1;
    let params = [_node_id,_item_limit,_current_page]
    const deviceResult = await executeF("vision_data","get_node_devices", params)
    const deviceIDs = deviceResult[0].get_node_devices.devices
    params = [JSON.stringify(deviceIDs)]
    executeF("vision_data","get_devices_details", params)
    .then(result => {
        res.status(200).json(result);
    })
    .catch(err => {
        res.status(500).json({error: err});
    });
})

/**
 * @description Generates a new API key to connect new nodes to the DB
 */
router.post('/key/generate',(req,res,next)=>{
    const _creation_date = new Date().toISOString();
    const params = [_creation_date];
    executeF("vision_data","insert_node_key", params)
    .then(result => {
        res.status(200).json(result);
    })
    .catch(err => {
        res.status(500).json({error: err});
    });
})

module.exports = router;