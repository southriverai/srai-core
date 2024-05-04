import json
import os
import sys
import time
import zipfile

import paramiko
import scp
from botocore.exceptions import WaiterError
from rivernode_core.channel_listener import ChannelListener

# from rivernode_core.tools.tools_aws import ToolsAws


class ManagerEC2(object):
    def __init__(self, system_config):
        super(ManagerEC2, self).__init__()
        self.system_config = system_config
        self.client_ec2 = self.system_config.load_client_ec2()
        self.resource_ec2 = self.system_config.load_resource_ec2()
        self.name_bucket_docker = "rivernode-docker-001"

    def load_list_image_description(self):
        # self | amazon | aws-marketplace

        if os.path.isfile("list_image_description.json"):
            with open("list_image_description.json", "r") as file:
                return json.load(file)

        list_image_description = self.client_ec2.describe_images(Owners=["amazon"])["Images"]
        with open("list_image_description.json", "w") as file:
            json.dump(list_image_description, file)
        return list_image_description

    def load_list_name_region(self):
        response = self.client_ec2.describe_regions()
        return [region["RegionName"] for region in response["Regions"]]
        # print('Regions:', response['Regions'])

    def load_list_name_availability_zone(self):
        response = self.client_ec2.describe_availability_zones()
        return [region["ZoneName"] for region in response["AvailabilityZones"]]

    def load_list_sir_id(
        self,
    ):
        response = self.client_ec2.describe_spot_instance_requests()
        list_sir_id_pending = []
        list_sir_id_fulfilled = []
        # print(response)
        for sir in response["SpotInstanceRequests"]:
            if sir["Status"]["Code"] == "fulfilled":
                list_sir_id_fulfilled.append(sir["SpotInstanceRequestId"])
            else:
                list_sir_id_pending.append(sir["SpotInstanceRequestId"])
        return list_sir_id_pending, list_sir_id_fulfilled

    def load_list_instance_id_from_list_sir_id(self, list_sir_id):
        list_filter = [{"Name": "spot-instance-request-id", "Values": list_sir_id}]
        response = self.client_ec2.describe_spot_instance_requests(Filters=list_filter)
        list_instance_id = []
        for sir in response["SpotInstanceRequests"]:
            if sir["Status"]["Code"] == "fulfilled":
                list_instance_id.append(sir["InstanceId"])
        return list_instance_id

    def load_instance_id_from_sir_id(self, sir_id):
        list_instance_id = self.load_list_instance_id_from_list_sir_id([sir_id])
        if len(list_instance_id) == 1:
            return list_instance_id[0]
        else:
            print()
            return None

    def load_list_instance_description(self, dict_tag={}):
        response = self.client_ec2.describe_instances()
        list_instance_description = []
        for list_instance_description_part in response["Reservations"]:
            for instance_description in list_instance_description_part["Instances"]:
                list_instance_description.append(instance_description)
        return list_instance_description

    def load_list_instance_id(self):
        list_instance_description = self.load_list_instance_description()
        return [instance_description["InstanceId"] for instance_description in list_instance_description]

    def instance_launch_spot(self, type_instance):
        # , count=1, is_spot=False, name_type='generel'
        # type_instance = 't2.medium' # for hosting web services
        # type_instance = 't3.xlarge'
        # size_volume_gb=100,

        price_spot = self.instance_load_spot_price(type_instance)
        print("price: " + price_spot)
        price_spot_bid = str(float(price_spot) * 1.1)
        print("bid: " + price_spot_bid)
        sys.stdout.flush()

        sir_id = self.instance_request_spot(price_spot_bid, type_instance)
        print(sir_id)
        sys.stdout.flush()
        self.sir_await_fulfilled(sir_id)
        instance_id = self.load_instance_id_from_sir_id(sir_id)
        print(instance_id)
        sys.stdout.flush()
        self.instance_await_running(instance_id)
        self.instance_await_connecting(instance_id)
        return instance_id

        # image_id = 'ami-04b29aaed8d74f8f3' #Machine learning instance AMI (at least 75 GB)
        # type_instance = 't2.medium'
        # return self.instance_launch(type_instance=type_instance, image_id=image_id, size_volume_gb=100, address_id=None)

    # in usd per hour
    # 'p2.large' has not spot price? should be like $0.3094 per Hour
    # def instance_load_spot_price(self, type_instance='t2.medium'):
    def instance_load_spot_price(self, type_instance):
        list_type_instance = [type_instance]
        name_availability_zone = self.system_config.load_name_availability_zone()
        response = self.client_ec2.describe_spot_price_history(
            InstanceTypes=list_type_instance,
            MaxResults=1,
            ProductDescriptions=["Linux/UNIX (Amazon VPC)"],
            AvailabilityZone=name_availability_zone,
        )

        # print(response['SpotPriceHistory'])
        return response["SpotPriceHistory"][0]["SpotPrice"]

    def instance_request_spot(self, spot_price, type_instance="t2.medium"):
        launch_specification = self.create_launch_specification_spot(type_instance)
        response = self.client_ec2.request_spot_instances(
            InstanceCount=1,
            LaunchSpecification=launch_specification,
            SpotPrice=spot_price,
            Type="one-time",
        )
        # print(response)
        sir_id = response["SpotInstanceRequests"][0]["SpotInstanceRequestId"]
        return sir_id

    def sir_await_fulfilled(self, sir_id):
        print("await spot_instance_request_fulfilled")
        sys.stdout.flush()
        waiter = self.client_ec2.get_waiter("spot_instance_request_fulfilled")
        waiter.wait(SpotInstanceRequestIds=[sir_id])
        instance_id = self.load_instance_id_from_sir_id(sir_id)
        while not instance_id:
            time.sleep(1)
            instance_id = self.load_instance_id_from_sir_id(sir_id)
        print("spot_instance_request_fulfilled")
        sys.stdout.flush()
        return instance_id

    def load_list_sir_description(self):
        response = self.client_ec2.describe_spot_instance_requests()
        return response["SpotInstanceRequests"]

    # TODO use this for regular ones as well
    def create_launch_specification_spot(self, type_instance="t2.medium"):
        name_key = "south_river_main"
        id_image = "ami-04b29aaed8d74f8f3"  # Machine learning instance AMI (at least 75 GB) #TODO replace this a we are using mostly docker

        # list_security_group = [{'GroupName': 'string','GroupId': 'string'}]
        list_security_group_id = ["sg-001a357692a7d0ee7"]  # Any
        list_mapping_block_device = [
            {
                "DeviceName": "/dev/sda1",
                "Ebs": {
                    "DeleteOnTermination": True,
                    "SnapshotId": "snap-0f968e137b5347031",
                    "VolumeSize": 100,
                    "VolumeType": "gp2",
                    "Encrypted": False,
                },
            }
        ]
        launch_specification = {}
        launch_specification["ImageId"] = id_image
        launch_specification["KeyName"] = name_key
        # launch_specification['SecurityGroups'] = list_security_group
        launch_specification["SecurityGroupIds"] = list_security_group_id
        launch_specification["InstanceType"] = type_instance
        launch_specification["Placement"] = {"AvailabilityZone": self.system_config.load_name_availability_zone()}
        launch_specification["BlockDeviceMappings"] = list_mapping_block_device
        return launch_specification

    # def instance_launch_small(self):
    #     image_id = '' #Machine learning instance AMI (at least 75 GB)
    #     type_instance = '' #get the smallest amount of
    #     # spin up a machine
    #     return self.instance_launch(type_instance=type_instance, image_id=image_id, size_volume_gb=100, address_id=None)

    # def instance_launch_general(self, size_volume_gb=100, address_id=None):
    #     image_id = 'ami-04b29aaed8d74f8f3' #Machine learning instance AMI (at least 75 GB)
    #     type_instance = 't2.medium'
    #     return self.instance_launch(type_instance=type_instance, image_id=image_id, size_volume_gb=100, address_id=None)

    # def instance_launch_train(self):
    #     image_id = 'ami-04b29aaed8d74f8f3' #Machine learning instance AMI (at least 75 GB)
    #     type_instance = 'p2.large' #get the smallest amount of
    #     # spin up a machine
    #     return self.instance_launch(type_instance=type_instance, image_id=image_id, size_volume_gb=100, address_id=None)

    def instance_launch(self, type_instance, size_volume_gb=100, address_id=None):
        # spin up a machine
        KeyName = "south_river_main"
        InstanceType = type_instance
        ImageId = "ami-04b29aaed8d74f8f3"
        SecurityGroupIds = ["sg-001a357692a7d0ee7"]  # Any
        BlockDeviceMappings = [
            {
                "DeviceName": "/dev/sda1",
                "Ebs": {
                    "DeleteOnTermination": True,
                    "SnapshotId": "snap-0f968e137b5347031",
                    "VolumeSize": 100,
                    "VolumeType": "gp2",
                    "Encrypted": False,
                },
            }
        ]

        instance = self.resource_ec2.create_instances(
            BlockDeviceMappings=BlockDeviceMappings,
            ImageId=ImageId,
            SecurityGroupIds=SecurityGroupIds,
            InstanceType=InstanceType,
            KeyName=KeyName,
            MinCount=1,
            MaxCount=1,
        )[0]

        if address_id:  # attach ip
            address = self.resource_ec2.VpcAddress(address_id)
            address.associate(instance.instance_id)
        return instance.instance_id

    def instance_get_hostname(self, instance_id):
        hostname = self.resource_ec2.Instance(instance_id).public_dns_name
        return hostname

    def instance_await_running(self, instance_id):
        waiter = self.client_ec2.get_waiter("instance_running")
        waiter.wait(InstanceIds=[instance_id])

    def instance_await_connecting(self, instance_id):
        pass

    def instance_run_command_killall9(self, instance_id, name_program):
        path_file_key_ssh = self.system_config.load_path_file_key_ssh()
        self.instance_run_command(instance_id, path_file_key_ssh, "sudo killall -9 " + name_program)

    def instance_run_command_start_service_model(self, instance_id, name_model, name_port="5000"):
        path_file_key_ssh = self.system_config.load_path_file_key_ssh()
        hostname = self.resource_ec2.Instance(instance_id).public_dns_name
        api_key = "XXX"
        # TODO replace command line arguments by descriptor_service.json
        # TODO upload
        # source activate tensorflow_p36; python ~/code/rivernode_keras/src/keras_core/service_model.py 127.0.0.1 5000 XXX xceptionimagenet_top_poolavg_base
        # TODO remove cv2 and replace with imageio
        command = (
            "source activate tensorflow_p36; pip install opencv-python; cd ~/code/rivernode_keras/src/keras_core/; python ~/code/rivernode_keras/src/keras_core/service_model.py "
            + hostname
            + " "
            + name_port
            + " "
            + api_key
            + " "
            + name_model
        )
        self.instance_run_command(instance_id, path_file_key_ssh, command)

    def instance_run_command(self, instance_id, path_file_key_ssh, string_command, disown=False):
        # get instance hostname
        instance = self.resource_ec2.Instance(instance_id)
        if not instance.state["Name"] == "running":
            raise RuntimeError('instance state not "running"')

        print("connecting to machine: " + instance_id)
        sys.stdout.flush()
        client_ssh = paramiko.SSHClient()
        client_ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client_ssh.connect(instance.public_dns_name, username="ubuntu", key_filename=path_file_key_ssh)

        print("running command: " + string_command)
        sys.stdout.flush()
        _, stdout, _ = client_ssh.exec_command(string_command)
        if disown:
            pass
        else:
            while not (stdout.channel.exit_status_ready()):
                for line in stdout.readlines():
                    print(line)
            for line in stdout.readlines():
                print(line)

        print("closing connection to machine: " + instance_id)
        client_ssh.close()

    def instance_upload_list_file_by_ssh_key(self, instance_id, list_path_file_tuple):
        path_file_key_ssh = self.system_config.load_path_file_key_ssh()
        hostname = self.resource_ec2.Instance(instance_id).public_dns_name
        client_ssh = paramiko.SSHClient()
        client_ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client_ssh.connect(hostname, username="ubuntu", key_filename=path_file_key_ssh)
        self.instance_upload_list_file_by_ssh_client(client_ssh, list_path_file_tuple)
        client_ssh.close()

    def instance_upload_list_file_by_ssh_client(self, client_ssh, list_path_file_tuple):
        client_scp = scp.SCPClient(client_ssh.get_transport())
        self.instance_upload_list_file_by_scp_client(client_scp, list_path_file_tuple)
        client_scp.close()

    def instance_upload_list_file_by_scp_client(self, client_scp, list_tuple_path_file):
        for tuple_path_file in list_tuple_path_file:
            try:
                path_file_source, path_file_target = tuple_path_file
                print("uploading : " + path_file_source)
                sys.stdout.flush()
                client_scp.put(path_file_source, path_file_target)
            except Exception as e:
                print(e)
                print("error on file: " + path_file_source)
                sys.stdout.flush()

    def instance_run_task(self, instance_id, json_task):
        path_file_key_ssh = self.system_config.load_path_file_key_ssh()
        self.instance_upload_list_file(instance_id, path_file_key_ssh, [], "task.json")
        self.instance_run_command(
            instance_id, path_file_key_ssh, "source activate tensorflow_p36; python script_run_task.py"
        )

    def instance_prepare_rivernode(self, instance_id):
        path_file_key_git = self.system_config.load_path_file_key_git()

        list_tuple_key_git = []
        list_tuple_key_git.append((path_file_key_git, "rivernode_git"))
        list_tuple_repository = []
        list_tuple_repository.append(("git@github.com:kozzion/rivernode_core.git", "rivernode_core"))
        list_tuple_repository.append(("git@github.com:kozzion/rivernode_keras.git", "rivernode_keras"))
        list_tuple_repository.append(("git@github.com:kozzion/rivernode_network.git", "rivernode_network"))
        list_tuple_repository.append(("git@github.com:kozzion/rivernode_social.git", "rivernode_social"))
        self.instance_prepare(instance_id, list_tuple_key_git, list_tuple_repository)

    def instance_prepare(self, instance_id, list_tuple_key_git, list_tuple_repository):  # This does nothing anymore
        path_file_key_ssh = self.system_config.load_path_file_key_ssh()
        # get instance hostname
        instance = self.resource_ec2.Instance(instance_id)
        if not instance.state["Name"] == "running":
            raise RuntimeError('instance state not "running"')

        print("connecting to maching: " + instance_id + " at " + instance.public_dns_name)
        sys.stdout.flush()
        client_ssh = paramiko.SSHClient()
        client_ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client_ssh.connect(instance.public_dns_name, username="ubuntu", key_filename=path_file_key_ssh)

        print("cleaning up instance")
        sys.stdout.flush()
        _, stdout, _ = client_ssh.exec_command("sudo rm -Rf key")
        stdout.channel.recv_exit_status()
        _, stdout, _ = client_ssh.exec_command("sudo rm -Rf code")
        stdout.channel.recv_exit_status()
        _, stdout, _ = client_ssh.exec_command("mkdir key")
        stdout.channel.recv_exit_status()
        _, stdout, _ = client_ssh.exec_command("mkdir code")
        stdout.channel.recv_exit_status()

        client_scp = scp.SCPClient(client_ssh.get_transport())

        print("copying config")
        _, stdout, _ = client_ssh.exec_command("mkdir ~/code/rivernode_config/")
        client_scp.put("C:\\project\\rivernode_config\\config.json", "~/code/rivernode_config/config.json")
        client_scp.put("C:\\project\\rivernode_config\\config.json", "~/code/rivernode_config/config.json")
        stdout.channel.recv_exit_status()

        print("copying git keys")
        for tuple_key_git in list_tuple_key_git:
            try:
                path_file_key_git_source, name_repository = tuple_key_git
                name_file_key_git = os.path.basename(path_file_key_git_source)
                path_dir_key_git_target = "~/key/" + name_repository + "/"
                path_file_key_git_target = "~/key/" + name_repository + "/" + name_file_key_git
                print("copying git key: " + name_file_key_git)
                sys.stdout.flush()

                _, stdout, stderr = client_ssh.exec_command("mkdir " + path_dir_key_git_target)
                stdout.channel.recv_exit_status()
                for line in stdout.readlines():
                    print(line)
                for line in stderr.readlines():
                    print(line)

                client_scp.put(path_file_key_git_source, path_file_key_git_target)

                _, stdout, stderr = client_ssh.exec_command("chmod 400 " + path_file_key_git_target)
                stdout.channel.recv_exit_status()
                for line in stdout.readlines():
                    print(line)
                for line in stderr.readlines():
                    print(line)

            except Exception as e:
                print(e)
                print("error on key: " + name_file_key_git)
                sys.stdout.flush()
        client_scp.close()

        # clone repositories
        print("git keys ready, now cloning repositories")
        sys.stdout.flush()
        for tuple_repository in list_tuple_repository:
            channel = client_ssh.get_transport().open_session()
            channel.get_pty()
            channel.invoke_shell()
            channel.recv(10000)
            cl = ChannelListener(channel)
            cl.start()

            channel.send('eval "$(ssh-agent -s)"\n')
            # time.sleep(1)
            for tuple_key_git in list_tuple_key_git:
                try:
                    path_file_key_git_source, name_key = tuple_key_git
                    name_file_key_git = os.path.basename(path_file_key_git_source)
                    path_dir_key_git_target = "~/key/" + name_key + "/"
                    path_file_key_git_target = "~/key/" + name_key + "/" + name_file_key_git

                    channel.send("ssh-add " + path_file_key_git_target + "\n")
                    time.sleep(1)

                except Exception as e:
                    print(e)
                    print("error on key: " + name_file_key_git)
                    sys.stdout.flush()

            url_git, name_repository = tuple_repository
            channel.send("git clone " + url_git + " ~/code/" + name_repository + "\n")
            channel.send("yes\n")

        channel = client_ssh.get_transport().open_session()  # TODO THIS is terrible for some reason this blocks
        channel.get_pty()  # TODO THIS is terrible for some reason this blocks
        channel.invoke_shell()  # TODO THIS is terrible for some reason this blocks
        time.sleep(30)

        client_ssh.close()
        print("all repositories cloned")
        # TODO clean this up

        # stdout_.channel.recv_exit_status()
        # lines = stdout_.readlines()
        # for line in lines:
        #     print line

    def instance_await_terminated(self, instance_id):
        waiter = self.client_ec2.get_waiter("instance_terminated")
        waiter.wait(InstanceIds=[instance_id])

    def instance_terminate(self, instance_id):
        list_instance_id = [instance_id]
        self.client_ec2.terminate_instances(InstanceIds=list_instance_id)

    def instance_terminate_all(self):
        list_instance_id = self.load_list_instance_id()
        self.client_ec2.terminate_instances(InstanceIds=list_instance_id)

    def docker_build(
        self,
        instance_id,
        path_file_docker_source,
        name_image,
        include_key=False,
        upload_image=False,
        list_download_before=[],
    ):
        path_file_key_ssh = self.system_config.load_path_file_key_ssh()

        # get instance hostname
        path_file_docker_target = "~/build/Dockerfile"
        instance = self.resource_ec2.Instance(instance_id)
        if not instance.state["Name"] == "running":
            raise RuntimeError('instance state not "running"')

        print("connecting to : " + instance_id + " at " + instance.public_dns_name)
        sys.stdout.flush()
        client_ssh = paramiko.SSHClient()
        client_ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client_ssh.connect(instance.public_dns_name, username="ubuntu", key_filename=path_file_key_ssh)

        for name_image_download in list_download_before:
            self.docker_download_for_client(client_ssh, name_image_download)

        # clean up by removing docker file
        print("clean docker build context")
        sys.stdout.flush()
        command = "sudo rm -rf build"
        self.remote_execute(client_ssh, command)
        command = "mkdir build"
        self.remote_execute(client_ssh, command)

        print("copy docker file")
        client_scp = scp.SCPClient(client_ssh.get_transport())
        client_scp.put(path_file_docker_source, path_file_docker_target)
        client_scp.close()

        print("build docker image")
        if include_key:
            path_file_key_git = self.system_config.load_path_file_key_git()
            with open(path_file_key_git, "r") as file:  # TODO get this directly from config
                string_git_key = file.read()
            path_file_key_git = self.system_config.load_path_file_key_git()
            command = (
                "sudo docker build -t "
                + name_image
                + " -f "
                + path_file_docker_target
                + ' --build-arg SSH_PRIVATE_KEY="'
                + string_git_key
                + '"'
                + "  ~/build"
            )
        else:
            command = "sudo docker build -t " + name_image + " -f " + path_file_docker_target + "  ~/build"
        self.remote_execute(client_ssh, command)

        if upload_image:
            self.docker_upload_for_client(client_ssh, name_image)
        client_ssh.close()

    def docker_upload(self, instance_id, name_image):
        # get instance hostname
        path_file_key_ssh = self.system_config.load_path_file_key_ssh()

        instance = self.resource_ec2.Instance(instance_id)
        if not instance.state["Name"] == "running":
            raise RuntimeError('instance state not "running"')

        print("connecting to : " + instance_id + " at " + instance.public_dns_name)
        sys.stdout.flush()
        client_ssh = paramiko.SSHClient()
        client_ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client_ssh.connect(instance.public_dns_name, username="ubuntu", key_filename=path_file_key_ssh)

        self.docker_upload_for_client(client_ssh, name_image)

    def docker_upload_for_client(self, client_ssh, name_image):
        print("save docker image to tar-file")
        path_file_docker_image_target = name_image + ".tar"
        command = "docker save -o " + path_file_docker_image_target + " " + name_image
        self.remote_execute(client_ssh, command)

        print("upload tar-file docker to s3")
        command = "AWS_ACCESS_KEY_ID=" + self.system_config.load_aws_access_key_id()
        command += " AWS_SECRET_ACCESS_KEY=" + self.system_config.load_aws_secret_access_key()
        command += (
            " aws s3 cp "
            + path_file_docker_image_target
            + " s3://"
            + self.name_bucket_docker
            + "/"
            + path_file_docker_image_target
        )
        self.remote_execute(client_ssh, command)

    def docker_download(self, instance_id, name_image):
        path_file_key_ssh = self.system_config.load_path_file_key_ssh()
        # get instance hostname
        instance = self.resource_ec2.Instance(instance_id)
        if not instance.state["Name"] == "running":
            raise RuntimeError('instance state not "running"')

        print("connecting to : " + instance_id + " at " + instance.public_dns_name)
        sys.stdout.flush()
        client_ssh = paramiko.SSHClient()
        client_ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client_ssh.connect(instance.public_dns_name, username="ubuntu", key_filename=path_file_key_ssh)

        self.docker_download_for_client(client_ssh, name_image)

    def docker_download_for_client(self, client_ssh, name_image):
        path_file_docker_image_target = name_image + ".tar"
        print("download tar-file docker to s3")
        command = "AWS_ACCESS_KEY_ID=" + self.system_config.load_aws_access_key_id()
        command += " AWS_SECRET_ACCESS_KEY=" + self.system_config.load_aws_secret_access_key()
        command += (
            " aws s3 cp s3://"
            + self.name_bucket_docker
            + "/"
            + path_file_docker_image_target
            + " "
            + path_file_docker_image_target
        )
        self.remote_execute(client_ssh, command)

        print("load docker image from tar-file")
        command = "docker load -i " + path_file_docker_image_target
        self.remote_execute(client_ssh, command)

    def docker_start_esb(self, instance_id):
        path_file_key_ssh = self.system_config.load_path_file_key_ssh()
        instance = self.resource_ec2.Instance(instance_id)
        if not instance.state["Name"] == "running":
            raise RuntimeError('instance state not "running"')
        name_host_local = instance.public_dns_name
        name_port_local = "5000"
        name_host_esb = name_host_local
        name_port_esb = name_port_local
        api_key_esb = "XXXX"
        name_image = "image_rivernode_controller_esb"

        self.docker_start(
            path_file_key_ssh,
            instance_id,
            name_host_local,
            name_port_local,
            name_host_esb,
            name_port_esb,
            api_key_esb,
            name_image,
        )

    def docker_start_for_demo(self, instance_id, name_image, name_config, download=True):
        name_host_local = self.instance_get_hostname(instance_id)
        name_port_local = "5000"
        name_host_esb = ""
        name_port_esb = ""
        api_key_esb = "XXXX"

        dict_env = {}
        dict_env["NAME_CONFIG"] = name_config
        dict_env["NAME_REGION"] = self.system_config.load_name_region()
        dict_env["AWS_ACCESS_KEY_ID"] = self.system_config.load_aws_access_key_id()
        dict_env["AWS_SECRET_ACCESS_KEY"] = self.system_config.load_aws_secret_access_key()
        dict_env["BASE64_KEY_ENCRYPTION_CONFIG"] = self.system_config.load_base64_key_encryption_config()
        self.docker_start(
            instance_id,
            name_host_local,
            name_port_local,
            name_host_esb,
            name_port_esb,
            api_key_esb,
            name_image,
            download,
            dict_env,
        )

    def docker_start(
        self,
        instance_id,
        name_host_local,
        name_port_local,
        name_host_esb,
        name_port_esb,
        api_key_esb,
        name_image,
        download=True,
        dict_env={},
    ):
        path_file_key_ssh = self.system_config.load_path_file_key_ssh()
        instance = self.resource_ec2.Instance(instance_id)
        if not instance.state["Name"] == "running":
            raise RuntimeError('instance state not "running"')

        print("connecting to : " + instance_id + " at " + name_host_local)
        sys.stdout.flush()
        client_ssh = paramiko.SSHClient()
        client_ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client_ssh.connect(name_host_local, username="ubuntu", key_filename=path_file_key_ssh)

        if download:
            print("download tar-file docker from s3")
            path_file_docker_image_target = name_image + ".tar"
            command = "AWS_ACCESS_KEY_ID=" + self.system_config.load_aws_access_key_id()
            command += " AWS_SECRET_ACCESS_KEY=" + self.system_config.load_aws_secret_access_key()
            command += (
                " aws s3 cp s3://"
                + self.name_bucket_docker
                + "/"
                + path_file_docker_image_target
                + " "
                + path_file_docker_image_target
            )
            self.remote_execute(client_ssh, command)

            print("load docker image from tar-file")
            command = "docker load -i " + path_file_docker_image_target
            self.remote_execute(client_ssh, command)

        print("start image: " + name_image)
        command = "sudo docker run -i -p " + name_port_local + ":" + name_port_local
        command += " -e NAME_HOST_LOCAL='" + name_host_local + "'"
        command += " -e NAME_PORT_LOCAL='" + name_port_local + "'"
        command += " -e NAME_HOST_ESB='" + name_host_esb + "'"
        command += " -e NAME_PORT_ESB='" + name_port_esb + "'"
        command += " -e API_KEY_ESB='" + api_key_esb + "'"

        # add extra items
        for key, value in dict_env.items():
            command += " -e " + key + "='" + value + "'"

        command += " " + name_image
        self.remote_execute(client_ssh, command)
