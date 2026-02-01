from __future__ import annotations

import random
import time
from typing import List

from .base import Sender, ProgressCb


class SimulatorSender(Sender):
    def __init__(self, log_out, log_in, log_info, per_line_delay_ms: int = 20, random_extra_delay_ms: int = 0, error_after_n_lines: int = 0):
        super().__init__(log_out, log_in, log_info)
        self.delay = per_line_delay_ms
        self.rand_delay = random_extra_delay_ms
        self.error_after = error_after_n_lines
        self._connected = False
        self._sent = 0

    def connect(self) -> None:
        self._connected = True
        self._sent = 0
        self.log_info("Simulation connected\n")

    def disconnect(self) -> None:
        if self._connected:
            self.log_info("Simulation disconnected\n")
        self._connected = False

    def stream(self, lines: List[str], on_progress: ProgressCb) -> None:
        if not self._connected:
            raise RuntimeError("Simulator not connected")
        total = len(lines)
        for i, line in enumerate(lines, start=1):
            self.log_out(line + "\n")
            d = self.delay / 1000.0
            if self.rand_delay:
                d += random.uniform(0, self.rand_delay / 1000.0)
            time.sleep(d)
            self._sent += 1
            if self.error_after and self._sent == self.error_after:
                self.log_in("error:1\n")
                raise RuntimeError("Simulated error after N lines")
            if i % 10 == 0:
                self.log_in("<Run|MPos:0,0,0|FS:100,100>\n")
            self.log_in("ok\n")
            on_progress(i, total)

    def wait_for_idle(self, timeout_s: float = 5.0) -> None:
        # Simulate a brief delay and then report Idle
        time.sleep(min(0.5, timeout_s))
        self.log_in("<Idle|MPos:0,0,0|FS:0,0>\n")

