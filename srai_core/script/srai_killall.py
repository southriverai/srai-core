import os
import subprocess


def srai_killall():
    if os.name == "nt":
        # windows
        subprocess.run("taskkill /F /IM python.exe", shell=True)
    else:
        # linux
        subprocess.run("killall python", shell=True)


def main():
    srai_killall()


if __name__ == "__main__":
    main()
