import os
from typing import Dict, List

import paramiko
from paramiko import SSHClient
from pip._vendor import tomli  # TODO replace in 3.11

from srai_core.command_handler_base import CommandHandlerBase
from srai_core.model.docker_registry_base import DockerRegistryBase
from srai_core.model.docker_registry_ecr import DockerRegistryEcr
from srai_core.tools_env import get_string_from_env


def get_client_ssh(hostname: str, username: str, path_file_pem: str, port: int = 22) -> SSHClient:
    # Initialize SSH client
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # Automatically add the server's host key
    # Load private key
    private_key = paramiko.RSAKey(filename=path_file_pem)

    # Connect using the private key for authentication
    ssh_client.connect(hostname, port, username, pkey=private_key)
    return ssh_client


def read_toml_dict() -> Dict:
    if os.path.isfile("pyproject.toml"):
        with open("pyproject.toml", "rb") as file:
            return tomli.load(file)
    else:
        raise Exception("pyproject.toml not found")


def get_project_name() -> str:
    return read_toml_dict()["tool"]["poetry"]["name"]


def get_project_version() -> str:
    return read_toml_dict()["tool"]["poetry"]["version"]


def get_image_tag() -> str:
    toml = read_toml_dict()
    image_name = "srai/" + toml["tool"]["poetry"]["name"]
    image_version = toml["tool"]["poetry"]["version"]
    image_tag = f"{image_name}:{image_version}"
    return image_tag


# TODO all should be async
async def build_docker(command_handler: CommandHandlerBase, path=None) -> None:
    image_tag = get_image_tag()
    # stop all containers using this image
    container_name = image_tag.split(":")[0].split("/")[-1]
    stop_container(command_handler, container_name)

    # remove all containers using this image
    remove_container(command_handler, container_name)

    # remove the image
    command = f"docker rmi {image_tag}"
    command_handler.execute(command)

    # build the image
    if path is not None:
        command = f"cd {path}; docker build -t {image_tag} {path}"  # TODO add --no-cache
    else:
        command = f"docker build -t {image_tag} ."  # TODO add --no-cache
    command_handler.execute(command)


async def release_docker_local_to_aws(command_handler: CommandHandlerBase) -> None:
    image_tag = get_image_tag()
    account_id = get_string_from_env("AWS_ACCOUNT_ID")
    region_name = get_string_from_env("AWS_REGION_NAME")
    docker_registry = DockerRegistryEcr(account_id, region_name)
    repository_name = image_tag.split(":")[0]
    docker_registry.login(command_handler)
    registry_url = docker_registry.registry_url

    # check if repository exists in registry

    list_repository = docker_registry.repository_list()
    for repo in list_repository:
        print(repo)

    if not docker_registry.repository_exists(repository_name):
        docker_registry.repository_create(repository_name)

    # retag the image
    command = f"docker tag {image_tag} "
    command += f"{registry_url}/{image_tag}"
    command_handler.execute(command)

    # push the image
    command = f"docker push {registry_url}/{image_tag}"
    command_handler.execute(command)


def start_container_command(
    image_tag: str,
    container_name: str,
    dict_env: Dict[str, str],
) -> str:
    command = f"docker run -d --name {container_name}"
    for key, value in dict_env.items():
        command += f" -e {key}={value}"
    command += f" {image_tag}"
    return command


async def start_container(
    command_handler: CommandHandlerBase,
    docker_registry: DockerRegistryBase,
    image_tag: str,
    container_name: str,
    dict_env: Dict[str, str],
) -> None:
    docker_registry.login(command_handler)
    docker_registry.image_pull(command_handler, image_tag)
    command = start_container_command(image_tag, container_name, dict_env)

    if type(docker_registry) is DockerRegistryEcr:
        command = command.replace(image_tag, f"{docker_registry.registry_url}/{image_tag}")
    # Execute the command
    command_handler.execute(command)


def list_container_name(command_handler: CommandHandlerBase) -> List[str]:
    # Command to check if the Docker container is running
    command = "docker ps -a --format '{{.Names}}'"
    output, _ = command_handler.execute(command)
    return output.strip().split("\n")


def parse_table(list_header: List[str], str_table: str) -> List[Dict[str, str]]:
    list_start = []
    list_end = []
    list_dict_line = []
    list_line = str_table.split("\n")
    for header in list_header:
        list_start.append(str_table.find(header))

    for i, start in enumerate(list_start[:-1]):
        list_end.append(list_start[i + 1])
    list_end.append(-1)

    for line in list_line[1:]:
        dict_line = {}
        for header, start, end in zip(list_header, list_start, list_end):
            if end == -1:
                dict_line[header] = line[start:].strip()
            else:
                dict_line[header] = line[start:end].strip()
        list_dict_line.append(dict_line)
    return list_dict_line


def list_container_status(
    command_handler: CommandHandlerBase,
) -> List[Dict[str, str]]:
    # Command to check if the Docker container is running
    command = "docker ps -a"

    # Execute the command
    output_out, _ = command_handler.execute(command)
    list_header = [
        "CONTAINER ID",
        "IMAGE",
        "COMMAND",
        "CREATED",
        "STATUS",
        "PORTS",
        "NAMES",
    ]
    return parse_table(list_header, output_out)


def container_logs(
    command_handler: CommandHandlerBase,
    container_name: str,
    logs_count: int,
) -> List[str]:
    # Command to check if the Docker container is running
    command = f"docker logs --tail {logs_count} {container_name}"

    # Execute the command
    output_out, _ = command_handler.execute(command)
    return output_out.split("\n")


def stop_container(
    command_handler: CommandHandlerBase,
    container_name: str,
) -> None:
    # Command to stop the Docker container
    command = f"docker stop {container_name}"

    # Execute the command
    command_handler.execute(command)


def container_status(command_handler: CommandHandlerBase, container_name: str) -> str:
    # Command to check if the Docker container is running
    command = f"docker inspect --format='{{{{.State.Status}}}}' {container_name}"

    # Execute the command
    output_out, _ = command_handler.execute(command)
    return output_out.strip()


def remove_container(
    command_handler: CommandHandlerBase,
    container_name: str,
) -> None:
    # Command to stop the Docker container
    command = f"docker rm {container_name}"

    # Execute the command
    command_handler.execute(command)


def clone_repository(
    command_handler: CommandHandlerBase,
    package_name: str,
    path: str,
    git_token: str,
) -> None:
    # clear the directory
    command = f"rm -rf {path}/{package_name}"
    command_handler.execute(command)
    # clone the repository with a token

    command = f"git clone https://{git_token}@github.com/southriverai/{package_name}.git {path}/{package_name}"
    command_handler.execute(command)
