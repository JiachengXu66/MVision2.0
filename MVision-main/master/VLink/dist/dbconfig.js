"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const Pool = require('pg').Pool;
const config = {
    user: 'dbadmin',
    password: 'password',
    host: 'host.docker.internal',
    port: 5432,
    database: 'ovision',
};
module.exports = new Pool(config);
//# sourceMappingURL=dbconfig.js.map