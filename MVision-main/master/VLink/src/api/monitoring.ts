const { exec } = require('child_process');
const os = require('os');
const createCsvWriter = require('csv-writer').createObjectCsvWriter;

/**
 * @returns {string} Filepath string based on the minute the server was started
 * @description Creates the filepath for the current time that the server was launched with
 */
function generateFilePath() {
  const date = new Date();
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  const hour = String(date.getHours()).padStart(2, '0');
  const minute = String(date.getMinutes()).padStart(2, '0');

  return `./logs/VLink_Deployment_${year}_${month}_${day}_${hour}_${minute}.csv`;
}

const filePath = generateFilePath()


/**
 * @type {CsvWriter} - CSV Writer for appending CSV file with log data
 * @description CSV writer set up to append new data entries to an existing CSV file, logging the following columns:
 *              'Timestamp': Time when the event was logged.
 *              'Event': Describes the event
 *              'Duration': Duration of time for the event to complete.
 */
const csvWriter = createCsvWriter({
    path: filePath,
    header: [
      {id: 'time', title: 'Timestamp'},
      {id: 'event', title: 'Event'},
      {id: 'duration', title:'Duration'},
    ],
    append: true,
  });

/**
 * @async
 * @param {string} event - Event description
 * @param {number} duration -  Duration of time for the event to complete.
 * @returns {Promise<void>} A promise that resolves when the log entry has been successfully appended to the CSV file.
 * @description Appends Data in log file with CSVWriter. Data is in timestamp, event, duration format
 */
async function appendLogs(event, duration) {
  await csvWriter.writeRecords([{
      time: new Date().toISOString(),
      event,
      duration
  }]);
}

module.exports = appendLogs;