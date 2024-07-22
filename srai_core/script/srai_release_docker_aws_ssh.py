import asyncio
import os

from srai_core.command_handler_ssh import CommandHandlerSsh
from srai_core.tools_docker import (
    build_docker,
    clone_repository,
    get_client_ssh,
    get_project_name,
    release_docker_local_to_aws,
)
from srai_core.tools_env import get_string_from_env


async def srai_release_docker_aws_ssh():
    hostname = get_string_from_env("AWS_CNC_HOSTNAME")  # TODO these could even come from boto3
    git_token = get_string_from_env("GITHUB_TOKEN")
    username = "ubuntu"
    path_file_pem = "c:/key/lightsaildefaultkey-eu-central-1.pem"
    if not os.path.exists(path_file_pem):
        raise Exception(f"File {path_file_pem} does not exist")

    ssh_client = get_client_ssh(hostname, username, path_file_pem)
    repository_name = get_project_name()
    command_handler = CommandHandlerSsh(ssh_client)

    clone_repository(command_handler, repository_name, "~", git_token)  # TODO
    path_target = f"~/{repository_name}"

    await build_docker(command_handler, path_target)
    await release_docker_local_to_aws(command_handler)


if __name__ == "__main__":
    asyncio.run(srai_release_docker_aws_ssh())
