import io
import re
import sys
import threading
import time
from typing import Callable, Match, Optional


class ThreadedOutput:
    def __init__(self, target: Callable, args: tuple | None = None, kwargs: dict | None = None, logger = None):
        self.logger = logger
        args = args or ()
        kwargs = kwargs or {}

        self.target = target
        self.args = args
        self.kwargs = kwargs
        self.stdout_buffer = io.StringIO()
        self.stderr_buffer = io.StringIO()
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        self.thread = None
        self.exception = None

        self.logger.debug(f"ThreadedOutput initialized with target={target}, args={args}, kwargs={kwargs}")

    def __enter__(self):
        sys.stdout = self.stdout_buffer
        sys.stderr = self.stderr_buffer
        self.thread = threading.Thread(target=self._run_target)
        self.thread.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout = self.original_stdout
        sys.stderr = self.original_stderr
        self.thread.join()
        if self.exception:
            raise self.exception

    def _run_target(self):
        try:
            self.target(*self.args, **self.kwargs)
        except Exception as e:
            self.exception = e

    def get_output(self) -> str:
        return self.stdout_buffer.getvalue()

    def get_error(self) -> str:
        return self.stderr_buffer.getvalue()

    def check_output(self, pattern: str, timeout: float = 1.0, interval: float = 0.1) -> Optional[Match]:
        start_time = time.time()
        while time.time() - start_time < timeout:
            output = self.get_output()
            match = re.search(pattern, output)
            if match:
                return match
            time.sleep(interval)
        return None

def example_function():
    print("Starting example function")
    for i in range(5):
        print(f"Iteration {i}")
        time.sleep(0.5)
    print("Example function completed")

# Usage example
if __name__ == "__main__":
    with ThreadedOutput(example_function) as threaded_output:
        while True:
            match = threaded_output.check_output(r"Iteration (\d+)")
            if match:
                print(f"Main thread: Found iteration {match.group(1)}")

            if "completed" in threaded_output.get_output():
                print("Main thread: Function completed")
                break

    print("Final output:")
    print(threaded_output.get_output())
