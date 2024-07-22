import asyncio
import json
import sys

from srai_core.command_handler_base import CommandHandlerBase
from srai_core.tools_docker import get_image_tag, list_container_name, remove_container, stop_container


async def srai_docker_stop(deployment: dict):
    for deploy_target in deployment["list_deploy_target"]:
        command_handler = CommandHandlerBase.from_dict(deploy_target["command_handler"])

        image_tag = get_image_tag()

        container_name = image_tag.split(":")[0].split("/")[-1]

        list_container_name_present = list_container_name(command_handler)
        if container_name in list_container_name_present:
            stop_container(command_handler, container_name)
            remove_container(command_handler, container_name)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: srai_docker_stop deployment_file.json")
        sys.exit(1)

    path_deployment_file = sys.argv[1]
    with open(path_deployment_file) as f:
        deployment = json.load(f)
    asyncio.run(srai_docker_stop(deployment))
