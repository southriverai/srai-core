import asyncio
import sys

from srai_core.command_handler_base import CommandHandlerBase
from srai_core.script.srai_build import srai_build
from srai_core.script.srai_release_code_public import srai_release_code_public
from srai_core.tools_docker import build_docker, release_docker_local_to_aws
from srai_core.tools_env import get_deployment


async def srai_release(deployment: dict) -> None:
    await srai_build(deployment)

    for release_target in deployment["list_release_target"]:
        command_handler = CommandHandlerBase.from_dict(release_target["command_handler"])
        release_target_type = release_target["release_target_type"]
        if release_target_type == "release_code_public":
            await srai_release_code_public(command_handler)
        elif release_target_type == "release_docker_local_to_aws":
            await release_docker_local_to_aws(command_handler)
        else:
            print(f"Unknown release_type: {release_target_type}")
            sys.exit(1)


def main():
    asyncio.run(srai_release(get_deployment()))


if __name__ == "__main__":
    main()
