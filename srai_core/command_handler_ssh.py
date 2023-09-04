from paramiko import SSHClient
from srai_core.base_command_handler import BaseCommandHandler


class CommandHandlerSsh(BaseCommandHandler):
    def __init__(self, cliend_ssh: SSHClient) -> None:
        self.cliend_ssh = cliend_ssh

    def execute(
        ssh_client: SSHClient,
        command: str,
    ) -> None:
        # Execute the command
        print(command)
        _, stdout, stderr = ssh_client.exec_command(command)
        output = stdout.read().decode("utf-8").strip()
        print(output)
        output = stderr.read().decode("utf-8").strip()
        print(output)
