#!/usr/bin/env python3

import asyncio
from asyncio.subprocess import PIPE

from rpcudp.protocol import RPCProtocol


# Any methods starting with "rpc_" are available to clients.
class RPCServer(RPCProtocol):
    senders_tasks = {}

    async def rpc_exec_shell(self, sender, command):
        process = await self._start_process(sender, command)
        # Run in background
        asyncio.ensure_future(self._monitor_stdout(sender, process))
        asyncio.ensure_future(self._monitor_stderr(sender, process))
        asyncio.ensure_future(self._wait_for_process_end(sender, process))

    def rpc_consume_input(self, sender, data):
        self._write_stdin(self.senders_tasks[sender], data)

    # Private functions
    async def _start_process(self, sender, command):
        process = await asyncio.create_subprocess_shell(command, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        self.senders_tasks[sender] = process
        return process

    async def _wait_for_process_end(self, sender, process):
        result = await process.wait()
        del self.senders_tasks[sender]
        protocol.consume_return_code(sender, result)

    @staticmethod
    async def _monitor_stdout(sender, process):
        while True:
            line = await process.stdout.readline()
            if line:
                protocol.consume_stdout(sender, line)
            else:
                break

    @staticmethod
    async def _monitor_stderr(sender, process):
        while True:
            line = await process.stderr.readline()
            if line:
                protocol.consume_stderr(sender, line)
            else:
                break

    @staticmethod
    def _write_stdin(process, data):
        if data == b'\4':  # End Of Transmission (EOT) character
            process.stdin.close()
        else:
            process.stdin.write(data)


loop = asyncio.get_event_loop()
listen = loop.create_datagram_endpoint(RPCServer, local_addr=('127.0.0.1', 1234))
transport, protocol = loop.run_until_complete(listen)
loop.run_forever()
