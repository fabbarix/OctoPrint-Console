import queue, subprocess, sys, threading, os
import asyncio, websockets
import json

from .token import token
from .ws_shell import WebSocketShell

class ShellServer:

    shellSockets = set()
    
    def __init__(self, logger):
        self.logger = logger
    
    def start(self):
        self.ws_thread = threading.Thread(target=self.start_server_thread, daemon=True)
        self.ws_thread.start()

    def stop(self):
        self.logger.info('Stopping WS Server')
        self.ws_loop.stop()
        for ws in self.shellSockets:
            self.logger('Stopping ws handler...')
            ws.stop_receiver()

    def start_server_thread(self):
        self.ws_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.ws_loop)
        start_server = websockets.serve(self.recv_connection, '0.0.0.0', 6969)
        self.ws_loop.run_until_complete(start_server)
        self.ws_loop.run_forever()
                            
    async def recv_connection(self, websocket):
        self.logger.info(f"Handling new websocket: {str(websocket)}")
        shell = WebSocketShell(websocket, token(), self.logger)
        self.shellSockets.add(shell)
        await shell.start_receiver()
