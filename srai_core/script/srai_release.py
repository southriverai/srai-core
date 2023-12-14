import asyncio
import json
import sys

from srai_core import command_handler_base
from srai_core.command_handler_base import CommandHandlerBase
from srai_core.tools_docker import build_docker_async, release_docker_local_to_aws_async


async def srai_release():
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


def main():
    asyncio.run(srai_release())


if __name__ == "__main__":
    main()
