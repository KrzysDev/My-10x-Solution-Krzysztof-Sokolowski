
import os

def main():
    while True: 
        console_input: str = input(">")
        try:
            os.system(console_input)
        except Exception as e:
            print("error occured: ", e)


if __name__ == "__main__":
    main()