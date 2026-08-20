# ==========================================
# AudioCheck PC - CONFIG
# Tkinter / Windows 32-bit compatible
# ==========================================

APP_TITLE = "Audio Check Fail V1.0"

# PC listens for Mac mini connections here
TCP_HOST = "0.0.0.0"
TCP_PORT = 5001

# 16 stations, 8 slots each
STATION_MIN = 1
STATION_MAX = 16
SLOT_MIN = 1
SLOT_MAX = 8

# TCP receive safety
MAX_BUFFER_CHARS = 65536

# UI polling interval for messages coming from network thread
UI_QUEUE_POLL_MS = 50

# Colors
COLOR_CONNECTED = "#7CB342"
COLOR_DISCONNECTED = "#E53935"
COLOR_WAITING = "#BDBDBD"
COLOR_TESTING = "#FFF176"
COLOR_FAIL_BG = "#F4B6B6"
COLOR_CELL = "#FFFFFF"
COLOR_HEADER = "#F2F2F2"
COLOR_BORDER = "#202020"
