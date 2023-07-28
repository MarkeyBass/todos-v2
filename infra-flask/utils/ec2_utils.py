import boto3


class EC2Manager:
    def __init__(self, region_name='us-east-1'):
        self.ec2_client = boto3.client('ec2', region_name=region_name)

    def create_ec2_instance(
        self,
        instance_type,
        key_pair_name,
        image_id,
        security_group_id,
        instance_name,
        iam_instance_profile_arn=None,
        user_data=None
    ):
        if instance_type not in ["t2.nano", "t2.micro", "t2.small"]:
            instance_type = 't2.micro'
            #            Ubuntu Server 22.04 LTS     Ubuntu Server 20.04 LTS   Amazon Linux 2023 AMI
        if image_id not in ["ami-053b0d53c279acc90", "ami-0261755bbcb8c4a84", "ami-05548f9cecf47b442"]:
            image_id = "ami-053b0d53c279acc90"
        # Prepare the EC2 instance creation parameters
        instance_params = {
            'ImageId': image_id,
            'InstanceType': instance_type,
            'KeyName': key_pair_name,
            'SecurityGroupIds': [security_group_id],
            'MinCount': 1,
            'MaxCount': 1,
            'TagSpecifications': [
                {
                    'ResourceType': 'instance',
                    'Tags': [{'Key': 'Name', 'Value': instance_name}]
                }
            ]
        }

        # Add optional parameters if provided
        if iam_instance_profile_arn:
            instance_params['IamInstanceProfile'] = {
                'Arn': iam_instance_profile_arn}
        if user_data:
            instance_params['UserData'] = user_data

        # Launch EC2 instance
        response = self.ec2_client.run_instances(**instance_params)

        res_instance_id = response['Instances'][0]['InstanceId']
        res_image_id = response['Instances'][0]['ImageId']
        res_instance_type = response['Instances'][0]['InstanceType']
        res_availability_zone = response['Instances'][0]['Placement']['AvailabilityZone']
        res_instance_name_tag = response['Instances'][0]['Tags'][0]['Value']

        res = {
            "instance_id": res_instance_id,
            "instance_image_id": res_image_id,
            "instance_type": res_instance_type,
            "instance_availability_zone": res_availability_zone,
            "instance_name": res_instance_name_tag,
        }

        print(res)
        return res


# if __name__ == "__main__":
#     def main():
#         region_name = 'us-east-1'
#         instance_type = "t2.micro"
#         key_pair_name = "jenkins-controller"
#         image_id = "ami-053b0d53c279acc90"
#         security_group_id = "sg-0c71e220b685cc3c4"
#         instance_name = "boto3ec2"

#         # Optional Parameters
#         # iam_instance_profile_arn = 'arn:aws:iam::504406221982:instance-profile/EC2-Policy-FullAccess'
#         iam_instance_profile_arn = None
#         user_data = 'sudo apt update && sudo apt install -y curl dirmngr gnupg apt-transport-https lsb-release ca-certificates && curl -sL https://deb.nodesource.com/setup_lts.x | sudo -E bash - && sudo apt install -y nodejs && node -v && npm -v'

#         ec2_manager = EC2Manager(region_name)
#         result = ec2_manager.create_ec2_instance(instance_type, key_pair_name, image_id, security_group_id,
#                                                 instance_name, iam_instance_profile_arn, user_data)
#     main()
