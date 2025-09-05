const pool  = require('../dbconfig.js');

/**
 * @async
 * @param {string} schemaName - Schema Name where function exists
 * @param {string} functionName - Function Name to execute
 * @param {Array} params - Parameters to pass to the function
 * @returns {Promise<Array|String>} - A promise that resolves to the rows returned or throws an error string (will display SQL error)
 * @description Dynamically calls a SQL function within a given SQL schema and supplies parameters in order of the "params" array
 */
async function executeF(schemaName, functionName, params) {
    const client = await pool.connect();
    let result;
    try {
        const paramPlaceholders = params.map((_, index) => `$${index + 1}`).join(', ');
        const queryText = `SELECT ${schemaName}.${functionName}(${paramPlaceholders})`;
        console.log("Executing Query: "+queryText);
        result = await client.query(queryText,params);
    } catch (err) {
        console.log(err);
        return "Error executing function";
    } finally {
        client.release();
    }
    return result ? result.rows : null;
}

module.exports = executeF;