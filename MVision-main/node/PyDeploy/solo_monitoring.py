import configparser
import sys
from aiohttp import web
import asyncio
import getpass
from jtop import jtop
import datetime
from modules.monitoring import DumpLogs, CompilePerformanceEntry, RecurringMonitoring

csvLog = []
global jetson

async def server_up():
    global jetson
    global csvLog

    server = '0.0.0.0'
    port = 1500
    app = web.Application()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, server, port)
    await site.start()
    print(f"Server started at http://{server}:{port}")
    file_path = f"/home/{getpass.getuser()}/Desktop/MVision/node/PyDeploy/analytics/Logs/Triton_Only_Run_{datetime.datetime.now().strftime('%Y_%m_%d_%H_%M')}.csv"
    await CompilePerformanceEntry(jetson, csvLog, "Initialising Logging")
    monitoringTask = loop.create_task(DumpLogs(csvLog, file_path))
    recurringLoggingTask = loop.create_task(RecurringMonitoring(jetson, csvLog, "Logging tick", 3))


async def main():
    await server_up()

if __name__ == "__main__":
    with jtop() as jetson: 
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
        loop.run_forever()