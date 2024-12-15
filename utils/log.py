import inspect
import logging
import traceback

app_log = logging.getLogger("main_logger")
app_log.setLevel(logging.INFO)

handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(levelname)s:     %(message)s"))

app_log.addHandler(handler)

class LogWrapper:
    def info(self, *args: list) -> None: app_log.info("\n".join(map(str,args)))
    def warn(self, *args: list) -> None:
        frame = inspect.currentframe()
        stack_trace = traceback.extract_stack(frame)
        stack = None
        for depth in range(len(stack_trace) - 2, 0, -1):
            filepath = stack_trace[depth].filename[7:]
            function = stack_trace[depth].name
            if not stack_trace[depth].filename.startswith("/app"):
                app_log.warn(stack)
                break
            stack = f"{stack} -> f{filepath}:f{function}()" if stack is not None else f"{filepath}:{function}()"
        app_log.warn("\n".join(map(str,args)))
    def error(self, *args: list) -> None: app_log.error("\n".join(map(str,args)))
    def debug(self, *args: list) -> None: app_log.debug("\n".join(map(str,args)))

Logger = LogWrapper()

