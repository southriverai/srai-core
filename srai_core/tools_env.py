import os
import boto3


def read_package_info():
    pass


def get_string_from_env(env_name: str) -> str:
    value = os.environ.get(env_name)
    if value is None:
        raise Exception(f"Environment variable {env_name} is not set")
    return value


def get_client_s3() -> boto3.client:
    aws_access_key_id = get_string_from_env("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = get_string_from_env("AWS_SECRET_ACCESS_KEY")
    aws_region_name = get_string_from_env("AWS_REGION_NAME")
    return boto3.client(
        "s3",
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=aws_region_name,
    )


def get_client_ecr() -> boto3.client:
    aws_access_key_id = get_string_from_env("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = get_string_from_env("AWS_SECRET_ACCESS_KEY")
    aws_region_name = get_string_from_env("AWS_REGION_NAME")
    return boto3.client(
        "ecr",
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=aws_region_name,
    )


def get_client_ecs() -> boto3.client:
    aws_access_key_id = get_string_from_env("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = get_string_from_env("AWS_SECRET_ACCESS_KEY")
    aws_region_name = get_string_from_env("AWS_REGION_NAME")
    return boto3.client(
        "ecs",
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=aws_region_name,
    )
