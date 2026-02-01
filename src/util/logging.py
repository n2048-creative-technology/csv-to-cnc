import threading
from typing import Callable


class LogEmitter:
    def __init__(self, callback: Callable[[str], None]):
        self._cb = callback
        self._lock = threading.Lock()

    def emit(self, text: str) -> None:
        with self._lock:
            self._cb(text)

    def info(self, text: str) -> None:
        self.emit(text)

    def out(self, line: str) -> None:
        self.emit(f">> {line.rstrip()}\n")

    def inc(self, line: str) -> None:
        self.emit(f"<< {line.rstrip()}\n")

