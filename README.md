# RPC_RemoteTaskExecution
An implementation of remote shell command execution using RPCUDP Python library. It allows the host (server) to execute many requests independently and captures the stdout, stdin, stderr and return code which is then returned to the caller (client).

Command's inputs and outputs are buffered until a newline appears. Then it is immediately send to the client - the program does not wait until the command finishes to send the data. The only thing that has to be sent after the command finishes is its return code.

## Build prerequisites
    Python 3.5 or later
    RPCUDP

## Build instructions
```
git clone https://github.com/kwencel/DistributedMonitor
pip install rpcudp
```

## How to use
Invoke the `server.py` and then `client.py` python script with a shell command to run as an argument. If the command contains spaces you can put it in double quotes. The return code of the `client.py` script is the return value of the remotely run command.

**test_progs** directory contains simple C programs that regularry produce output after a fixed amount of delay to simulate long-running processes. Because the implementation makes heavy use of asynchronous processing, I wanted to demonstrate that it is able to concurrently handle many long-running tasks and piping them.
