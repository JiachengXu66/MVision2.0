"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const axios = require('axios');
const { isIPv4, isIPv6 } = require('net');
const executeF = require('./execute_F.js');
const delayPromise = (ms) => new Promise(resolve => setTimeout(resolve, ms));
const pollNodeConnection = async (ip) => {
    const maxAttempts = 3;
    const delay = 5000;
    for (let attempt = 1; attempt <= maxAttempts; attempt++) {
        try {
            const url = `http://${ip}:2500/node/available`;
            const response = await axios.get(url);
            console.log(`Server responded on attempt ${attempt}:`, response.data);
            return "Success";
        }
        catch (error) {
            console.log(`Attempt ${attempt} failed. Error: ${error.message}`);
            if (attempt < maxAttempts) {
                console.log(`Waiting for ${delay / 1000} seconds before next attempt...`);
                await delayPromise(delay);
            }
            else {
                console.log('Max attempts reached. Disconnecting node.');
                return ip;
            }
        }
    }
    return null;
};
const pollNodeDevices = async (ip) => {
    try {
        const url = `http://${ip}:2500/node/cameras`;
        const response = await axios.get(url);
        return response.data;
    }
    catch (error) {
        return;
    }
    ;
};
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
                const get_node = await executeF("vision_data", "get_node_from_addr", [ip]);
                const node_id = get_node[0].get_node_from_addr.node_id;
                await executeF("vision_data", "update_disconnect_all_devices", [node_id]);
                return ipAddress;
            }
            const nodeResponse = await pollNodeDevices(ipAddress);
            if (nodeResponse.get_cameras.cameras && nodeResponse.get_cameras.cameras.length > 0) {
                const camerasJSON = JSON.stringify(nodeResponse.get_cameras.cameras);
                const deviceResponse = await executeF("vision_data", "insert_devices", [camerasJSON, (new Date().toISOString())]);
                const deviceIDs = deviceResponse[0].insert_devices;
                const node_id = nodeResponse.get_cameras.node_id;
                await executeF("vision_data", "update_node_device_map", [node_id, JSON.stringify(deviceIDs), "Connected"]);
                await executeF("vision_data", "update_node_device_map", [node_id, JSON.stringify(deviceIDs), "Disconnected"]);
                console.log("Device status updated for node: ", node_id);
            }
            else if (!nodeResponse.get_cameras.cameras || nodeResponse.get_cameras.cameras.length == 0) {
                const node_id = nodeResponse.get_cameras.node_id;
                await executeF("vision_data", "update_disconnect_all_devices", [node_id]);
                console.log("Devices disconnected for node: ", node_id);
            }
            else {
                console.log("Error accessing devices");
            }
            return null;
        }));
        const failedIPs = timeoutAddresses.filter(ip => ip !== null);
        console.log("Failed or timed out IPs:", failedIPs);
    }
    catch (error) {
        console.error("Error in startPolling:", error.message);
    }
    finally {
        console.log('Scheduling next polling in 3 minutes...');
        setTimeout(startPolling, 30000);
    }
};
module.exports = startPolling;
//# sourceMappingURL=polling.js.map