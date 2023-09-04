from srai_core.tools_env import get_client_ecr


class EcrHelper:
    def __init__(self) -> None:
        self.ecr_client = get_client_ecr()

    def list_ecr_images(self):
        # Create an ECR client

        # Get a list of all repositories in your ECR
        repositories = self.ecr_client.describe_repositories()

        for repo in repositories["repositories"]:
            repo_name = repo["repositoryName"]
            print(f"Images in repository: {repo_name}")

            # Paginate through image details since ECR might have many images
            paginator = self.ecr_client.get_paginator("list_images")
            for page in paginator.paginate(repositoryName=repo_name):
                for image in page["imageIds"]:
                    print(
                        f"  Image: {image.get('imageTag', 'latest')} (Digest: {image['imageDigest']})"
                    )


def main():
    ecr_helper = EcrHelper()
    ecr_helper.list_ecr_images()


if __name__ == "__main__":
    main()
