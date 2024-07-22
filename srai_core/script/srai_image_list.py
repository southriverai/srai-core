from srai_core.model.docker_registry_ecr import DockerRegistryEcr
from srai_core.tools_env import get_string_from_env


def main():
    repository = DockerRegistryEcr(get_string_from_env("AWS_ACCOUNT_ID"), get_string_from_env("AWS_REGION_NAME"))

    dict_list_images = repository.image_list()
    for repo_name, list_images in dict_list_images.items():
        print(f"Images in repository: {repo_name}")
        for image_tag in list_images:
            print(f"{repo_name}:{image_tag}")


if __name__ == "__main__":
    main()
