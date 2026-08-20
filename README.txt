AUDIO CHECK PC - TKINTER / WINDOWS 32-BIT
=========================================

This version removes:
- PySide6
- Shiboken
- Qt

Runtime uses only Python standard library:
- tkinter
- socket
- threading
- queue
- re

NETWORK
-------
PC:
192.168.1.10
TCP port:
5001

The program listens on:
0.0.0.0:5001

The Mac mini app connects to:
192.168.1.10:5001

IMPORTANT:
Windows Firewall must allow inbound TCP port 5001.

MAC PROTOCOL
------------
When operator enters Station 4 and presses START:

Station 4: W

PC:
- identifies the socket as Station4
- LED -> GREEN
- status -> Waiting

Atlas begins:

Station 4: T

PC:
- status -> Testing
- yellow background

Every 4 seconds Mac may send:

slot:
1 P
2 P
3 P
4 F
5 P
6 P
7 P
8 P

PC:
- Pass = bold large text
- Fail = bold large text + light red background

When Atlas folders disappear:

D

PC:
- clears ALL Pass/Fail of that station
- Testing -> Waiting
- LED remains GREEN while TCP remains connected

If TCP disconnects:
- LED -> RED
- status -> Waiting

BUILD 32-BIT
------------
You MUST build on Windows using 32-bit Python.

Check:
python -c "import struct; print(struct.calcsize('P')*8)"

It MUST print:
32

Then double-click:

build_windows32.bat

Output:
dist\AudioCheckPC.exe

DEBUG / SEE RECEIVED DATA
-------------------------
Option 1:
run_source_debug.bat

Option 2:
build_windows32_debug.bat

Then run:
dist_debug\AudioCheckPC_Debug.exe

The console will show:
Client connected ...
RX ... Station 4: W
RX ... Station 4: T
RX ... 1 P
RX ... 4 F
RX ... D

WINDOWS FIREWALL
----------------
If Mac cannot connect, allow inbound TCP 5001.

Example command from an Administrator CMD:

netsh advfirewall firewall add rule name="AudioCheckPC TCP 5001" dir=in action=allow protocol=TCP localport=5001
