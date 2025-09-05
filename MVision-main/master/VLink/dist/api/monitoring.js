"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const { exec } = require('child_process');
const os = require('os');
const createCsvWriter = require('csv-writer').createObjectCsvWriter;
function generateFilePath() {
    const date = new Date();
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hour = String(date.getHours()).padStart(2, '0');
    const minute = String(date.getMinutes()).padStart(2, '0');
    return `./logs/VLink_Deployment_${year}_${month}_${day}_${hour}_${minute}.csv`;
}
const filePath = generateFilePath();
const csvWriter = createCsvWriter({
    path: filePath,
    header: [
        { id: 'time', title: 'Timestamp' },
        { id: 'event', title: 'Event' },
        { id: 'duration', title: 'Duration' },
    ],
    append: true,
});
async function appendLogs(event, duration) {
    await csvWriter.writeRecords([{
            time: new Date().toISOString(),
            event,
            duration
        }]);
}
module.exports = appendLogs;
//# sourceMappingURL=monitoring.js.map