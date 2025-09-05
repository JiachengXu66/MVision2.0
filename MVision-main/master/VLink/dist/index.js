"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const http = require('http');
const app = require('./app');
const port = process.env.PORT || 3000;
const server = http.createServer(app);
server.listen(port);
//# sourceMappingURL=index.js.map