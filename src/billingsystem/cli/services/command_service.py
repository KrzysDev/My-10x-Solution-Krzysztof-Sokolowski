import json
import os
import sys
import threading
import time
from datetime import datetime


IS_WINDOWS = sys.platform.startswith("win")

if IS_WINDOWS:
    from winpty import PtyProcess
else:
    from ptyprocess import PtyProcessUnicode as PtyProcess


class Console:
    STOP_COMMAND = "stop recording"
    LOG_FILENAME = "recording.json"

    def __init__(self, recording_name = "recording1", autostart=True):
        self.shell = None
        self.newline = "\n"
        self._reader_thread = None
        self._stopped = False

        self.recorded_logs_path = f"./recordings/{recording_name}/logs"
        self.entered_commands = []
        os.makedirs(self.recorded_logs_path, exist_ok=True)

        if autostart:
            self.start()

    def start(self):
        self.shell, self.newline = self._spawn_shell()
        self._stopped = False
        self._drain_initial_output()

        self._reader_thread = threading.Thread(
            target=self._read_output,
            daemon=True,
        )
        self._reader_thread.start()

    def stop(self):
        if self._stopped:
            return
        self._stopped = True

        if self.shell is not None and self.shell.isalive():
            try:
                self.shell.write("exit" + self.newline)
            except EOFError:
                pass

    def is_alive(self):
        if self._stopped:
            return False
        return self.shell is not None and self.shell.isalive()

    def prompt(self, text=""):
        if not self.is_alive():
            return None

        try:
            command = input(text)
        except EOFError:
            self.stop()
            return None
        except KeyboardInterrupt:
            try:
                self.shell.write("\x03")
            except EOFError:
                self.stop()
            return ""

        if command == self.STOP_COMMAND:
            self.stop()
            return None

        self._log_command(command)

        try:
            self.shell.write(command + self.newline)
        except EOFError:
            self.stop()
            return None

        return command

    def _log_command(self, command):
        self.entered_commands.append({
            "command": command,
            "timestamp": datetime.now().isoformat(),
        })

        log_path = os.path.join(self.recorded_logs_path, self.LOG_FILENAME)
        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(self.entered_commands, f, ensure_ascii=False, indent=2)

    def _spawn_shell(self):
        if IS_WINDOWS:
            shell = PtyProcess.spawn("cmd.exe")
            shell.write("prompt $E[93m(recording)$E[0m $P$G\r\n")
            shell.write("cls\r\n")
            newline = "\r\n"
        else:
            user_shell = os.environ.get("SHELL", "/bin/bash")
            shell = PtyProcess.spawn([user_shell])
            shell.write(
                'export PS1="\\[\\033[93m\\](recording)\\[\\033[0m\\] \\w $ "\n'
            )
            shell.write("clear\n")
            newline = "\n"

        return shell, newline

    def _drain_initial_output(self, timeout=1.0):
        end_time = time.time() + timeout
        while time.time() < end_time:
            try:
                self.shell.read(4096)
            except EOFError:
                break

    def _read_output(self):
        while self.shell.isalive():
            try:
                output = self.shell.read(4096)
                if output:
                    print(output, end="", flush=True)
            except EOFError:
                break


if __name__ == "__main__":
    console = Console()
    while console.is_alive():
        console.prompt()