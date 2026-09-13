from billingsystem.cli.services.command_service import Console
from billingsystem.cli.services.screenshot_service import ScreenshotService
import argparse

parser = argparse.ArgumentParser(description="The argument parser of billing system")

def define_parser_arguments():
    parser.add_argument("--record", action="store_true", help="starts recording")
    parser.add_argument("--recordings", action="store_true", help="displays recorded recordings")

import os
import subprocess
from pathlib import Path

def open_recordings_folder(path: str):
    folder = Path(path)

    if not folder.exists():
        print(f"Folder nie istnieje: {folder}")
        return

    if os.name == "nt": 
        os.startfile(folder)
    elif os.uname().sysname == "Darwin": 
        subprocess.run(["open", folder])
    else:  # Linux
        subprocess.run(["xdg-open", folder])

def main():

    define_parser_arguments()

    args = parser.parse_args()

    if args.record:
        name = input("recording name: ")
        console = Console(recording_name=name)
        ss_service = ScreenshotService(recording_name=name, interval=10)
        ss_service.start_recording()

        while console.is_alive():
            console.prompt()

        ss_service.stop_recording()
    elif args.recordings:
        open_recordings_folder("./recordings")


if __name__ == "__main__":
      main()

    