import asyncio
import base64
from typing import Dict, List

import paramiko
from paramiko import SSHClient

from srai_core.command_handler_base import CommandHandlerBase
from srai_core.tools_env import get_client_ecr, get_string_from_env


def list_ecr_images() -> Dict[str, List[str]]:
    client_ecr = get_client_ecr()
    account_id = "169192938140"
    region_name = "eu-west-1"
    url = get_registry_url(account_id, region_name)
    print(url)
    # Create an ECR client

    # Get a list of all repositories in your ECR
    repositories = client_ecr.describe_repositories()

    dict_list_images = {}
    for repo in repositories["repositories"]:
        repo_name = repo["repositoryName"]
        print(f"Images in repository: {repo_name}")
        dict_list_images[repo_name] = []

        # Paginate through image details since ECR might have many images
        paginator = client_ecr.get_paginator("list_images")
        for page in paginator.paginate(repositoryName=repo_name):
            for image in page["imageIds"]:
                image_tag = image.get("imageTag", "latest")
                dict_list_images[repo_name].append(image_tag)

    return dict_list_images


def read_setup_cfg() -> dict:
    path_file_setup_cfg = "setup.cfg"
    dict_setup_cfg = {}
    with open(path_file_setup_cfg, "r") as file_setup_cfg:
        list_line = file_setup_cfg.readlines()
        for line in list_line:
            if "=" not in line:
                continue
            key = line.split("=")[0]
            value = line.split("=")[1]
            key = key.strip()
            value = value.strip()
            value = value.replace('"', "")
            dict_setup_cfg[key] = value
    return dict_setup_cfg


def read_module_init() -> dict:
    dict_setup_cfg = read_setup_cfg()
    module_name = dict_setup_cfg["module-name"]
    path_file_module_init = f"{module_name}/__init__.py"
    dict_module_init = {}
    with open(path_file_module_init, "r") as file_module_init:
        list_line = file_module_init.readlines()
        for line in list_line:
            key = line.split("=")[0]
            value = line.split("=")[1]
            key = key.strip()
            value = value.strip()
            value = value.replace('"', "")
            dict_module_init[key] = value
    return dict_module_init


def get_client_ssh(hostname: str, username: str, path_file_pem: str, port: int = 22) -> SSHClient:
    # Initialize SSH client
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # Automatically add the server's host key
    # Load private key
    private_key = paramiko.RSAKey(filename=path_file_pem)

    # Connect using the private key for authentication
    ssh_client.connect(hostname, port, username, pkey=private_key)
    return ssh_client


def get_image_tag() -> str:
    dict_module_init = read_module_init()
    image_name = "srai/" + dict_module_init["__title__"]
    image_version = dict_module_init["__version__"]
    image_tag = f"{image_name}:{image_version}"
    return image_tag


def get_registry_url(account_id, region_name) -> str:
    return f"{account_id}.dkr.ecr.{region_name}.amazonaws.com"


# TODO all should be async
async def build_docker_async(command_handler: CommandHandlerBase, path=None) -> None:
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


def build_docker(command_handler: CommandHandlerBase, path=None) -> None:
    return asyncio.run(build_docker_async(command_handler, path))


def get_ecr_login_token():
    ecr_client = get_client_ecr()
    response = ecr_client.get_authorization_token()
    token = response["authorizationData"][0]["authorizationToken"]
    return base64.b64decode(token).decode("utf-8")


def login_docker_to_ecr(command_handler: CommandHandlerBase, account_id: str, region_name: str) -> None:
    token = get_ecr_login_token()
    username, password = token.split(":")
    registry_url = get_registry_url(account_id, region_name)
    command = f"docker login --username {username} --password {password} {registry_url}"
    command_handler.execute(command)


def list_ecr_repository():
    ecr_client = get_client_ecr()
    response = ecr_client.describe_repositories()
    list_repository = response["repositories"]
    return list_repository


def create_ecr_repository():
    ecr_client = get_client_ecr()
    dict_module_init = read_module_init()
    image_name = "srai/" + dict_module_init["__title__"]
    ecr_client.create_repository(repositoryName=image_name)


async def release_docker_local_to_aws_async(command_handler: CommandHandlerBase) -> None:
    image_tag = get_image_tag()
    account_id = get_string_from_env("AWS_ACCOUNT_ID")
    region_name = get_string_from_env("AWS_REGION_NAME")

    login_docker_to_ecr(command_handler, account_id, region_name)
    registry_url = get_registry_url(account_id, region_name)

    command = f"docker tag {image_tag} "
    command += f"{registry_url}/{image_tag}"
    command_handler.execute(command)

    command = f"docker push {registry_url}/{image_tag}"
    command_handler.execute(command)


def release_docker_aws_local(command_handler: CommandHandlerBase) -> None:
    return asyncio.run(release_docker_local_to_aws_async(command_handler))


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


def pull_image_command(account_id, region_name):
    image_tag = get_image_tag()
    registry_url = get_registry_url(account_id, region_name)
    command = f"docker pull {registry_url}/{image_tag}"
    return command


def start_container(
    command_handler: CommandHandlerBase,
    account_id: str,
    region_name: str,
    image_tag: str,
    container_name: str,
    dict_env: Dict[str, str],
) -> None:
    return asyncio.run(
        start_container_async(command_handler, account_id, region_name, image_tag, container_name, dict_env)
    )


async def start_container_async(
    command_handler: CommandHandlerBase,
    account_id: str,  # TODO remove
    region_name: str,  # TODO remove
    image_tag: str,
    container_name: str,
    dict_env: Dict[str, str],
) -> None:
    command = login_docker_to_ecr(command_handler, account_id, region_name)
    if account_id is not None and region_name is not None:
        command = pull_image_command(account_id, region_name)
        # Execute the command
        command_handler.execute(command)

        registry_url = get_registry_url(account_id, region_name)
    command = start_container_command(image_tag, container_name, dict_env)
    if account_id is not None and region_name is not None:
        command = command.replace(image_tag, f"{registry_url}/{image_tag}")
    # Execute the command
    command_handler.execute(command)


def list_container_name(ssh_client: SSHClient) -> List[str]:
    # Command to check if the Docker container is running
    command = "docker ps -a --format '{{.Names}}'"

    # Execute the command
    _, stdout, _ = ssh_client.exec_command(command)
    output = stdout.read().decode("utf-8").strip()
    return output.split("\n")


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
) -> dict:
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


def exec_ssh(
    ssh_client: SSHClient,
    command: str,
) -> None:
    # Execute the command
    print(command)
    _, stdout, stderr = ssh_client.exec_command(command)
    output = stdout.read().decode("utf-8").strip()
    print(output)
    output = stderr.read().decode("utf-8").strip()
    print(output)
