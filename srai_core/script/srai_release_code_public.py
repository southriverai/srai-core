import asyncio

from srai_core.command_handler_base import CommandHandlerBase
from srai_core.command_handler_subprocess import CommandHandlerSubprocess


async def srai_release_code_public(command_handler: CommandHandlerBase):
    print("Delete old distribution")
    command = "rm -rf dist"
    command_handler.execute(command)

    print("Creating distribution")
    command = "poetry build"
    command_handler.execute(command)

    print("Uploading distribution")
    command = "twine upload dist/*"
    command_handler.execute(command)


if __name__ == "__main__":
    command_handler = CommandHandlerSubprocess()
    asyncio.run(srai_release_code_public(command_handler))
