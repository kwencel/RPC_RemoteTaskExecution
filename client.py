#!/usr/bin/env python3

import argparse
import asyncio
import os
import sys

from rpcudp.protocol import RPCProtocol

return_code = 1  # by default assume there was a problem invoking the remote task


# A custom asyncio protocol used for capturing stdin of the Python process
class StdinCaptureProtocol(asyncio.Protocol):
    def __init__(self, protocol, host):
        self.protocol = protocol
        self.host = host

    def data_received(self, data):
        self.protocol.consume_input(self.host, data)

    def connection_lost(self, exc):
        self.protocol.consume_input(self.host, str.encode('\4'))  # End Of Transmission (EOT) character
        super().connection_lost(exc)


# Any methods starting with "rpc_" are available to clients.
class RPCServer(RPCProtocol):
    def rpc_consume_stdout(self, sender, output):
        print(output.decode("utf-8").rstrip('\n'), flush=True)

    def rpc_consume_stderr(self, sender, output):
        print(output.decode("utf-8").rstrip('\n'), file=sys.stderr, flush=True)

    def rpc_consume_return_code(self, sender, retval):
        global return_code
        return_code = retval
        loop.stop()


async def exec_shell(protocol, address, command):
    await protocol.exec_shell(address, command)

parser = argparse.ArgumentParser()
parser.add_argument('command', help='shell command to run on the remote server')
parser.add_argument('--host-address',
                    help='Address of the RPC server. Defaults to 127.0.0.1 or RTASK_HOST_ADDRESS environment variable (if set).',
                    default=os.environ.get('RTASK_HOST_ADDRESS', '127.0.0.1'))
parser.add_argument('--host-port', type=int,
                    help='Port of the server. Defaults to 1234 or RTASK_HOST_PORT environment variable (if set).',
                    default=os.environ.get('RTASK_HOST_PORT', 1234))
parser.add_argument('--client-address',
                    help='Address of the RPC client. Defaults to 127.0.0.1 or RTASK_CLIENT_ADDRESS environment variable (if set).',
                    default=os.environ.get('RTASK_CLIENT_ADDRESS', '127.0.0.1'))
parser.add_argument('--client-port', type=int,
                    help='Port of the client. Defaults to OS-chosen or RTASK_CLIENT_PORT environment variable (if set).',
                    default=os.environ.get('RTASK_CLIENT_PORT', None))
args = parser.parse_args()


# Start local UDP server to be able to handle responses
loop = asyncio.get_event_loop()
listen = loop.create_datagram_endpoint(RPCServer, local_addr=(args.client_address, args.client_port))
transport, protocol = loop.run_until_complete(listen)

# Call remote UDP server to say hi
coroutine = exec_shell(protocol, (args.host_address, args.host_port), args.command)
loop.run_until_complete(coroutine)
loop.run_until_complete(loop.connect_read_pipe(lambda: StdinCaptureProtocol(protocol, (args.host_address, args.host_port)), sys.stdin))
loop.run_forever()
sys.exit(return_code)
