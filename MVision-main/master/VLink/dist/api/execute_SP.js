"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const pool = require('../dbconfig.js');
async function executeSP(schema_name, stored_procedure_name, params) {
    console.log(pool);
    const client = await pool.connect();
    let result;
    try {
        const paramPlaceholders = params.map((_, index) => `$${index + 1}`).join(', ');
        result = await client.query(`CALL ${schema_name}.${stored_procedure_name}(${paramPlaceholders})`, params);
    }
    catch (err) {
        console.log(err);
        return "Error executing stored procedure";
    }
    finally {
        client.release();
    }
    return result ? result.rows : null;
}
module.exports = executeSP;
//# sourceMappingURL=execute_SP.js.map