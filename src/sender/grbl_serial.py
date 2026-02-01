from __future__ import annotations

import time
from typing import List

import serial  # type: ignore

from .base import Sender, ProgressCb


class GrblSerialSender(Sender):
    def __init__(self, log_out, log_in, log_info, port: str, baud: int):
        super().__init__(log_out, log_in, log_info)
        self.port = port
        self.baud = baud
        self.ser: serial.Serial | None = None

    def connect(self) -> None:
        self.log_info(f"Connecting {self.port} @ {self.baud}\n")
        self.ser = serial.Serial(self.port, self.baud, timeout=1)
        time.sleep(2.0)  # allow GRBL reset
        self._flush()
        self._write("$G")  # status report to wake

    def disconnect(self) -> None:
        if self.ser:
            self.log_info("Disconnecting\n")
            try:
                self.ser.close()
            finally:
                self.ser = None

    def _write(self, line: str) -> None:
        assert self.ser is not None
        data = (line.strip() + "\n").encode("ascii")
        self.log_out(line + "\n")
        self.ser.write(data)

    def _readline(self) -> str:
        assert self.ser is not None
        raw = self.ser.readline()
        try:
            s = raw.decode("ascii", errors="ignore").strip()
        except Exception:
            s = ""
        if s:
            self.log_in(s + "\n")
        return s

    def _flush(self) -> None:
        assert self.ser is not None
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()

    def stream(self, lines: List[str], on_progress: ProgressCb) -> None:
        if not self.ser:
            raise RuntimeError("Serial not connected")
        total = len(lines)
        sent = 0
        for line in lines:
            self._write(line)
            # read until ok or error
            while True:
                resp = self._readline()
                if not resp:
                    continue
                if resp.lower().startswith("ok"):
                    break
                if resp.lower().startswith("error"):
                    raise RuntimeError(resp)
            sent += 1
            on_progress(sent, total)

    def wait_for_idle(self, timeout_s: float = 5.0) -> None:
        assert self.ser is not None
        self.log_info("Waiting for Idle\n")
        deadline = time.time() + timeout_s
        while time.time() < deadline:
            self._write("?")
            # read one line with short timeout
            start = time.time()
            while time.time() - start < 0.5:
                resp = self._readline()
                if "<Idle" in resp:
                    return
            time.sleep(0.1)
        raise TimeoutError("Controller did not become Idle in time")

