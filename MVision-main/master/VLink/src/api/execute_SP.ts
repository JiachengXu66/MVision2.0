const pool = require('../dbconfig.js');

/**
 * @async
 * @param {string} schemaName - Schema Name where Stored Procedure exists
 * @param {string} storedProcedureName - Stored Procedure Name to execute
 * @param {Array} params - Parameters to pass to the function
 * @returns {Promise<Array|String>} - A promise that resolves to the rows returned or throws an error string (will display SQL error)
 * @description Dynamically calls a SQL SP within a given SQL schema and supplies parameters in order of the "params" array
 */
async function executeSP(schemaName, storedProcedureName, params) {
    console.log(pool);
    const client  = await pool.connect();
    let result;
    try{
      const paramPlaceholders = params.map((_, index) => `$${index + 1}`).join(', ');
      result = await client.query(`CALL ${schemaName}.${storedProcedureName}(${paramPlaceholders})`, params);      
    }
    catch(err){
        console.log(err);
        return "Error executing stored procedure";
    }
    finally{
        client.release();
    }
    return result ? result.rows : null
}

module.exports = executeSP;
