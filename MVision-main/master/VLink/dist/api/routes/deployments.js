"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const express = require('express');
const router = express.Router();
const executeF = require('../execute_F.js');
const axios = require('axios');
const appendLogs = require('../monitoring.js');
const { isIPv4, isIPv6 } = require('net');
router.post('/create', async (req, res, next) => {
    const startTime = Date.now();
    const _deployment_id = req.body.deployment_id || 9999;
    const _deployment_name = req.body.deployment_name;
    const _target_id = req.body.target_id;
    const _status_value = req.body.status_value || 'New';
    const _model_id = req.body.model_id;
    const _creation_date = new Date(req.body.creation_date).toISOString();
    const _start_date = new Date(req.body.start_date).toISOString();
    const _expiry_date = new Date(req.body.expiry_date).toISOString();
    const _node_id = req.body.node_id;
    const _device_id = req.body.device_id;
    const params = [_deployment_name, _target_id, _status_value, _model_id, _creation_date, _start_date, _expiry_date, _node_id, _device_id];
    try {
        if (_start_date <= _creation_date && _creation_date < _expiry_date) {
            const result = await executeF("vision_data", "insert_deployments", params);
            const _deployment_id = result[0].insert_deployments;
            const params_device = [JSON.stringify([_device_id])];
            const result_device = await executeF("vision_data", "get_devices_details", params_device);
            const device_name = result_device[0].get_devices_details.devices[0].device_name;
            const addr_params = [_node_id];
            const result_addr = await executeF("vision_data", "get_addr_from_node", addr_params);
            console.log(result_addr);
            const address = result_addr[0].get_addr_from_node.node_address;
            console.log(address);
            const ip = isIPv6(address) && address.includes('::ffff:') ? address.split('::ffff:')[1] : address;
            console.log(ip);
            const intialise_deployment_url = `http://${ip}:2500/node/deployments/initialise`;
            const deployment_information = {
                "deployment_information": [
                    {
                        "deployment_id": _deployment_id,
                        "model_id": _model_id,
                        "device_name": device_name
                    }
                ]
            };
            try {
                const deployment_result = await axios.post(intialise_deployment_url, deployment_information, {
                    headers: {
                        'Content-Type': 'application/json',
                    }
                });
                const duration = Math.round((Date.now() - startTime) / 1000);
                await appendLogs(`Deployment: ${_deployment_id} Created and Deployed`, duration);
                res.status(200).json(deployment_result);
            }
            catch (e) {
                const duration = Math.round((Date.now() - startTime) / 1000);
                await appendLogs(`Deployment: ${_deployment_id} Created and Failed to Deploy`, duration);
                res.status(500).json({ error: e });
            }
        }
        else {
            const insert_response = await executeF("vision_data", "insert_deployments", params);
            if (insert_response.status == 200) {
                const duration = Math.round((Date.now() - startTime) / 1000);
                await appendLogs(`Deployment: ${_deployment_id} Created`, duration);
                res.status(200).json(insert_response);
            }
            else {
                const duration = Math.round((Date.now() - startTime) / 1000);
                await appendLogs(`Deployment: ${_deployment_id} Creation Failed`, duration);
                res.status(500).json(insert_response);
            }
        }
    }
    catch (e) {
        console.log(e);
    }
});
router.post('/switch/status', async (req, res, next) => {
    const startTime = Date.now();
    const _deployment_id = req.body.deployment_id || 9999;
    const _deployment_name = req.body.deployment_name;
    const _target_id = req.body.target_id;
    const _status_value = req.body.status_value;
    const _model_id = req.body.model_id;
    const _creation_date = new Date(req.body.creation_date).toISOString();
    const _start_date = new Date(req.body.start_date).toISOString();
    const _expiry_date = new Date(req.body.expiry_date).toISOString();
    const _node_id = req.body.node_id;
    const _device_id = req.body.device_id;
    if (_status_value == 'Active' || _status_value == 'New') {
        const params_device = [JSON.stringify([_device_id])];
        const result_device = await executeF("vision_data", "get_devices_details", params_device);
        const device_name = result_device[0].get_devices_details.devices[0].device_name;
        const addr_params = [_node_id];
        const result_addr = await executeF("vision_data", "get_addr_from_node", addr_params);
        const address = result_addr[0].get_addr_from_node.node_address;
        const ip = isIPv6(address) && address.includes('::ffff:') ? address.split('::ffff:')[1] : address;
        const intialise_deployment_url = `http://${ip}:2500/node/deployments/stop`;
        const deployment_information = {
            "deployment_information": [
                {
                    "deployment_id": _deployment_id,
                    "model_id": _model_id,
                    "device_name": device_name
                }
            ]
        };
        try {
            const initialise_results = await axios.post(intialise_deployment_url, deployment_information, {
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            const params_update = [_deployment_id, "Disabled"];
            const update_result = await executeF("vision_data", "update_deployment_status", params_update);
            const duration = Math.round((Date.now() - startTime) / 1000);
            await appendLogs(`Disabled Deployment: ${_deployment_id} Successfully`, duration);
            res.status(200).json({ result: update_result });
        }
        catch (e) {
            const duration = Math.round((Date.now() - startTime) / 1000);
            await appendLogs(`Disabled Deployment: ${_deployment_id} Unsuccessfully`, duration);
            res.status(500).json({ error: e });
        }
    }
    else if (_status_value == 'Disabled') {
        const params_device = [JSON.stringify([_device_id])];
        const result_device = await executeF("vision_data", "get_devices_details", params_device);
        const device_name = result_device[0].get_devices_details.devices[0].device_name;
        const addr_params = [_node_id];
        const result_addr = await executeF("vision_data", "get_addr_from_node", addr_params);
        console.log(result_addr);
        const address = result_addr[0].get_addr_from_node.node_address;
        console.log(address);
        const ip = isIPv6(address) && address.includes('::ffff:') ? address.split('::ffff:')[1] : address;
        console.log(ip);
        const intialise_deployment_url = `http://${ip}:2500/node/deployments/initialise`;
        const deployment_information = {
            "deployment_information": [
                {
                    "deployment_id": _deployment_id,
                    "model_id": _model_id,
                    "device_name": device_name
                }
            ]
        };
        try {
            const initialise_results = await axios.post(intialise_deployment_url, deployment_information, {
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            const params_update = [_deployment_id, "Active"];
            const update_result = await executeF("vision_data", "update_deployment_status", params_update);
            const duration = Math.round((Date.now() - startTime) / 1000);
            await appendLogs(`Activated Deployment: ${_deployment_id} Successfully`, duration);
            res.status(200).json({ result: update_result });
        }
        catch (e) {
            const duration = Math.round((Date.now() - startTime) / 1000);
            await appendLogs(`Activated Deployment: ${_deployment_id} Unsuccessfully`, duration);
            res.status(500).json({ error: e });
        }
    }
});
router.get('/', (req, res, next) => {
    const _item_limit = parseInt(req.query.itemLimit, 10) || 10;
    const _current_page = parseInt(req.query.currentPage, 10) || 1;
    const params = [_item_limit, _current_page];
    executeF("vision_data", "get_latest_deployments", params)
        .then(result => {
        res.status(200).json(result);
    })
        .catch(err => {
        res.status(500).json({ error: err });
    });
});
router.get('/id/:_deployment_id', (req, res, next) => {
    const _deployment_id = req.params._deployment_id;
    const params = [_deployment_id];
    executeF("vision_data", "get_deployment", params)
        .then(result => {
        res.status(200).json(result);
    })
        .catch(err => {
        res.status(500).json({ error: err });
    });
});
module.exports = router;
//# sourceMappingURL=deployments.js.map