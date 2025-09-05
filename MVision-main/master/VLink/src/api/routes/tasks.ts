const express = require('express');
const router = express.Router();
const executeSP = require('../execute_SP.js');
const executeF= require('../execute_F.js');
const axios = require('axios');

/**
 * @description Creates new model task in the database. If successful it POSTS to the model creation server with the task_id
 *              of the task to complete
 */
router.post('/create', async(req,res,next)=>{
    const _task_id = req.body.task_id || 9999;
    const _model_name = req.body.model_name;
    const _epochs = req.body.epochs;
    const _num_frames = req.body.num_frames;
    const _shuffle_size = req.body.shuffle_size;
    const _batch_size = req.body.batch_size;
    const _creation_date = new Date(req.body.creation_date).toISOString();
    const _status_value = req.body.status_value || 'queue';
    const _train = req.body.train;
    const _test = req.body.test;
    const _verification = req.body.verification;
    const _classes = req.body.classes;
    const _sources = req.body.sources;
    
    const params = [_model_name,_epochs,_num_frames,_shuffle_size,_batch_size,_creation_date,_status_value,_train,_test,_verification,JSON.stringify(_classes)
        ,JSON.stringify(_sources)
    ];
    console.log(params);
    try{
        const taskID = await executeF("vision_data", "insert_model_task", params);
        
        res.status(200).json({ task_id: taskID });
        const modelCreationURL = "http://host.docker.internal:8080/model/create";
        
        axios.post(modelCreationURL, taskID, {
            headers: {
                'Content-Type': 'application/json',
            }
        }).then(() => {
            console.log('Further processing completed successfully.');
        }).catch((err) => {
            console.error('Error during further processing:', err);
        });
    }  
    catch (err) {
        console.error('Error:', err);
        res.status(500).json({ error: err.toString() });
    }
})

/**
 * @description Updates an existing model tasks status within the database. 
 *              Called from the PyTrain server at various stages in the creation process
 */
router.post('/update',(req,res,next)=>{
    const _task_id = req.body.task_id;
    const _status_value = req.body.status_value;
    const params = [_task_id,_status_value];
    executeF("vision_data", "update_model_task_status", params)
    .then(result => {
        res.status(200).json(result);
    })
    .catch(err => {
        res.status(500).json({error: err});
    });
})

/**
 * @description Gets task data for a specific task ID
 */
router.get('/id/:task_id',(req,res,next)=>{
    const _task_id = req.params.task_id;
    const params = [_task_id];
    executeF("vision_data","get_task", params)
    .then(result => {
        res.status(200).json(result);
    })
    .catch(err => {
        res.status(500).json({error: err});
    });
})


/**
 * @description Gets an aggregation of sources for a specific task ID from the taskclass map
 */
router.get('/:task_id/classes',(req,res,next)=>{
    const _task_id = req.params.task_id;
    const params = [_task_id];
    executeF("vision_data","get_task_classes", params)
    .then(result => {
        res.status(200).json(result);
    })
    .catch(err => {
        res.status(500).json({error: err});
    });
})

/**
 * @description Gets an aggregation of sourced for a specific task ID from the tasksource map
 */
router.get('/:task_id/sources',(req,res,next)=>{
    const _task_id = req.params.task_id;
    const params = [_task_id];
    executeF("vision_data","get_task_sources", params)
    .then(result => {
        res.status(200).json(result);
    })
    .catch(err => {
        res.status(500).json({error: err});
    });
})


module.exports = router;