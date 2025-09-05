import { error } from "console";

const express = require('express');
const router = express.Router();

const executeF= require('../execute_F.js');
const appendLogs = require('../monitoring.js')

/**
 * @description Creates new target in the database. Checks to see whether the inputted data is of 
 *              Person or Location format before sending the request to auto complete relevant 
 *              parameters as null
 */
router.post('/create', (req,res,next)=>{
    const startTime = Date.now();
    const _target_id = req.body.target_id || 9999;
    const _target_name = req.body.target_name;
    const _alt_name = req.body.alt_name;
    const _creation_date = new Date(req.body.creation_date).toISOString();
    const _status_value = req.body.status_value || 'New';
    const _dob = req.body.dob || null;
    const _role = req.body.role || null;
    const _access = req.body.access || null
    try{
        if (_dob === null && _role === null && !(_access === null))
        {
            const params = [_target_name,_alt_name,_creation_date,_status_value,_access,null,null]
            
            const insertResult = executeF("vision_data","insert_targets", params)
            console.log(insertResult.result)
            const duration = Math.round((Date.now() - startTime) / 1000);
            appendLogs(`Created Target`,duration);
            res.status(200).json(insertResult)
        }
        else if(_access === null && !(_dob === null) && !(_role === null))
        {
            const params = [_target_name,_alt_name,_creation_date,_status_value,null,_dob,_role]
            const insertResult = executeF("vision_data","insert_targets", params)
            const duration = Math.round((Date.now() - startTime) / 1000);
            appendLogs(`Created Target`,duration);
            res.status(200).json(insertResult)
        }
        else
        {
            throw "Data configured incorrectly aborting";
        }
    }
    catch(e){
        console.log(e)
    }
    
})

/**
 * @description Gets latest target data given a limit of items per page and the current page number 
 *              (works via the target index)
 */
router.get('/',(req,res,next)=>{
    const _item_limit = parseInt(req.query.itemLimit, 10) || 10; 
    const _current_page = parseInt(req.query.currentPage, 10) || 1;
    const params = [_item_limit,_current_page];
    executeF("vision_data","get_latest_targets", params)
    .then(result => {
        res.status(200).json(result);
    })
    .catch(err => {
        res.status(500).json({error: err});
    });
})

/**
 * @description Gets target data for a specific target ID
 */
router.get('/id/:target_id',(req,res,next)=>{
    const _target_id = req.params.target_id;
    const params = [_target_id];
    executeF("vision_data","get_target", params)
    .then(result => {
        res.status(200).json(result);
    })
    .catch(err => {
        res.status(500).json({error: err});
    });
})

module.exports = router;