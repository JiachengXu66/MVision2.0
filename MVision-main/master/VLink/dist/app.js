"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const app = express();
const fs = require('fs');
const executeF = require('./api/execute_F.js');
const startPolling = require('./api/polling.js');
app.set('trust proxy', true);
const os = require('os');
const config = JSON.parse(fs.readFileSync('./config.json', 'utf8'));
const corsOptions = {
    origin: (origin, callback) => {
        if (!origin)
            return callback(null, true);
        if (config.corsIps.includes(origin)) {
            callback(null, true);
        }
        else {
            callback(new Error('Not allowed by CORS'));
        }
    },
};
app.use(cors(corsOptions));
const ipRestrictionMiddleware = async (req, res, next) => {
    try {
        const params = [];
        const response = await executeF("vision_data", "get_approved_nodes", params);
        console.log(req.ip);
        if (req.path === '/nodes/connect' || config.allowedIps.includes(req.ip) || response[0].get_approved_nodes.includes(req.ip)) {
            next();
        }
        else {
            res.status(403).send("Error access denied, you do not have permission to access this resource.");
        }
    }
    catch (error) {
        console.error('Error querying approved nodes:', error.message);
        next();
    }
};
app.use(ipRestrictionMiddleware);
const deploymentRoutes = require('./api/routes/deployments');
const targetRoutes = require('./api/routes/targets');
const reportRoutes = require('./api/routes/reports');
const mapRoutes = require('./api/routes/maps');
const taskRoutes = require('./api/routes/tasks');
const modelRoutes = require('./api/routes/models');
const nodeRoutes = require('./api/routes/nodes');
app.use(bodyParser.urlencoded({ extended: false }));
app.use(bodyParser.json());
app.use('/reports', reportRoutes);
app.use('/targets', targetRoutes);
app.use('/deployments', deploymentRoutes);
app.use('/maps', mapRoutes);
app.use('/tasks', taskRoutes);
app.use('/models', modelRoutes);
app.use('/nodes', nodeRoutes);
app.use((req, res, next) => {
    const error = new Error('Not Found');
    error.status = 404;
    next(error);
});
startPolling();
module.exports = app;
//# sourceMappingURL=app.js.map