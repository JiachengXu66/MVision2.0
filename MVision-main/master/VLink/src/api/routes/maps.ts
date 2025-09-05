const express = require('express');
const router = express.Router();
const executeSP = require('../execute_SP.js');
const executeF= require('../execute_F.js');

/**
 * @description Gets map of graph ID to graph names
 */
router.get('/graphs',(req,res,next)=>{
    const params = [];
    executeF("vision_data","get_graph_map", params)
    .then(result => {
        res.status(200).json(result);
    })
    .catch(err => {
        res.status(500).json({error: err});
    });
})

/**
 * @description Gets map of class ID to class names
 */
router.get('/class',(req,res,next)=>{
    const params = [];
    executeF("vision_data","get_class_map", params)
    .then(result => {
        res.status(200).json(result);
    })
    .catch(err => {
        res.status(500).json({error: err});
    });
})

/**
 * @description Gets map of configurations ID to configuration properties
 */
router.get('/configurations',(req,res,next)=>{
    const params = [];
    executeF("vision_data","get_configuration_map", params)
    .then(result => {
        res.status(200).json(result);
    })
    .catch(err => {
        res.status(500).json({error: err});
    });
})

/**
 * @description Gets map of category IDs to category names
 */
router.get('/categories',(req,res,next)=>{
    const params = []; 
    executeF("vision_data","get_categories_map", params)
    .then(result => {
        res.status(200).json(result);
    })
    .catch(err => {
        res.status(500).json({error: err});
    });
})

/**
 * @description Gets map of total counts of all main objects (targets, models, deployments, reports, nodes, devices)
 */
router.get('/counts',(req,res,next)=>{
    const params = [];
    executeF("vision_data","get_count_map", params)
    .then(result => {
        res.status(200).json(result);
    })
    .catch(err => {
        res.status(500).json({error: err});
    });
})

/**
 * @description Gets map of source IDs to source names
 */
router.get('/source',(req,res,next)=>{
    const params = [];
    executeF("vision_data","get_source_map", params)
    .then(result => {
        res.status(200).json(result);
    })
    .catch(err => {
        res.status(500).json({error: err});
    });
})

module.exports = router;