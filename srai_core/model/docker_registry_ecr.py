import base64
from typing import Dict, List

from srai_core.model.docker_registry_base import DockerRegistryBase
from srai_core.tools_env import get_client_ecr


class DockerRegistryEcr(DockerRegistryBase):
    def __init__(self, account_id: str, region_name: str):
        self.client_ecr = get_client_ecr()
        registry_url = DockerRegistryEcr.get_registry_url(account_id, region_name)
        token = DockerRegistryEcr.get_ecr_login_token()
        username, password = token.split(":")
        super().__init__(registry_url, username, password)
        self.account_id = account_id
        self.region_name = region_name

    @staticmethod
    def get_ecr_login_token():
        ecr_client = get_client_ecr()
        response = ecr_client.get_authorization_token()
        token = response["authorizationData"][0]["authorizationToken"]
        return base64.b64decode(token).decode("utf-8")

    @staticmethod
    def get_registry_url(account_id, region_name) -> str:
        return f"{account_id}.dkr.ecr.{region_name}.amazonaws.com"

    def image_list(self) -> Dict[str, List[str]]:

        # Create an ECR client
        client_ecr = get_client_ecr()

        # Get a list of all repositories in your ECR
        repositories = client_ecr.describe_repositories()

        dict_list_images = {}
        for repo in repositories["repositories"]:
            repo_name = repo["repositoryName"]
            dict_list_images[repo_name] = []

            # Paginate through image details since ECR might have many images
            paginator = client_ecr.get_paginator("list_images")
            for page in paginator.paginate(repositoryName=repo_name):
                for image in page["imageIds"]:
                    image_tag = image.get("imageTag", "latest")
                    dict_list_images[repo_name].append(image_tag)
            dict_list_images[repo_name].sort()  # TODO use version compare
        return dict_list_images

    def repository_create(self, repository_name: str, is_tag_immutable: bool = True):
        if is_tag_immutable:
            image_tag_mutability = "IMMUTABLE"
        else:
            image_tag_mutability = "MUTABLE"
        self.client_ecr.create_repository(repositoryName=repository_name, imageTagMutability=image_tag_mutability)

    def repository_delete(self, repository_name: str) -> None:
        self.client_ecr.delete_repository(repositoryName=repository_name)

    def repository_exists(self, repository_name: str):
        list_repository = self.repository_list()
        for repo in list_repository:
            if repo["repositoryName"] == repository_name:
                return True
        return False

    def repository_list(self) -> List[Dict]:
        response = self.client_ecr.describe_repositories()
        list_repository = response["repositories"]
        return list_repository
