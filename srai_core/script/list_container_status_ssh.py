import os

from srai_core.command_handler_ssh import CommandHandlerSsh
from srai_core.tools_docker import get_client_ssh, list_container_status


def main():
    hostname = "18.185.177.93"  # TODO these could even come from boto3
    username = "ubuntu"
    path_file_pem = "c:/key/lightsaildefaultkey-eu-central-1.pem"
    if not os.path.exists(path_file_pem):
        raise Exception(f"File {path_file_pem} does not exist")

    ssh_client = get_client_ssh(hostname, username, path_file_pem)
    command_handler = CommandHandlerSsh(ssh_client)
    container_statuss = list_container_status(command_handler)
    for container_status in container_statuss:
        print(container_status["NAMES"])
        print("--" + container_status["IMAGE"])
        print("--" + container_status["STATUS"])


if __name__ == "__main__":
    main()
