import subprocess
from srai_core.base_command_handler import BaseCommandHandler


class CommandHandlerSubprocess(BaseCommandHandler):
    def __init__(self):
        pass

    def execute(self, command: str) -> None:
        # Execute the command
        print(command)
        subprocess.run(command, shell=True)
