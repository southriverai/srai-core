import asyncio
import json
import os
import sys

from srai_core.command_handler_base import CommandHandlerBase
from srai_core.command_handler_subprocess import CommandHandlerSubprocess
from srai_core.script.release_code_public import release_code_public_async
from srai_core.tools_docker import build_docker, release_docker_local_to_aws_async


async def srai_release():
    # check for docker file:

    if len(sys.argv) < 2:
        if os.path.isfile("deployment.json"):
            print("using default deployment_file.json")
            path_file_deployment = "deployment.json"
        else:
            command_handler = CommandHandlerSubprocess()
            if os.path.isfile("dockerfile"):
                print("Doing default release: build_docker")
                await build_docker(command_handler)
            else:
                print("Doing default release: release_code_public")
                await release_code_public_async(command_handler)
            sys.exit(0)

    else:
        path_file_deployment = sys.argv[1]

    with open(path_file_deployment) as f:
        deployment = json.load(f)

    for build_target in deployment["list_build_target"]:
        print(build_target)
        command_handler = CommandHandlerBase.from_dict(build_target["command_handler"])
        await build_docker(command_handler)

    for release_target in deployment["list_release_target"]:
        command_handler = CommandHandlerBase.from_dict(release_target["command_handler"])
        release_target_type = release_target["release_target_type"]
        if release_target_type == "release_code_public":
            await release_code_public_async(command_handler)
        elif release_target_type == "release_docker_local_to_aws":
            await release_docker_local_to_aws_async(command_handler)
        else:
            print(f"Unknown release_type: {release_target_type}")
            sys.exit(1)


def main():
    asyncio.run(srai_release())


if __name__ == "__main__":
    main()
