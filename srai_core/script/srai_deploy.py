import asyncio
import json
import sys

from srai_core.command_handler_base import CommandHandlerBase
from srai_core.model.docker_registry_base import DockerRegistryBase
from srai_core.model.docker_registry_ecr import DockerRegistryEcr
from srai_core.script.srai_release import srai_release
from srai_core.tools_docker import get_image_tag, remove_container, start_container, stop_container
from srai_core.tools_env import get_deployment, get_string_from_env


async def srai_deploy(deployment: dict):
    await srai_release(deployment)
    for deploy_target in deployment["list_deploy_target"]:
        command_handler = CommandHandlerBase.from_dict(deploy_target["command_handler"])
        deploy_target_type = deploy_target["deploy_target_type"]
        if deploy_target_type == "deploy_docker":
            image_tag = get_image_tag()
            dict_env = deploy_target["environment_dict"]
            if "port_dict" in deploy_target:
                dict_port = deploy_target["port_dict"]
            else:
                dict_port = {}
            dict_env["IMAGE_TAG"] = image_tag

            container_name = image_tag.split(":")[0].split("/")[-1]
            registry = DockerRegistryBase("", "kozzion", "wrc0ceq5xjk-ext!PET")
            stop_container(command_handler, container_name)
            remove_container(command_handler, container_name)

            await start_container(
                command_handler,
                registry,
                image_tag,
                container_name,
                dict_env,
                dict_port,
            )
        elif deploy_target_type == "deploy_docker_aws":
            image_tag = get_image_tag()
            dict_env = deploy_target["environment_dict"]
            if "port_dict" in deploy_target:
                dict_port = deploy_target["port_dict"]
            else:
                dict_port = {}
            account_id = get_string_from_env("AWS_ACCOUNT_ID")  # TODO this is a mess
            region_name = get_string_from_env("AWS_REGION_NAME")  # TODO this is a mess
            registry = DockerRegistryEcr(account_id, region_name)
            dict_env["IMAGE_TAG"] = image_tag

            container_name = image_tag.split(":")[0].split("/")[-1]
            stop_container(command_handler, container_name)
            remove_container(command_handler, container_name)
            await start_container(command_handler, registry, image_tag, container_name, dict_env, dict_port)
        else:
            print(f"Unknown `deploy_target_type`: {deploy_target_type}")
            sys.exit(1)


def main():

    asyncio.run(srai_deploy(get_deployment()))


if __name__ == "__main__":
    main()
