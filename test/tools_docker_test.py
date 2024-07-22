from srai_core.command_handler_subprocess import CommandHandlerSubprocess
from srai_core.model.docker_registry_ecr import DockerRegistryEcr
from srai_core.tools_env import get_string_from_env


def test_repository_list():
    account_id = get_string_from_env("AWS_ACCOUNT_ID")
    region_name = get_string_from_env("AWS_REGION_NAME")
    docker_registry = DockerRegistryEcr(account_id, region_name)
    for repository in docker_registry.repository_list():
        print(repository["repositoryName"])


def test_image_list():
    account_id = get_string_from_env("AWS_ACCOUNT_ID")
    region_name = get_string_from_env("AWS_REGION_NAME")
    docker_registry = DockerRegistryEcr(account_id, region_name)
    for respository_name, list_image_version in docker_registry.image_list().items():
        for image_version in list_image_version:
            image_tag = f"{respository_name}:{image_version}"
            print(image_tag)


def test_login():
    command_handler = CommandHandlerSubprocess()
    account_id = get_string_from_env("AWS_ACCOUNT_ID")
    region_name = get_string_from_env("AWS_REGION_NAME")
    docker_registry = DockerRegistryEcr(account_id, region_name)
    docker_registry.login(command_handler)


if __name__ == "__main__":
    # test_repository_list()
    # test_image_list()
    test_login()
