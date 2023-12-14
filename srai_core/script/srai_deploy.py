import asyncio
import json
import sys

from srai_core.command_handler_base import CommandHandlerBase
from srai_core.tools_docker import (
    build_docker_async,
    get_image_tag,
    release_docker_local_to_aws_async,
    remove_container,
    start_container_async,
    stop_container,
)


async def srai_deploy():
    if len(sys.argv) < 2:
        print("Usage: deploy_docker deployment_file.json")
        sys.exit(1)

    path_deployment_file = sys.argv[1]
    with open(path_deployment_file) as f:
        deployment = json.load(f)
    for build_target in deployment["list_build_target"]:
        command_handler = CommandHandlerBase.from_dict(build_target)
        await build_docker_async(command_handler)

    for release_target in deployment["list_release_target"]:
        command_handler = CommandHandlerBase.from_dict(release_target)
        release_type = release_target["release_type"]
        if release_type == "release_docker_local_to_aws":
            await release_docker_local_to_aws_async(command_handler)
        else:
            print(f"Unknown release_type: {release_type}")
            sys.exit(1)

    for deploy_target in deployment["list_deploy_target"]:
        command_handler = CommandHandlerBase.from_dict(deploy_target)
        image_tag = get_image_tag()
        dict_env = deploy_target["environment_dict"]
        if "account_id" in deploy_target:
            account_id = deploy_target["account_id"]
        else:
            account_id = None
        if "region_name" in deploy_target:
            region_name = deploy_target["region_name"]
        else:
            region_name = None

        dict_env["IMAGE_TAG"] = image_tag

        container_name = image_tag.split(":")[0].split("/")[-1]
        stop_container(command_handler, container_name)
        remove_container(command_handler, container_name)
        await start_container_async(command_handler, account_id, region_name, image_tag, container_name, dict_env)


def main():
    asyncio.run(srai_deploy())


if __name__ == "__main__":
    main()
