import os
import re

from setuptools import find_packages, setup


def get_version(project_name: str):
    project_path = project_name.replace("-", "_")
    version_file = os.path.join(os.path.dirname(__file__), project_path, "__init__.py")
    with open(version_file, "r") as f:
        content = f.read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", content, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


with open("README.md", "r") as f:
    long_description = f.read()

with open("requirements.txt", "r") as f:
    requirements = f.read().splitlines()


project_url = "https://github.com/southriverai/"
project_name = "srai-core"

setup(
    name=project_name,
    packages=find_packages(),
    version=get_version(project_name),
    license="MIT",
    package_data={},
    python_requires=">=3.5",
    install_requires=requirements,
    author="Jaap Oosterbroek",
    author_email="jaap.oosterbroek@southriverai.com",
    description="A library core functions used in other SRAI libraries.",
    entry_points={
        "console_scripts": [
            "srai_build=srai_core.script.srai_build:main",
            "srai_release=srai_core.script.srai_release:main",
            "srai_deploy=srai_core.script.srai_deploy:main",
            "build_docker=srai_core.script.build_docker:main",
            "deploy_docker=srai_core.script.deploy_docker:main",
            "deploy_docker_local=srai_core.script.deploy_docker_local:main",
            "deploy_docker_remote_ssh=srai_core.script.deploy_docker_remote_ssh:main",
            "stop_docker_remote=srai_core.script.stop_docker_remote:main",
            "release_docker_aws_local=srai_core.script.release_docker_aws_local:main",
            "release_docker_aws_ssh=srai_core.script.release_docker_aws_ssh:main",
            "release_code_public=srai_core.script.release_code_public:main",
            "create_repository=srai_core.script.create_repository:main",
            "list_images=srai_core.script.list_images:main",
            "list_containers_ssh = srai_core.script.list_containers_ssh:main",
            "list_container_status_ssh = srai_core.script.list_container_status_ssh:main",
            "list_commands=srai_core.script.list_commands:main",
            "docker_logs_ssh=srai_core.script.docker_logs_ssh:main",
        ],
    },
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=f"{project_url}/{project_name}",
    download_url=f"{project_url}/{project_name}/archive/v_01.tar.gz",
    keywords=["SRAI", "TOOLS"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",  # Define that your audience are developers
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",  # Again, pick a license
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
    ],
)
