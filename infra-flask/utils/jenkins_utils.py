# pip install python-jenkins
# pip install beautifulsoup4

import time

import jenkins
import requests
from typing import List
from requests.auth import HTTPBasicAuth
from bs4 import BeautifulSoup
import subprocess
import os
import json

INFRA_FLASK_JENKINS_TOKEN = '11c8364eadd295889aa944b35f29a1140b'
JENKINS_URL = "http://52.207.130.141:8080/"
JENKINS_ADMIN_USERNAME = 'python-user'
JENKINS_ADMIN_PASSWORD = "123456"

possible_roles = {
    "READ_ONLY": 'read-only', 
    "READ_AND_BUILD": 'read-and-build', 
    "READ_BUILD_CREATE": 'read-build-create'
}

jenkins_client = jenkins.Jenkins(
    JENKINS_URL, username=JENKINS_ADMIN_USERNAME, password=JENKINS_ADMIN_PASSWORD, timeout=10)


def create_jenkins_job(job_name: str, job_description: str, job_commands: List[str]):

    # XML configuration of the python - jenkins job
    commands_xml = '\n'.join(
        [f'<hudson.tasks.Shell>\n<command>{command}</command>\n</hudson.tasks.Shell>' for command in job_commands])

    config = f"""
  <project>
      <actions/>
      <description>{job_description}</description>
      <keepDependencies>false</keepDependencies>
      <properties/>
      <scm class="hudson.scm.NullSCM"/>
      <canRoam>true</canRoam>
      <disabled>false</disabled>
      <triggers/>
      <concurrentBuild>false</concurrentBuild>
      <builders>
          {commands_xml}
      </builders>
      <publishers/>
  </project>
  """

    jenkins_client.create_job(job_name, config)
    create_info = jenkins_client.get_job_info(job_name)
    return create_info


def get_jenkins_job_last_build_info(job_name):
    job_info = jenkins_client.get_job_info(job_name)
    return job_info['lastCompletedBuild']
    


def run_jenkins_job(job_name, parameters=None):
   
    try:
        jenkins_client.get_whoami()
        jenkins_client.get_version()
    except Exception as err:
        return {'message': f"Error connecting to Jenkins: {str(err)}", 'success': False}, 

    try:
        job_start_log = jenkins_client.build_job(job_name, parameters=None)
        print("===== START LOG =====", job_start_log, "has job started",type(job_start_log) == int)
        if not isinstance(job_start_log, int):
            raise TypeError("The job starting log returned an unexpected value type")
        job_info = jenkins_client.get_job_info(job_name)

        job_path = job_info['url'].split('/')[3] + '/' + job_info['url'].split('/')[4]
        job_url = JENKINS_URL + job_path

        print('===== job_url =====', job_url)


        return {
            'message': f'Job nomber {job_info["lastCompletedBuild"]["number"] + 1} have started successfully. \nplease check the link for more info {job_info["url"]}', 
            'job_url': job_url,
            'success': True 
        }
    except TypeError as err:
        return {'message': f"Error - Job Failed to start: {str(err)}", 'success': False}


def create_jenkins_user(username: str, password: str, role: str = None):
    create_user_url = f"{JENKINS_URL}securityRealm/createAccountByAdmin"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Bearer {INFRA_FLASK_JENKINS_TOKEN}"
    }
    data = {
        "username": username,
        "password1": password,
        "password2": password,
        "fullname": username,
        "email": f"{username}@example.com",
        "jenkins.security.ApiTokenProperty": True
    }

    response = requests.post(create_user_url, headers=headers, data=data, auth=HTTPBasicAuth(
        JENKINS_ADMIN_USERNAME, INFRA_FLASK_JENKINS_TOKEN))

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        error_div = soup.find('div', class_='error')
        if error_div:
            error_message = error_div.text.strip()
            print(f"Error creating user '{username}': {error_message}")
            return {
                "success": False,
                "message": f"Error creating user '{username}': {error_message}"
            }
        else:
            print(f"User '{username}' created successfully.")
            print("Status Code:", response.status_code)
            message = f"User '{username}' created successfully."

            role_created_res = jenkins_user_assign_roles(username, role)

            if role_created_res["success"] == True:
                message = message + '\n' + role_created_res["message"]
            else:
                message = message + '\n + User {username} was created without privilages'

            print({
                "success": True,
                "message": message,
                "statusCode:": response.status_code
            })

            return {
                "success": True,
                "message": message,
                "statusCode:": response.status_code
            }
    else:
        print(f"Error creating user '{username}': {response.text}")
        print("Status Code:", response.status_code)
        print("Headers:", response.headers)
        return {
            "success": False,
            "message": f"Error creating user '{username}': {response.text}",
            "statusCode:": response.status_code
        }


def jenkins_user_assign_roles(username: str, role: str):

    possible_roles_list = [
        possible_roles["READ_ONLY"], 
        possible_roles["READ_AND_BUILD"], 
        possible_roles["READ_BUILD_CREATE"]
    ]
    
    new_role = role if role in possible_roles_list else 'read-only'

    assign_role_url = f"{JENKINS_URL}role-strategy/strategy/assignRole"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Bearer {INFRA_FLASK_JENKINS_TOKEN}"
    }
    data = {
        "type": "globalRoles",
        "roleName": new_role,
        "sid": username
    }

    response = requests.post(assign_role_url, headers=headers, data=data, auth=HTTPBasicAuth(
        JENKINS_ADMIN_USERNAME, INFRA_FLASK_JENKINS_TOKEN))

    if response.status_code == 200:
        return {
            "success": True,
            "message": f"Role '{new_role}' assigned to user '{username}' successfully.",
            "statusCode": response.status_code
        }
    else:
        return {
            "success": False,
            "message": f"Error assigning role '{new_role}' to user '{username}': {response.text}",
            "statusCode": response.status_code
        }


def get_jenkins_users():
    users_url = f"{JENKINS_URL}/asynchPeople/api/json"
    headers = {
        "Content-Type": "application/json"
    }
    auth = HTTPBasicAuth(JENKINS_ADMIN_USERNAME, JENKINS_ADMIN_PASSWORD)

    response = requests.get(users_url, headers=headers, auth=auth)

    if response.status_code == 200:
        users = response.json()
        print(users)
        return users
    else:
        print(response.text)
        return None




if __name__ == "__main__":
    # run_jenkins_job('todos-deploy-to-prod')
    run_jenkins_job('pyhon_test_job_1')
    # get_jenkins_job_last_build_info('pyhon_test_job')
    # run_jenkins_job('todos-test-and-deploy-2')
    # run_jenkins_job('todos-deploy-to-prod')
    #     jenkins_user_assign_roles('new_user_7')
    # create_user('new_user_15', '123456', 'read-build-create')
    # create_jenkins_user('new_user_16', '123456', 'read-build-createjhksfdjukhsdf')
    # create_jenkins_job("python-test-1", "bla bla", ["echo Hello world"])
    # create_jenkins_job("python-test-1", "bla bla", ["echo Hello world", "pwd", "ls -la"])
    # jenkins_user_assign_roles('new_user_7')
    # get_jenkins_users()