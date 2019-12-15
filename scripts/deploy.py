"""
Example docker deployment to AWS ECS cluster.

The script does the following:

    1. Loads environment variables from .env file in the project root

    For each service in SERVICES
    2. Generates a populated ECS task definition
        - You can configure your task definitions in the get_task_definition() method.
    3. Optionally authenticate Docker to ECR
    4. Optionally build any configured containers
    5. Optionally push any configured containers to ECR
    6. Register the new task definition in ECR
    7. Retrieve the latest task definition revision number
    8. Update the running service with the new task definition and force a new deployment
"""

# pylint: disable=dangerous-default-value,too-many-arguments,missing-function-docstring

import datetime
import json
import os
import subprocess
from typing import List

import boto3
import docker
import tomlkit
from dotenv import dotenv_values


def get_project_meta() -> dict:
    pyproj_path = "./pyproject.toml"
    if os.path.exists(pyproj_path):
        with open(pyproj_path, "r") as pyproject:
            file_contents = pyproject.read()
        return tomlkit.parse(file_contents)["tool"]["poetry"]
    else:
        return {}


pkg_meta = get_project_meta()
project = pkg_meta.get("name")
version = pkg_meta.get("version")

ENV = os.getenv("ENV", "prod")
AWS_ACCOUNT_ID = os.getenv("AWS_ACCOUNT_ID")
SERVICE_NAME: str = os.getenv("SERVICE_NAME")  # type: ignore
IMAGE_NAME: str = os.getenv("IMAGE_NAME")  # type: ignore
CLUSTER_NAME = os.getenv("ECS_CLUSTER")  # type: ignore
TASK_IAM_ROLE = f"arn:aws:iam::{AWS_ACCOUNT_ID}:role/ihs-task-role"

if not any([ENV, AWS_ACCOUNT_ID, SERVICE_NAME, IMAGE_NAME, CLUSTER_NAME]):
    raise ValueError("One or more environment variables are missing")


SERVICES: List[str] = [
    "ihs-web",
    "ihs-worker-collector",
    "ihs-worker-deleter",
    "ihs-worker-submitter",
    "ihs-worker-default",
    "ihs-cron",
]

IMAGES = [
    {"name": SERVICE_NAME, "dockerfile": "Dockerfile", "build_context": "."},
]

TAGS = [
    {"key": "domain", "value": "technology"},
    {"key": "service_name", "value": project},
    {"key": "environment", "value": ENV},
    {"key": "terraform", "value": "true"},
]


BUILD = False
PUSH = False

print("\n\n" + "-" * 30)
print(f"ENV: {ENV}")
print(f"AWS_ACCOUNT_ID: {AWS_ACCOUNT_ID}")
print(f"CLUSTER_NAME: {CLUSTER_NAME}")
print(f"SERVICES: {SERVICES}")
print("-" * 30 + "\n\n")


task_envs = dotenv_values(".env.production")


def transform_envs(d: dict):
    return [{"name": k, "value": v} for k, v in d.items()]


def get_task_definition(
    name: str,
    envs: dict,
    account_id: str,
    service_name: str,
    environment: str,
    image_name: str,
    tags: list = [],
    task_iam_role_arn: str = "ecsTaskExecutionRole",
):
    # image = f"{account_id}.dkr.ecr.us-east-1.amazonaws.com/{image_name}:{environment}"
    image = IMAGE_NAME
    defs = {
        "ihs-web": {
            "containerDefinitions": [
                {
                    "name": "ihs-web",
                    "command": ["ihs", "run", "web", "-b 0.0.0.0:8000"],
                    "memoryReservation": 128,
                    "image": image,
                    "essential": True,
                    "environment": transform_envs(envs),
                    "portMappings": [
                        {
                            "containerPort": 8000,
                            "protocol": "tcp",
                        },  # dynamically allocates host port
                    ],
                },
            ],
            "executionRoleArn": "ecsTaskExecutionRole",
            "family": f"{service_name}",
            "networkMode": "bridge",
            "taskRoleArn": task_iam_role_arn,
            "tags": tags,
            "cpu": "256",  # from 128 CPU units (0.125 vCPUs) and 10240 CPU units (10 vCPUs)
        },
        "ihs-worker-submitter": {
            "containerDefinitions": [
                {
                    "name": "ihs-worker",
                    "command": [
                        "ihs",
                        "run",
                        "worker",
                        "-c",
                        "10",
                        "-Q",
                        "ihs-submissions-h,ihs-submissions-v",
                        # "--loglevel",
                        # "info",
                    ],
                    "memoryReservation": 128,
                    "image": image,
                    "essential": True,
                    "environment": transform_envs(envs),
                },
            ],
            "executionRoleArn": "ecsTaskExecutionRole",
            "family": f"{service_name}",
            "networkMode": "bridge",
            "taskRoleArn": task_iam_role_arn,
            "tags": tags,
            "cpu": "256",  # from 128 CPU units (0.125 vCPUs) and 10240 CPU units (10 vCPUs)
        },
        "ihs-worker-collector": {
            "containerDefinitions": [
                {
                    "name": "ihs-worker",
                    "command": [
                        "ihs",
                        "run",
                        "worker",
                        "-c",
                        "10",
                        "-Q",
                        "ihs-collections-h,ihs-collections-v",
                        # "--loglevel",
                        # "warn",
                    ],
                    "memoryReservation": 128,
                    "image": image,
                    "essential": True,
                    "environment": transform_envs(envs),
                },
            ],
            "executionRoleArn": "ecsTaskExecutionRole",
            "family": f"{service_name}",
            "networkMode": "bridge",
            "taskRoleArn": task_iam_role_arn,
            "tags": tags,
            "cpu": "256",  # from 128 CPU units (0.125 vCPUs) and 10240 CPU units (10 vCPUs)
        },
        "ihs-worker-deleter": {
            "containerDefinitions": [
                {
                    "name": "ihs-worker",
                    "command": [
                        "ihs",
                        "run",
                        "worker",
                        "-c",
                        "10",
                        "-Q",
                        "ihs-deletions-h,ihs-deletions-v",
                        # "--loglevel",
                        # "warn",
                    ],
                    "memoryReservation": 128,
                    "image": image,
                    "essential": True,
                    "environment": transform_envs(envs),
                },
            ],
            "executionRoleArn": "ecsTaskExecutionRole",
            "family": f"{service_name}",
            "networkMode": "bridge",
            "taskRoleArn": task_iam_role_arn,
            "tags": tags,
            "cpu": "256",  # from 128 CPU units (0.125 vCPUs) and 10240 CPU units (10 vCPUs)
        },
        "ihs-worker-default": {
            "containerDefinitions": [
                {
                    "name": "ihs-worker",
                    "command": [
                        "ihs",
                        "run",
                        "worker",
                        "-c",
                        "10",
                        "-Q",
                        "ihs-default",
                        # "--loglevel",
                        # "warn",
                    ],
                    "memoryReservation": 128,
                    "image": image,
                    "essential": True,
                    "environment": transform_envs(envs),
                },
            ],
            "executionRoleArn": "ecsTaskExecutionRole",
            "family": f"{service_name}",
            "networkMode": "bridge",
            "taskRoleArn": task_iam_role_arn,
            "tags": tags,
            "cpu": "256",  # from 128 CPU units (0.125 vCPUs) and 10240 CPU units (10 vCPUs)
        },
        "ihs-cron": {
            "containerDefinitions": [
                {
                    "name": "ihs-cron",
                    "command": ["ihs", "run", "cron", "--loglevel", "debug"],
                    "memoryReservation": 128,
                    "cpu": 256,
                    "image": image,
                    "essential": True,
                    "environment": transform_envs(envs),
                },
            ],
            "executionRoleArn": "ecsTaskExecutionRole",
            "family": f"{service_name}",
            "networkMode": "bridge",
            "taskRoleArn": task_iam_role_arn,
            "tags": tags,
            "cpu": "256",  # from 128 CPU units (0.125 vCPUs) and 10240 CPU units (10 vCPUs)
        },
    }

    return defs[name]


class AWSContainerInterface:
    ignore_env = False
    _env_name = None
    access_key_id = None
    secret_access_key = None
    region = None
    account_id = None
    _ecr = None
    _ecs = None
    cluster_name = None
    service_name = None
    _docker_client = None
    _docker_is_authorized = False

    def __init__(self, env_name: str = None, ignore_env: bool = False):
        self.ignore_env = ignore_env
        self._env_name = env_name
        self.credentials_from_profile()

    @property
    def docker_is_authorized(self):
        return self._docker_is_authorized

    @property
    def env_name(self):
        if not self.ignore_env:
            return os.getenv("ENV", self._env_name)
        else:
            return self._env_name

    @property
    def has_credentials(self):
        return all(
            [
                self.access_key_id is not None,
                self.secret_access_key is not None,
                self.region is not None,
                self.account_id is not None,
            ]
        )

    @property
    def ecr_url(self):
        if not self.has_credentials:
            self.credentials_from_profile()
        return f"{self.account_id}.dkr.ecr.{self.region}.amazonaws.com"

    @property
    def docker_client(self):
        return self._docker_client or self._get_docker_client()

    def credentials_from_profile(self, env_name: str = None):
        """Read AWS credentials from file.

        :param filename: Credentials filename, defaults to '.aws_credentials.json'
        :param filename: str, optional
        :return: Dictionary of AWS credentials.
        :rtype: Dict[str, str]
        """

        env_name = env_name or self.env_name

        # TODO: Incorporate session token
        credentials = {
            "access_key_id": os.getenv("AWS_ACCESS_KEY_ID"),
            "secret_access_key": os.getenv("AWS_SECRET_ACCESS_KEY"),
            "region": os.getenv("AWS_REGION", "us-east-1"),
            "account_id": os.getenv("AWS_ACCOUNT_ID"),
            "session_token": os.getenv("AWS_SESSION_TOKEN"),
            "security_token": os.getenv("AWS_SECURITY_TOKEN"),
        }

        [setattr(self, k, v) for k, v in credentials.items()]

        return credentials

    def get_client(self, service_name: str) -> "client":

        if not self.has_credentials:
            self.credentials_from_profile()

        return boto3.client(
            service_name,
            aws_access_key_id=self.access_key_id,
            aws_secret_access_key=self.secret_access_key,
            region_name=self.region,
            aws_session_token=self.session_token,
        )

    def ecs(self):
        return self._ecs or self.get_client("ecs")

    def ecr(self):
        return self._ecr or self.get_client("ecr")

    def _get_docker_client(self, bypass_login: bool = False):

        # if not self.docker_is_authorized and bypass_login:
        docker_client = docker.DockerClient(base_url="unix:///var/run/docker.sock")

        # ecr_client = boto3.client('ecr', region_name=self.region)

        # token = ecr_client.get_authorization_token()

        # username, password = base64.b64decode(token['authorizationData'][0]['authorizationToken']).decode().split(':')
        # registry = token['authorizationData'][0]['proxyEndpoint']

        # print(docker_client.login(username, password, registry=registry, reauth=True))
        self._docker_login()

        return docker_client

    def _docker_login(self) -> str:
        """Authenticate to AWS in Docker

        Returns:
            dict -- credential mapping from get-login
        """
        os.environ["AWS_ACCOUNT_ID"] = self.account_id
        os.environ["AWS_ACCESS_KEY_ID"] = self.access_key_id
        os.environ["AWS_SECRET_ACCESS_KEY"] = self.secret_access_key
        credentials = (
            subprocess.check_output(["aws", "ecr", "get-login", "--no-include-email"])
            .decode("ascii")
            .strip()
        )

        message = os.popen(credentials).read()  # execute login in subprocess

        print(message)
        if "succeeded" in message.lower():
            self._docker_is_authorized = True

        # return credentials

    def update_service(self, cluster_name: str, service_name: str, force=True):

        # force new deployment of ECS service
        print(
            "\n\n"
            + f"{self.env_name} -- Forcing new deployment to ECS: {self.cluster_name}/{self.service_name}"
            + "\n\n"
        )
        response = self.ecs().update_service(
            cluster=cluster_name, service=service_name, forceNewDeployment=force
        )

        print("\n\n" + f"{self.env_name} -- Exiting ECS deployment update." + "\n\n")
        return self

    def update_task_definition(self):
        pass


class DockerImage:
    """ Image should be agnostic to its destination """

    build_context = "."
    dockerfile = "./Dockerfile"
    name = None
    image = None
    image_manager = None

    def __init__(
        self,
        image_manager: AWSContainerInterface,
        name: str = None,
        dockerfile: str = None,
        build_context: str = None,
        show_log: bool = False,
        tags: list = None,
    ):

        self.name = name
        self.image_manager = image_manager
        self.build_context = build_context or self.build_context
        self.dockerfile = dockerfile or self.dockerfile
        self.tags = self.default_tags + (tags or [])

    @property
    def commit_hash(self):
        return (
            subprocess.check_output(["git", "rev-parse", "--short", "HEAD"])
            .decode("ascii")
            .strip()
        )

    @property
    def build_date(self):
        return datetime.datetime.now().date()

    @property
    def default_tags(self):
        return [
            "latest",
            f"{self.build_date}",
            self.commit_hash,
            image_manager.env_name,
        ]

    @property
    def client(self):
        return self.image_manager.docker_client

    @property
    def repo_name(self):
        if isinstance(self.image_manager, AWSContainerInterface):
            return f"{self.image_manager.ecr_url}/{self.name}"
        else:
            return None  # docker hub url here

    def _logstream(self, source, stream_type: str):

        if stream_type == "build":
            while True:
                try:
                    output = next(source)
                    if "stream" in output.keys():
                        print(output["stream"].strip("\n"))
                    else:
                        print(output)
                except StopIteration:
                    break
                except ValueError:
                    print("Error parsing output from docker image build: %s" % output)

        elif stream_type == "push":
            for chunk in source.split("\r\n"):
                try:
                    if chunk:
                        d = json.loads(chunk)
                        print(d)

                except StopIteration:
                    break
                except ValueError:
                    print("Error parsing output from docker push to ECR: %s" % chunk)

    def build(self, show_log: bool = False):

        self.print_message(f"Building docker image: {self.name}")

        self.image, generator = self.client.images.build(
            path=self.build_context, dockerfile=self.dockerfile, tag=self.name
        )

        if show_log:
            self._logstream(generator, stream_type="build")

        self.print_message(f"Docker image build complete: {self.name}")

        return self

    def tag(self, name: str, tag: str):
        self.image.tag(name, tag=tag)
        return self

    def push(self, tag: str = None, show_log: bool = False):

        tag = tag or "latest"

        self.tag(self.repo_name, tag)

        self.print_message(f"Pushing to remote: {self.repo_name}")

        generator = self.client.images.push(self.repo_name, tag=tag)

        if show_log:
            self._logstream(generator, stream_type="push")

        self.print_message("Push complete")

        return self

    def print_message(self, message: str):
        print("\n" + "-" * 10 + f" {message} " + "-" * 10 + "\n")

    def deploy(
        self,
        tag: str = None,
        build: bool = True,
        push: bool = True,
        show_log: bool = False,
    ):

        if build:
            self.build(show_log=show_log)
        else:
            self.image = self.client.images.get(self.name)

        if push:
            self.push(show_log=show_log, tag=tag)

    def deploy_all(self, *args, **kwargs):
        for tag in self.tags:
            self.deploy(tag, *args, **kwargs)


image_manager = AWSContainerInterface(ENV)

# image_manager._docker_login()

# for image in IMAGES:
#     i = DockerImage(image_manager, **image)  # type: ignore
#     i.deploy_all(build=BUILD, push=PUSH, show_log=True)

client = image_manager.ecs()


def get_latest_revision(task_name: str):
    response = client.describe_task_definition(taskDefinition=task_name)
    return response["taskDefinition"]["revision"]


results = []
for service in SERVICES:
    print(f"{service}: Creating new task definition")
    cdef = get_task_definition(
        name=service,
        envs=task_envs,
        account_id=image_manager.account_id,  # type: ignore
        service_name=service,
        environment=ENV,
        image_name=SERVICE_NAME,
        tags=TAGS,
        task_iam_role_arn=TASK_IAM_ROLE,
    )
    print(f"{service}: Registering new revision in {image_manager.account_id}")
    # pprint(cdef)
    client.register_task_definition(**cdef)

    rev_num = get_latest_revision(f"{service}")
    print(f"{service}: Updating service to {service}:{rev_num}")
    results.append((service, rev_num))

for service, rev_num in results:
    response = client.update_service(
        cluster=CLUSTER_NAME,
        service=service,
        forceNewDeployment=True,
        taskDefinition=f"{service}:{rev_num}",
    )
    print(f"{service}: Updated service to {service}:{rev_num}")
