import os
from typing import List
from srai_core.tools_docker import (
    get_client_ssh,
    build_docker,
    list_container_name,
    get_image_tag,
    start_container_ssh,
    stop_container,
    release_docker_aws,
    remove_container,
)


if __name__ == "__main__":
    build_docker()
    release_docker_aws()
    account_id = "169192938140"
    region_name = "eu-west-1"
    hostname = "18.185.177.93"  # TODO these could even come from boto3
    username = "ubuntu"
    path_file_pem = "c:/key/lightsaildefaultkey-eu-central-1.pem"
    if not os.path.exists(path_file_pem):
        raise Exception(f"File {path_file_pem} does not exist")

    image_tag = get_image_tag()
    container_name = image_tag.split(":")[0].split("/")[-1]
    dict_env = {}
    dict_env["SRAI_TELEGRAM_TOKEN"] = os.environ.get("SRAI_TELEGRAM_TOKEN")
    dict_env["AWS_ACCESS_KEY_ID"] = os.environ.get("AWS_ACCESS_KEY_ID")
    dict_env["AWS_SECRET_ACCESS_KEY"] = os.environ.get("AWS_SECRET_ACCESS_KEY")
    dict_env["AWS_DEFAULT_REGION"] = os.environ.get("AWS_DEFAULT_REGION")
    dict_env["IMAGE_TAG"] = image_tag

    ssh_client = get_client_ssh(hostname, username, path_file_pem)
    list_container_name_present = list_container_name(ssh_client)
    print(f"Container name: {container_name}")
    print(list_container_name_present)
    if container_name in list_container_name_present:
        print(f"Container {container_name} is in use")
        stop_container(ssh_client, container_name)
        remove_container(ssh_client, container_name)
    remove_container(ssh_client, container_name)  # TODO for good riddance
    start_container_ssh(
        ssh_client, account_id, region_name, image_tag, container_name, dict_env
    )
