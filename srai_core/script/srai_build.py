import asyncio
import json
import sys

from srai_core.command_handler_base import CommandHandlerBase
from srai_core.tools_docker import build_docker
from srai_core.tools_env import get_deployment


async def srai_build(deployment: dict) -> None:
    for build_target in deployment["list_build_target"]:
        if "build_target_type" not in build_target:
            print("`build_target_type` type not found")
            print(json.dumps(build_target, indent=4))
            sys.exit(1)

        if build_target["build_target_type"] == "build_docker":
            await build_docker(CommandHandlerBase.from_dict(build_target["command_handler"]))
        else:
            print(f"Unknown build target type: {build_target['type']}")
            sys.exit(1)


def main():
    asyncio.run(srai_build(get_deployment()))


if __name__ == "__main__":
    main()
