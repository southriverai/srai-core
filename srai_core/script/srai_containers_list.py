import asyncio

from srai_core.command_handler_base import CommandHandlerBase
from srai_core.command_handler_subprocess import CommandHandlerSubprocess
from srai_core.tools_docker import list_container_name


async def srai_container_list(command_handler: CommandHandlerBase):
    # hostname = "18.185.177.93"  # TODO these could even come from boto3
    # username = "ubuntu"
    # path_file_pem = "c:/key/lightsaildefaultkey-eu-central-1.pem"
    # if not os.path.exists(path_file_pem):
    #     raise Exception(f"File {path_file_pem} does not exist")

    # ssh_client = get_client_ssh(hostname, username, path_file_pem)
    list_container_name_running = list_container_name(command_handler)
    for container_name_running in list_container_name_running:
        print(container_name_running)


if __name__ == "__main__":
    command_handler = CommandHandlerSubprocess()
    asyncio.run(srai_container_list(command_handler))
