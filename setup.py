from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

with open("requirements.txt", "r") as f:
    requirements = f.read().splitlines()


setup(
    name="srai-core",
    packages=find_packages(),
    version="0.10.0",  # TODO manual....
    license="MIT",
    package_data={},
    python_requires=">=3.5",
    install_requires=requirements,
    author="Jaap Oosterbroek",
    author_email="jaap.oosterbroek@southriverai.com",
    description="A library core functions used in other SRAI libraries.",
    entry_points={
        "console_scripts": [
            "build_docker=srai_core.script.build_docker:main",
            "deploy_docker_local=srai_core.script.deploy_docker_local:main",
            "deploy_docker_remote_ssh=srai_core.script.deploy_docker_remote_ssh:main",
            "release_docker_aws_local=srai_core.script.release_docker_aws_local:main",
            "release_docker_aws_ssh=srai_core.script.release_docker_aws_ssh:main",
            "release_code_public=srai_core.script.release_code_public:main",
            "create_repository=srai_core.script.create_repository:main",
            "list_images=srai_core.script.list_images:main",
            "list_containers_ssh = srai_core.script.list_containers_ssh:main",
            "list_container_status = srai_core.script.list_container_status:main",
            "list_commands=srai_core.script.list_commands:main",
        ],
    },
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/southriverai/srai-core",
    download_url="https://github.com/southriverai/srai-core/archive/v_01.tar.gz",
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
