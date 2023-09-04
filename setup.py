from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

with open("requirements.txt", "r") as f:
    requirements = f.read().splitlines()

setup(
    name="srai-core",
    packages=find_packages(),
    version="0.8.0",
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
            "release_docker_aws=srai_core.script.release_docker_aws:main",
            "create_repository=srai_core.script.create_repository:main",
            "list_images=srai_core.script.list_images:main",
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
