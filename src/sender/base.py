from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable, List


ProgressCb = Callable[[int, int], None]
LogCb = Callable[[str], None]


class Sender(ABC):
    def __init__(self, log_out: LogCb, log_in: LogCb, log_info: LogCb):
        self.log_out = log_out
        self.log_in = log_in
        self.log_info = log_info

    @abstractmethod
    def connect(self, *args, **kwargs) -> None:
        ...

    @abstractmethod
    def disconnect(self) -> None:
        ...

    @abstractmethod
    def stream(self, lines: List[str], on_progress: ProgressCb) -> None:
        ...

    @abstractmethod
    def wait_for_idle(self, timeout_s: float = 5.0) -> None:
        ...

