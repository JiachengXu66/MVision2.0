const express = require('express');
const router = express.Router();
const executeF= require('../execute_F.js');
const appendLogs = require('../monitoring.js')

/**
 * @description Creates a model in the database from a given task ID
 */
router.post('/create',(req,res,next)=>{
    const startTime = Date.now();
    const _task_id = req.body.task_id;
    const _location_name = req.body.location_name;
    const params = [_task_id,_location_name];
    executeF("vision_data", "insert_models", params)
    .then(result => {
        const duration = Math.round((Date.now() - startTime) / 1000);
        appendLogs(`Created Model`,duration);
        res.status(200).json(result);
    })
    .catch(err => {
        res.status(500).json({error: err});
    });
})

/**
 * @description Gets an aggregation of classes for a specific model ID from the taskclass map
 */
router.get('/id/:model_id/classes',(req,res,next)=>{
    const _model_id = req.params.model_id
    const params = [_model_id];
    executeF("vision_data","get_model_classes", params)
    .then(result => {
        res.status(200).json(result);
    })
    .catch(err => {
        res.status(500).json({error: err});
    });
})

/**
 * @description Get each category and the classes associated with them 
 */
router.get('/categories',(req,res,next)=>{
    const params = []
    executeF("vision_data", "get_categorised_classes", params)
    .then(result => {
        res.status(200).json(result);
    })
    .catch(err => {
        res.status(500).json({error: err});
    });
})

/**
 * @description Gets latest model data given a limit of items per page and the current page number 
 *              (works via the model index)
 */
router.get('/',(req,res,next)=>{
    const _item_limit = parseInt(req.query.itemLimit, 10) || 10; 
    const _current_page = parseInt(req.query.currentPage, 10) || 1;
    const params = [_item_limit,_current_page];
    executeF("vision_data","get_latest_models", params)
    .then(result => {
        res.status(200).json(result);
    })
    .catch(err => {
        res.status(500).json({error: err});
    });
})

/**
 * @description Gets model data for a specific model ID
 */
router.get('/id/:model_id',(req,res,next)=>{
    const _model_id = req.params.model_id
    const params = [_model_id];
    executeF("vision_data","get_model", params)
    .then(result => {
        res.status(200).json(result);
    })
    .catch(err => {
        res.status(500).json({error: err});
    });
})

module.exports = router;