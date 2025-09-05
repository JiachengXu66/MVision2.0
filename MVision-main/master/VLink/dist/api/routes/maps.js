"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const express = require('express');
const router = express.Router();
const executeSP = require('../execute_SP.js');
const executeF = require('../execute_F.js');
router.get('/graphs', (req, res, next) => {
    const params = [];
    executeF("vision_data", "get_graph_map", params)
        .then(result => {
        res.status(200).json(result);
    })
        .catch(err => {
        res.status(500).json({ error: err });
    });
});
router.get('/class', (req, res, next) => {
    const params = [];
    executeF("vision_data", "get_class_map", params)
        .then(result => {
        res.status(200).json(result);
    })
        .catch(err => {
        res.status(500).json({ error: err });
    });
});
router.get('/configurations', (req, res, next) => {
    const params = [];
    executeF("vision_data", "get_configuration_map", params)
        .then(result => {
        res.status(200).json(result);
    })
        .catch(err => {
        res.status(500).json({ error: err });
    });
});
router.get('/categories', (req, res, next) => {
    const params = [];
    executeF("vision_data", "get_categories_map", params)
        .then(result => {
        res.status(200).json(result);
    })
        .catch(err => {
        res.status(500).json({ error: err });
    });
});
router.get('/counts', (req, res, next) => {
    const params = [];
    executeF("vision_data", "get_count_map", params)
        .then(result => {
        res.status(200).json(result);
    })
        .catch(err => {
        res.status(500).json({ error: err });
    });
});
router.get('/source', (req, res, next) => {
    const params = [];
    executeF("vision_data", "get_source_map", params)
        .then(result => {
        res.status(200).json(result);
    })
        .catch(err => {
        res.status(500).json({ error: err });
    });
});
module.exports = router;
//# sourceMappingURL=maps.js.map