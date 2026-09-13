from billingsystem.cli.services.command_service import Console

def main():
    name = input("recording name: ")

    console = Console(recording_name=name)

    while console.is_alive():
            console.prompt()

if __name__ == "__main__":
      main()

    