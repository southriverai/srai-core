#
import os
import subprocess


def main():
    print("Delete old distribution")
    subprocess.run("rm -rf dist", shell=True, check=True)

    print("Creating distribution")
    username = os.environ.get("PYPI_USERNAME")
    password = os.environ.get("PYPI_PASSWORD")

    subprocess.run("python setup.py sdist", shell=True, check=True)

    command = "twine upload dist/*"
    print(f"Running command: {command}")
    subprocess.run(command, shell=True, check=True)


if __name__ == "__main__":
    main()
