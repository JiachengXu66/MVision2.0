"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const express = require('express');
const router = express.Router();
const executeF = require('../execute_F.js');
const appendLogs = require('../monitoring.js');
router.post('/create', async (req, res, next) => {
    console.log(req.body);
    const startTime = Date.now();
    const _report_id = req.body.report_id;
    const _report_name = req.body.report_name;
    const _report_type = req.body.report_type;
    const _deployment_id = req.body.deployment_id;
    const _frequency_value = req.body.frequency_value;
    const _frequency_unit = req.body.frequency_unit;
    const _creation_date = new Date(req.body.creation_date).toISOString();
    const _range_value = req.body.range_value;
    const _range_unit = req.body.range_unit;
    const _graph_id = req.body.graph_id;
    const _threshold = req.body.threshold;
    const _classes = req.body.report_classes;
    const params = [_report_name, _report_type, _deployment_id, _frequency_value, _frequency_unit, _creation_date, _range_value, _range_unit, _graph_id, _threshold];
    const result = await executeF("vision_data", "insert_reports", params);
    const report_id = result[0].insert_reports;
    const params_map = [report_id, JSON.stringify(_classes)];
    executeF("vision_data", "insert_report_class", params_map).then(result => {
        res.status(200).json(result);
    })
        .catch(err => {
        res.status(500).json({ error: err });
    });
});
router.get('/', (req, res, next) => {
    const _item_limit = parseInt(req.query.itemLimit, 10) || 10;
    const _current_page = parseInt(req.query.currentPage, 10) || 1;
    const params = [_item_limit, _current_page];
    executeF("vision_data", "get_latest_reports", params)
        .then(result => {
        res.status(200).json(result);
    })
        .catch(err => {
        res.status(500).json({ error: err });
    });
});
router.get('/id/:report_id', (req, res, next) => {
    const _report_id = req.params.report_id;
    const params = [_report_id];
    executeF("vision_data", "get_report", params)
        .then(result => {
        res.status(200).json(result);
    })
        .catch(err => {
        res.status(500).json({ error: err });
    });
});
router.get('/id/:report_id/classes', (req, res, next) => {
    const _report_id = req.params.report_id;
    const params = [_report_id];
    executeF("vision_data", "get_report_classes", params)
        .then(result => {
        res.status(200).json(result);
    })
        .catch(err => {
        res.status(500).json({ error: err });
    });
});
router.get('/id/:report_id/graph', (req, res, next) => {
    const _report_id = req.params.report_id;
    const params = [_report_id];
    executeF("vision_data", "get_graph_id", params)
        .then(result => {
        res.status(200).json(result);
    })
        .catch(err => {
        res.status(500).json({ error: err });
    });
});
router.get('/id/:report_id/data', (req, res, next) => {
    const _start_date = new Date(new Date(req.query.start_date).getTime() + 3600000).toISOString();
    const _end_date = new Date(new Date(req.query.end_date).getTime() + 3600000).toISOString();
    const _class_id = req.query.class_id;
    const _deployment_id = req.query.deployment_id;
    const _threshold = req.query.threshold;
    const _metric_value = req.query.metric_value || null;
    console.log(_start_date);
    console.log(_end_date);
    const params = [_start_date, _end_date, _class_id, _deployment_id, _threshold, _metric_value];
    console.log(params);
    executeF("vision_data", "get_report_data", params)
        .then(result => {
        res.status(200).json(result);
    })
        .catch(err => {
        res.status(500).json({ error: err });
    });
});
module.exports = router;
//# sourceMappingURL=reports.js.map