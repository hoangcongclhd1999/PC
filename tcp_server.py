import queue
import socket
import threading

from config import (
    TCP_HOST,
    TCP_PORT,
    MAX_BUFFER_CHARS,
)
from protocol_parser import parse_line


class AudioCheckTcpServer:
    """
    Standard-library TCP server.
    Compatible with 32-bit Python on Windows.

    Network threads NEVER touch Tkinter directly.
    All UI actions go into ui_queue.
    """

    def __init__(self, ui_queue, log=print):
        self.ui_queue = ui_queue
        self.log = log

        self._server_socket = None
        self._accept_thread = None
        self._stop_event = threading.Event()

        self._lock = threading.RLock()

        # station -> client socket
        self._station_clients = {}

        # client socket -> station
        self._client_station = {}

    def start(self):
        if self._accept_thread and self._accept_thread.is_alive():
            return True

        self._stop_event.clear()

        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Useful when restarting the app quickly.
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            server.bind((TCP_HOST, TCP_PORT))
            server.listen(32)
            server.settimeout(1.0)
        except OSError as e:
            try:
                server.close()
            except Exception:
                pass

            self.ui_queue.put(
                ("server_error", f"Cannot listen on port {TCP_PORT}: {e}")
            )
            return False

        self._server_socket = server

        self.log(
            f"TCP Server listening on {TCP_HOST}:{TCP_PORT}"
        )

        self.ui_queue.put(
            ("server_started", TCP_HOST, TCP_PORT)
        )

        self._accept_thread = threading.Thread(
            target=self._accept_loop,
            name="AudioCheckAccept",
            daemon=True,
        )
        self._accept_thread.start()

        return True

    def stop(self):
        self._stop_event.set()

        server = self._server_socket
        self._server_socket = None

        if server is not None:
            try:
                server.close()
            except Exception:
                pass

        with self._lock:
            clients = list(self._client_station.keys())

        for client in clients:
            try:
                client.shutdown(socket.SHUT_RDWR)
            except Exception:
                pass

            try:
                client.close()
            except Exception:
                pass

    def _accept_loop(self):
        while not self._stop_event.is_set():
            server = self._server_socket

            if server is None:
                break

            try:
                client, address = server.accept()
            except socket.timeout:
                continue
            except OSError:
                break

            client.settimeout(1.0)

            ip, port = address[0], address[1]

            self.log(
                f"Client connected from {ip}:{port}; "
                f"waiting for Station X message"
            )

            thread = threading.Thread(
                target=self._client_loop,
                args=(client, ip, port),
                name=f"Client-{ip}-{port}",
                daemon=True,
            )
            thread.start()

    def _bind_station(self, client, station):
        """
        Bind one TCP connection to a station.

        If another connection was already bound to the same station,
        close the old one so the newest START wins.
        """
        if not 1 <= station <= 16:
            return False

        old_client = None

        with self._lock:
            current_station = self._client_station.get(client)

            if current_station is not None:
                return current_station == station

            old_client = self._station_clients.get(station)

            self._station_clients[station] = client
            self._client_station[client] = station

        if old_client is not None and old_client is not client:
            self.log(
                f"Station{station}: replacing old connection"
            )

            try:
                old_client.shutdown(socket.SHUT_RDWR)
            except Exception:
                pass

            try:
                old_client.close()
            except Exception:
                pass

        self.ui_queue.put(("connected", station, True))

        return True

    def _client_loop(self, client, ip, port):
        buffer = ""

        try:
            while not self._stop_event.is_set():
                try:
                    data = client.recv(4096)
                except socket.timeout:
                    continue
                except OSError:
                    break

                if not data:
                    break

                text = data.decode("utf-8", errors="ignore")
                buffer += text

                if len(buffer) > MAX_BUFFER_CHARS:
                    self.log(
                        f"{ip}:{port}: receive buffer too large; reset"
                    )
                    buffer = ""

                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    line = line.strip("\r ").strip()

                    if line:
                        self._process_line(
                            client,
                            ip,
                            port,
                            line,
                        )

        finally:
            station = None

            with self._lock:
                station = self._client_station.pop(client, None)

                if station is not None:
                    if self._station_clients.get(station) is client:
                        self._station_clients.pop(station, None)

            try:
                client.close()
            except Exception:
                pass

            if station is not None:
                self.log(
                    f"Station{station} disconnected "
                    f"({ip}:{port})"
                )
                self.ui_queue.put(
                    ("connected", station, False)
                )
                self.ui_queue.put(
                    ("status", station, "Waiting")
                )
            else:
                self.log(
                    f"Unidentified client disconnected "
                    f"({ip}:{port})"
                )

    def _process_line(self, client, ip, port, line):
        self.log(f"RX {ip}:{port}: {line}")

        parsed = parse_line(line)

        station_from_message = parsed["station"]

        with self._lock:
            station_from_socket = self._client_station.get(client)

        # First "Station X: W/T" identifies this connection.
        if station_from_socket is None and station_from_message is not None:
            if self._bind_station(client, station_from_message):
                station_from_socket = station_from_message

        # Safety: once a connection is Station4, don't let it update Station5.
        if (
            station_from_socket is not None
            and station_from_message is not None
            and station_from_socket != station_from_message
        ):
            self.log(
                f"WARNING: connection bound to Station"
                f"{station_from_socket} but message says Station"
                f"{station_from_message}; ignored"
            )
            return

        station = station_from_socket or station_from_message

        # "slot:" needs no UI action.
        if parsed["slot_header"]:
            return

        if station is None:
            self.log(
                f"Ignored '{line}' because Station is unknown"
            )
            return

        # Any valid data proves station is alive.
        self.ui_queue.put(("connected", station, True))

        # D => clear + Waiting
        if parsed["clear"]:
            self.ui_queue.put(("clear", station))

        if parsed["status"] is not None:
            self.ui_queue.put(
                ("status", station, parsed["status"])
            )

        # Result lines automatically imply Testing if T was missed.
        if parsed["results"] and parsed["status"] is None:
            self.ui_queue.put(
                ("status", station, "Testing")
            )

        for slot, value in sorted(parsed["results"].items()):
            self.ui_queue.put(
                ("result", station, slot, value)
            )
