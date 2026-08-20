import queue
import tkinter as tk

from config import UI_QUEUE_POLL_MS
from tcp_server import AudioCheckTcpServer
from ui import AudioCheckWindow


def main():
    root = tk.Tk()

    window = AudioCheckWindow(root)

    # Network threads put events here.
    ui_queue = queue.Queue()

    server = AudioCheckTcpServer(
        ui_queue=ui_queue,
        log=print,
    )

    def process_network_events():
        while True:
            try:
                event = ui_queue.get_nowait()
            except queue.Empty:
                break

            kind = event[0]

            if kind == "connected":
                _, station, connected = event
                window.set_connected(
                    station,
                    connected,
                )

            elif kind == "status":
                _, station, status = event
                window.set_status(
                    station,
                    status,
                )

            elif kind == "result":
                _, station, slot, value = event
                window.set_result(
                    station,
                    slot,
                    value,
                )

            elif kind == "clear":
                _, station = event
                window.clear_station(station)

            elif kind == "server_started":
                _, host, port = event
                window.set_server_started(
                    host,
                    port,
                )

            elif kind == "server_error":
                _, text = event
                window.show_server_error(text)

        root.after(
            UI_QUEUE_POLL_MS,
            process_network_events,
        )

    def close_app():
        server.stop()
        root.destroy()

    root.protocol(
        "WM_DELETE_WINDOW",
        close_app,
    )

    server.start()

    root.after(
        UI_QUEUE_POLL_MS,
        process_network_events,
    )

    root.mainloop()


if __name__ == "__main__":
    main()
