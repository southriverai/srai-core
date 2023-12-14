import asyncio
import json
import sys

from srai_core.command_handler_base import CommandHandlerBase
from srai_core.tools_docker import build_docker_async


async def srai_build() -> None:
    if len(sys.argv) < 2:
        print("Usage: deploy_docker deployment_file.json")
        sys.exit(1)

    path_deployment_file = sys.argv[1]
    with open(path_deployment_file) as f:
        deployment = json.load(f)

    for build_target in deployment["list_build_target"]:
        await build_docker_async(CommandHandlerBase.from_dict(build_target))


def main():
    asyncio.run(srai_build())


if __name__ == "__main__":
    main()
