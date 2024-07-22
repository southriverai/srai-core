from srai_core.command_handler_base import CommandHandlerBase


class DockerRegistryBase:

    def __init__(self, registry_url: str, username: str, password: str):
        self.registry_url = registry_url
        self.username = username
        self.password = password

    def get_registry_url(self):
        return self.registry_url

    def get_username(self):
        return self.username

    def get_password(self):
        return self.password

    def get_command_login(self) -> str:
        return f"docker login --username {self.username} --password {self.password} {self.registry_url}"

    def login(self, command_handler: CommandHandlerBase) -> None:
        command = self.get_command_login()
        command_handler.execute(command)

    def image_pull(self, command_handler: CommandHandlerBase, image_tag: str) -> None:
        command = f"docker pull {self.registry_url}/{image_tag}"
        command_handler.execute(command)
