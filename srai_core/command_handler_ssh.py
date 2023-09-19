from typing import Tuple
from paramiko import SSHClient
from srai_core.base_command_handler import BaseCommandHandler


class CommandHandlerSsh(BaseCommandHandler):
    def __init__(self, cliend_ssh: SSHClient) -> Tuple[str, str]:
        self.cliend_ssh = cliend_ssh

    def execute(
        self,
        command: str,
    ) -> None:
        # Execute the command
        print(command)
        _, stdout, stderr = self.cliend_ssh.exec_command(command)
        output_out = stdout.read().decode("utf-8").strip()
        print(output_out)
        output_err = stderr.read().decode("utf-8").strip()
        print(output_err)
        return output_out, output_err
