import re
import boto3
from botocore.exceptions import BotoCoreError, ClientError, EndpointConnectionError, NoCredentialsError


class IamManager:
    def __init__(self):
        self.iam_client = boto3.client('iam')

    def create_iam_user(self, username: str, initial_pass: str, user_group: str) -> object:
        if user_group not in ["read-only", "devops", "SabiesGroup"]:
            user_group = "read-only"
        
        error = None
        error_2 = None
        link = None
        access_key_id = None
        res_create_access_key = None
        secret_access_key = None
        res_create_user = None
        res_add_to_group = None
        res_create_access_key = None

        try: 
            # create user
            res_create_user = self.iam_client.create_user(UserName=username)

            # Add user to group
            res_add_to_group = self.iam_client.add_user_to_group(
                GroupName=user_group,
                UserName=username
            )
            res_create_login_profile = self.iam_client.create_login_profile(
                UserName=username,
                Password=initial_pass,
                PasswordResetRequired=True
            )
            res_create_access_key = self.iam_client.create_access_key(
                UserName=username
            )
            access_key_id = res_create_access_key['AccessKey']['AccessKeyId'] if res_create_access_key and res_create_access_key.get('AccessKey') else None
            secret_access_key = res_create_access_key['AccessKey']['SecretAccessKey'] if res_create_access_key and res_create_access_key.get('AccessKey') else None
           
            link = None
            if res_create_user and res_create_user.get("User"): 
                link = "https://"+re.match(r'arn:aws:iam::(\d+):',res_create_user['User']['Arn']).group(1)+".signin.aws.amazon.com/console"
            

            print(link)  # generate the link automatically
        except (BotoCoreError, ClientError, EndpointConnectionError, NoCredentialsError, Exception) as err:
            # An error occurred, perform rollback

            # Remove user from group
            if res_add_to_group:
                try:
                    self.iam_client.remove_user_from_group(
                        GroupName=user_group,
                        UserName=username
                    )
                except (BotoCoreError, ClientError, EndpointConnectionError, NoCredentialsError, Exception) as rollback_err:
                    # Handle rollback error (optional)
                    error_2 = rollback_err

            # Delete any access keys that were created
            if res_create_access_key and access_key_id:
                try:
                    self.iam_client.delete_access_key(
                        UserName=username,
                        AccessKeyId=access_key_id
                    )
                except (BotoCoreError, ClientError, EndpointConnectionError, NoCredentialsError, Exception) as rollback_err:
                    # Handle rollback error (optional)
                    error_2 = rollback_err

            # Delete IAM user
            if res_create_user and res_create_user.get("User"):
                try:
                    self.iam_client.delete_user(UserName=username)
                    res_create_user = None
                except (BotoCoreError, ClientError, EndpointConnectionError, NoCredentialsError, Exception) as rollback_err:
                    # Handle rollback error (optional)
                    error_2 = rollback_err


            error = err

            # link = None
            # access_key_id = None
            # res_create_access_key = None
            # secret_access_key = None
            # res_create_user = None
            # res_add_to_group = None
            # res_create_access_key = None


        return {
            "res_username": res_create_user["User"]["UserName"] if res_create_user and res_create_user.get("User") else None, 
            "login_link": link,
            "access_key_id": access_key_id,
            "secret_access_key": secret_access_key,
            "error": error,
            "error_2": error_2
        }
    
if __name__ == "__main__":
    def main():
        iam_manager = IamManager()
        result = iam_manager.create_iam_user("koko-1", "Password@1234", "read-only")
    main()