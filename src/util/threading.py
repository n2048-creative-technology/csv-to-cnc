import queue
import threading
from typing import Callable, Any


class UIEventQueue:
    def __init__(self, tk_root):
        self._q: "queue.Queue[tuple[Callable[..., Any], tuple[Any, ...], dict[str, Any]]]" = queue.Queue()
        self._root = tk_root

    def post(self, fn: Callable[..., Any], *args, **kwargs) -> None:
        self._q.put((fn, args, kwargs))

    def pump(self) -> None:
        try:
            while True:
                fn, args, kwargs = self._q.get_nowait()
                try:
                    fn(*args, **kwargs)
                finally:
                    self._q.task_done()
        except queue.Empty:
            pass

    def start_auto_pump(self, interval_ms: int = 50) -> None:
        def _tick():
            self.pump()
            self._root.after(interval_ms, _tick)

        self._root.after(interval_ms, _tick)

def run_in_thread(target: Callable[[], Any]) -> threading.Thread:
    t = threading.Thread(target=target, daemon=True)
    t.start()
    return t

