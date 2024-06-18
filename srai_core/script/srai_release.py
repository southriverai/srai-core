import asyncio
import json
import os
import sys

from srai_core.command_handler_base import CommandHandlerBase
from srai_core.script.release_code_public import release_code_public_async
from srai_core.tools_docker import build_docker_async, release_docker_local_to_aws_async


async def srai_release():
    # check for docker file:

    if len(sys.argv) < 2:
        if os.path.isfile("deployment_file.json"):
            print("using default deployment_file.json")
            path_deployment_file = "deployment_file.json"
        else:
            print("Usage: srai_release deployment_file.json")
            sys.exit(1)
    else:
        path_deployment_file = sys.argv[1]
    with open(path_deployment_file) as f:
        deployment = json.load(f)
    for build_target in deployment["list_build_target"]:
        print(build_target)
        command_handler = CommandHandlerBase.from_dict(build_target)
        await build_docker_async(command_handler)

    for release_target in deployment["list_release_target"]:
        command_handler = CommandHandlerBase.from_dict(release_target)
        release_type = release_target["release_type"]
        if release_type == "release_code_public":
            await release_code_public_async(command_handler)
        elif release_type == "release_docker_local_to_aws":
            await release_docker_local_to_aws_async(command_handler)
        else:
            print(f"Unknown release_type: {release_type}")
            sys.exit(1)


def main():
    asyncio.run(srai_release())


if __name__ == "__main__":
    main()
