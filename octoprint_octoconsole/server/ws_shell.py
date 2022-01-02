import subprocess
import select
import threading
import asyncio

class WebSocketShell:
    def __init__(self, ws, token, logger):
        self.ws = ws
        self.logger = logger
        self.token = token
        self.authenticated = False
        self.shell = None
    
    async def start_receiver(self):
        async for message in self.ws:
            self.logger.info(f"Received message {message}")
            if self.authenticated:
                self.stdin(message)
            else:
                self.logger.info(f"Authenticating")
                await self.auth(message)
        self.logger.info(f"Socket has been closed")
        if self.shell != None:
            self.shell.kill()

    async def stop_receiver(self):
        await self.ws.close()

    async def auth(self, message):
        if message == f"AUTH:{self.token}":
            self.logger.info(f"Authentication Succeeded")
            self.authenticated = True
            await self.ws.send('Connected...\n\r')
            self.logger.info(f"Starting a shell")
            self.shell = subprocess.Popen(["/bin/bash", "-i"], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=0)
            self.stdout()
        else:
            self.logger.info(f"Authentication Failed")
            await self.ws.send('Authentication failed!\n\r')

    def is_ws_connected(self):
        return not self.ws.closed

    def stdin(self, message):
        self.shell.stdin.write(message.encode())
    
    def stdout(self):
        if self.shell == None:
            self.logger.info('This should not happen - ever')
        else:
            self.logger.info("Starting reader thread")
            self.reader_thread = threading.Thread(
                target = self.reader_thread,
                daemon = True
            )
            self.reader_thread.start()

    def reader_thread(self):
        reader_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(reader_loop)
        reader_loop.run_until_complete(self.reader())
        self.logger.info("Reader thread is done")
        reader_loop.close()
        
    async def reader(self):
        read_fds = [ self.shell.stdout.fileno() ]
        
        while True and self.is_ws_connected():
            stdin = select.select(read_fds, [], [], 1.0)
            for fd in stdin:
                self.logger.info("Reading incoming pipe")
                data = self.shell.stdout.read(4096)
                self.logger.info(f"Read {len(data)} bytes")
                if self.is_ws_connected():
                    self.logger.info(f"Sending: {data}")
                    await self.ws.send(data)
            if self.shell.poll() != None:
                self.logger.info(f"Shell is done")
                if self.is_ws_connected():
                    await self.ws.send("<EOF>")
                break
        self.logger.info(f"Reader ending")
