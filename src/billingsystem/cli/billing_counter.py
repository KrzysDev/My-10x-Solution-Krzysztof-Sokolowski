from winpty import PtyProcess
import threading
import time


def read_output(shell):
    while shell.isalive():
        try:
            output = shell.read(4096)

            if output:
                print(output, end="", flush=True)

        except EOFError:
            break


def drain_initial_output(shell, timeout=1.0):
    end_time = time.time() + timeout
    while time.time() < end_time:
        try:
            shell.read(4096)
        except EOFError:
            break


def main():
    shell = PtyProcess.spawn("cmd.exe")

    shell.write("prompt $E[93m(recording)$E[0m $P$G\r\n")
    shell.write("cls\r\n")

    drain_initial_output(shell)

    thread = threading.Thread(
        target=read_output,
        args=(shell,),
        daemon=True,
    )
    thread.start()

    while shell.isalive():
        try:
            command = input()

            if command == "stop recording":
                shell.write("exit\r\n")
                break

            shell.write(command + "\r\n")

        except KeyboardInterrupt:
            shell.write("\x03")
        except EOFError:
            shell.write("exit\r\n")
            break


if __name__ == "__main__":
    main()