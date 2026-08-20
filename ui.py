import tkinter as tk
from tkinter import messagebox

from config import (
    APP_TITLE,
    COLOR_CONNECTED,
    COLOR_DISCONNECTED,
    COLOR_WAITING,
    COLOR_TESTING,
    COLOR_FAIL_BG,
    COLOR_CELL,
    COLOR_HEADER,
    COLOR_BORDER,
)


class LedIndicator(tk.Canvas):
    def __init__(self, master, size=18):
        super().__init__(
            master,
            width=size,
            height=size,
            bg=COLOR_HEADER,
            highlightthickness=0,
            bd=0,
        )

        margin = 2

        self._circle = self.create_oval(
            margin,
            margin,
            size - margin,
            size - margin,
            fill=COLOR_DISCONNECTED,
            outline=COLOR_DISCONNECTED,
        )

    def set_connected(self, connected):
        color = (
            COLOR_CONNECTED
            if connected
            else COLOR_DISCONNECTED
        )

        self.itemconfig(
            self._circle,
            fill=color,
            outline=color,
        )


class StationPanel(tk.Frame):
    def __init__(self, master, stations):
        super().__init__(master, bg=COLOR_BORDER)

        self.stations = stations

        self.leds = {}
        self.status_labels = {}
        self.result_labels = {}

        # Column 0 = Slot
        self._make_cell(
            row=0,
            column=0,
            text="Slot",
            bg=COLOR_HEADER,
            font=("Arial", 10),
            rowspan=2,
        )

        for col, station in enumerate(stations, start=1):
            header = tk.Frame(
                self,
                bg=COLOR_HEADER,
                bd=1,
                relief="solid",
            )
            header.grid(
                row=0,
                column=col,
                sticky="nsew",
            )

            header.columnconfigure(0, weight=1)
            header.columnconfigure(1, weight=0)

            title = tk.Label(
                header,
                text=f"Station#{station}",
                bg=COLOR_HEADER,
                font=("Arial", 10),
            )
            title.grid(
                row=0,
                column=0,
                padx=(4, 2),
                pady=4,
                sticky="e",
            )

            led = LedIndicator(header, size=18)
            led.grid(
                row=0,
                column=1,
                padx=(1, 5),
                pady=3,
                sticky="w",
            )

            self.leds[station] = led

            status = self._make_cell(
                row=1,
                column=col,
                text="Waiting",
                bg=COLOR_WAITING,
                font=("Arial", 10, "bold"),
            )

            self.status_labels[station] = status

        for slot in range(1, 9):
            self._make_cell(
                row=slot + 1,
                column=0,
                text=str(slot),
                bg=COLOR_HEADER,
                font=("Arial", 10, "bold"),
            )

            for col, station in enumerate(stations, start=1):
                label = self._make_cell(
                    row=slot + 1,
                    column=col,
                    text="",
                    bg=COLOR_CELL,
                    font=("Arial", 10),
                )

                self.result_labels[(station, slot)] = label

        # Let station columns stretch evenly.
        self.columnconfigure(0, weight=0, minsize=65)

        for col in range(1, len(stations) + 1):
            self.columnconfigure(
                col,
                weight=1,
                minsize=95,
            )

        self.rowconfigure(0, minsize=31)
        self.rowconfigure(1, minsize=25)

        for row in range(2, 10):
            self.rowconfigure(row, minsize=28)

    def _make_cell(
        self,
        row,
        column,
        text,
        bg,
        font,
        rowspan=1,
    ):
        label = tk.Label(
            self,
            text=text,
            bg=bg,
            fg="#111111",
            font=font,
            bd=1,
            relief="solid",
            anchor="center",
        )

        label.grid(
            row=row,
            column=column,
            rowspan=rowspan,
            sticky="nsew",
        )

        return label

    def set_connected(self, station, connected):
        led = self.leds.get(station)

        if led:
            led.set_connected(connected)

    def set_status(self, station, status):
        label = self.status_labels.get(station)

        if not label:
            return

        if str(status).lower() == "testing":
            label.config(
                text="Testing",
                bg=COLOR_TESTING,
            )
        else:
            label.config(
                text="Waiting",
                bg=COLOR_WAITING,
            )

    def set_result(self, station, slot, value):
        label = self.result_labels.get((station, slot))

        if not label:
            return

        normalized = str(value).strip().lower()

        if normalized == "fail":
            label.config(
                text="Fail",
                bg=COLOR_FAIL_BG,
                font=("Arial", 12, "bold"),
            )
        elif normalized == "pass":
            label.config(
                text="Pass",
                bg=COLOR_CELL,
                font=("Arial", 12, "bold"),
            )
        else:
            label.config(
                text=str(value),
                bg=COLOR_CELL,
                font=("Arial", 11, "bold"),
            )

    def clear_station(self, station):
        for slot in range(1, 9):
            label = self.result_labels.get((station, slot))

            if label:
                label.config(
                    text="",
                    bg=COLOR_CELL,
                    font=("Arial", 10),
                )


class AudioCheckWindow:
    def __init__(self, root):
        self.root = root

        self.root.title(APP_TITLE)
        self.root.geometry("1000x590")
        self.root.minsize(920, 520)

        title = tk.Label(
            root,
            text=APP_TITLE,
            font=("Arial", 18, "bold"),
        )
        title.pack(pady=(7, 4))

        # Station 9..16 top, 1..8 bottom.
        self.top_panel = StationPanel(
            root,
            list(range(9, 17)),
        )
        self.top_panel.pack(
            fill="both",
            expand=True,
            padx=6,
            pady=(0, 0),
        )

        self.bottom_panel = StationPanel(
            root,
            list(range(1, 9)),
        )
        self.bottom_panel.pack(
            fill="both",
            expand=True,
            padx=6,
            pady=(0, 4),
        )

        self.server_label = tk.Label(
            root,
            text="TCP Server: starting...",
            font=("Arial", 9),
            anchor="w",
        )
        self.server_label.pack(
            fill="x",
            padx=8,
            pady=(2, 5),
        )

    def _panel(self, station):
        if 1 <= station <= 8:
            return self.bottom_panel

        if 9 <= station <= 16:
            return self.top_panel

        return None

    def set_connected(self, station, connected):
        panel = self._panel(station)

        if panel:
            panel.set_connected(station, connected)

    def set_status(self, station, status):
        panel = self._panel(station)

        if panel:
            panel.set_status(station, status)

    def set_result(self, station, slot, value):
        panel = self._panel(station)

        if panel:
            panel.set_result(station, slot, value)

    def clear_station(self, station):
        panel = self._panel(station)

        if panel:
            panel.clear_station(station)

    def set_server_started(self, host, port):
        self.server_label.config(
            text=f"TCP Server: Listening on port {port}"
        )

    def show_server_error(self, text):
        self.server_label.config(
            text="TCP Server ERROR",
            fg="#D32F2F",
        )

        messagebox.showerror(
            "TCP Server Error",
            text,
        )
