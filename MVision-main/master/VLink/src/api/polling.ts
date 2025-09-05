const axios = require('axios');
const { isIPv4, isIPv6 } = require('net');
const executeF = require('./execute_F.js');

const delayPromise = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

/**
 * @async
 * @param {string} ip - The IP address of the node to be polled.
 * @returns {Promise<string | null>} - Returns a promise that resolves to "Success" if response is receieved, 
 *                                     IP if it times out and null if it fails                                    
 * @description Executes connection attempts to a node for a given IP address,occurs up to three times with a
 *              set delay of 5 seconds per attempt
 *              Returns either string, where IP indicates lost connection and Success indicates
 */
const pollNodeConnection = async (ip: string): Promise<string | null> => {
  const maxAttempts = 3;
  const delay = 5000;

  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      const url = `http://${ip}:2500/node/available`;
      const response = await axios.get(url);
      console.log(`Server responded on attempt ${attempt}:`, response.data);
      return "Success";
    } catch (error) {
      console.log(`Attempt ${attempt} failed. Error: ${error.message}`);
      if (attempt < maxAttempts) {
        console.log(`Waiting for ${delay / 1000} seconds before next attempt...`);
        await delayPromise(delay);
      } else {
        console.log('Max attempts reached. Disconnecting node.');
        return ip; 
      }
    }
  }
  return null;
};

/**
 * @param {string} ip - The nodes IP address.
 * @returns {Promise<any | null>} - Returns a promise that resolves to the response if a response is recieved,
 *                                  if an error occurs it resolves to null.
 * @async
 * @description Attempts to connect to the given IP address, retrieving and returning camera device information. 
 *             If the request fails due to any error (e.g., network issues, incorrect IP, no response), the function returns `null`.
 */
const pollNodeDevices = async (ip: string): Promise<any | null> => {
    try {
      const url = `http://${ip}:2500/node/cameras`;
      const response = await axios.get(url);
      return response.data;
    } catch (error) {
        return
      };
  }


/**
 * @async
 * @description Retrieves a list of approved nodes and their IP addresses.
 *              Attempts to poll the nodes connection and update the devices on the system.
 *              If the attempt fails it updates the node and device status to 'Disconnected'
 *              Reruns every 3 minutes
 */
const startPolling = async () => {
  try {
    const params = [];
    const response = await executeF("vision_data", "get_approved_nodes", params);
    const timeoutAddresses = await Promise.all(response[0].get_approved_nodes.map(async (ip) => {
      if (!isIPv4(ip) && !(isIPv6(ip) && ip.includes('::ffff:'))) {
        console.log(`Invalid IP Format: ${ip}`);
        return null;
      }

      const ipAddress = isIPv6(ip) && ip.includes('::ffff:') ? ip.split('::ffff:')[1] : ip;
      const result = await pollNodeConnection(ipAddress);
      if (result !== "Success") {
        await executeF("vision_data", "update_node_connection", [ip, "Disconnected"]);
        const getNode = await executeF("vision_data", "get_node_from_addr", [ip]);
        const nodeID = getNode[0].get_node_from_addr.node_id;
        await executeF("vision_data", "update_disconnect_all_devices", [nodeID]);
        return ipAddress;
      }
      
      const nodeResponse = await pollNodeDevices(ipAddress)
      if (nodeResponse.get_cameras.cameras && nodeResponse.get_cameras.cameras.length > 0) {
        const camerasJSON = JSON.stringify(nodeResponse.get_cameras.cameras);
        const deviceResponse = await executeF("vision_data", "insert_devices", [camerasJSON, (new Date().toISOString())]);
        const deviceIDs = deviceResponse[0].insert_devices;
        const nodeID = nodeResponse.get_cameras.node_id;
        await executeF("vision_data", "update_node_device_map", [nodeID, JSON.stringify(deviceIDs), "Connected"]);
        await executeF("vision_data", "update_node_device_map", [nodeID, JSON.stringify(deviceIDs), "Disconnected"]);
        console.log("Device status updated for node: ", nodeID);
      } else if (!nodeResponse.get_cameras.cameras || nodeResponse.get_cameras.cameras.length == 0) {
        const nodeID = nodeResponse.get_cameras.node_id;
        await executeF("vision_data", "update_disconnect_all_devices", [nodeID]);
        console.log("Devices disconnected for node: ", nodeID);
      } else {
        console.log("Error accessing devices");
      }
      return null;
    }));

    const failedIPs = timeoutAddresses.filter(ip => ip !== null);
    console.log("Failed or timed out IPs:", failedIPs);
  } catch (error) {
    console.error("Error in startPolling:", error.message);
  } finally {
    console.log('Scheduling next polling in 3 minutes...');
    setTimeout(startPolling, 30000); 
  }
};
  
module.exports = startPolling;