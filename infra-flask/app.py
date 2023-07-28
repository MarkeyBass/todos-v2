# pip install (flask, flask_sqlalchemy, flask_migrate)
# flask db init (create dir instance and db migrations)
# flask db migrate -m "profile creation" (create The instance of the database)
# flask db upgrade
# flask db migrate -m "profile add picture" (create The instance of the database)
# flask db upgrade
from utils.jenkins_utils import create_jenkins_job, create_jenkins_user, get_jenkins_job_last_build_info, run_jenkins_job
from utils.ec2_utils import EC2Manager
from utils.iam_utils import IamManager
from flask import Flask, render_template, request
import jenkins
import json
import re


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/jenkins_job', methods=['POST', 'GET'])
def jenkins_job():
    error = None

    if request.method == 'POST':
        job_name = request.form.get('job_name')
        job_describtion = request.form.get('job_describtion')
        job_commands = request.form.get('job_commands')
        job_commands_list = [command.strip() for command in re.split(r'\r\n|\n', job_commands) if command.strip()]

        try:
            res = create_jenkins_job(job_name, job_describtion, job_commands_list)
    
        except jenkins.JenkinsException as err:
            error = str(err)
            res = None
    else:
        # Set default values or handle the case when the form is not submitted
        job_name = ''
        job_describtion = ''
        job_commands = ''
        res = None

    return render_template(
        'jenkins_job.html',
        job_name=job_name,
        job_describtion=job_describtion,
        job_commands=job_commands,
        res=json.dumps(res, indent=4) if res else None,
        error=error
    )

@app.route('/jenkins_user', methods=['POST', 'GET'])
def jenkins_user():
    success = None
    message = None
    statusCode = None

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')

        res = create_jenkins_user(username, password, role)
        success = res['success']
        message = res['message']
        statusCode = res.get('statusCode')
        print(res)
    else:
        username = ''
        password = ''
        success = None
        message = None
        statusCode = None

    return render_template('jenkins_user.html', success=success, message=message, statusCode=statusCode)

@app.route('/jenkins_todos_app', methods=['POST', 'GET'])
def jenkins_todos_app():
    
    TEST_AND_PROD_JOB = 'todos-test-and-deploy-2'
    PROD_JOB = 'todos-deploy-to-prod'
    
    success = None
    message = None


    test_and_prod_last_build = get_jenkins_job_last_build_info(TEST_AND_PROD_JOB)  or { 'number': 0 }
    prod_last_build = get_jenkins_job_last_build_info(PROD_JOB) or { 'number': 0 }

    if request.method == 'POST':
        job_option = request.form.get('job-option')
        print(job_option)



        job_to_build = TEST_AND_PROD_JOB if job_option == "TEST_PROD_BOTH"  else PROD_JOB
        job_params = None if job_option == "TEST_PROD_BOTH" else {'Key': job_option}

        res = run_jenkins_job(job_to_build, job_params)
        success = res['success'] 
        message = res['message'] 
        job_url = res['job_url'] 
        print(res)
    else:
        job_option = ''
        success = None
        message = None
        job_url = None
        

    return render_template('jenkins_todos_app.html', 
                           success=success, message=message,
                           test_and_prod_last_build=test_and_prod_last_build, prod_last_build=prod_last_build,
                           job_url=job_url)

@app.route('/ec2', methods=['GET', 'POST'])
def create_ec2_instance():
    error = None
    res_instance_name = "" 
    res_instance_id = ""
    res_image_id = "" 
    res_instance_availability_zone = ""
    res_instance_type = ""

    if request.method == 'POST':
        region_name = "us-east-1"
        security_group_id = "sg-0c71e220b685cc3c4"
        key_pair_name = "jenkins-controller"
        iam_instance_profile_arn = None
        user_data = None

        instance_name = request.form.get('instance_name')
        instance_type = request.form.get('instance_type')
        image_id = request.form.get('image_id')

        ec2_manager = EC2Manager(region_name)

        try:
            res = ec2_manager.create_ec2_instance(instance_type, key_pair_name, image_id, security_group_id,
                                 instance_name, iam_instance_profile_arn, user_data)
            
            res_instance_name = res["instance_name"]
            res_instance_id = res["instance_id"]
            res_image_id = res["instance_image_id"]
            res_instance_availability_zone = res["instance_availability_zone"]
            res_instance_type = res["instance_type"]
        
        except Exception as err:
            print(err)
            error=err


    return render_template(
        'ec2.html', 
        instance_name=res_instance_name, 
        instance_id=res_instance_id,
        image_id=res_image_id, 
        instance_type=res_instance_type, 
        instance_availability_zone=res_instance_availability_zone,
        error=error
        )

@app.route('/iam_user', methods=['GET', 'POST'])
def iam():
    res_username = None
    user_group = None
    login_link = None
    access_key_id = None
    secret_access_key = None
    error = None
    error_2 = None

    if request.method == 'POST':
        usename = request.form['username']
        password = request.form['password']
        user_group = request.form['user_group']

        try:
            iam_manager = IamManager()
            res = iam_manager.create_iam_user(usename, password, user_group)
        
            res_username = res["res_username"]
            login_link = res["login_link"]
            access_key_id = res["access_key_id"]
            secret_access_key = res["secret_access_key"]
            error = res["error"]
            error_2 = res["error_2"]

        except Exception as err:
            error = str(err)
    
    return render_template(
        'iam_user.html', 
        res_username=res_username, 
        user_group=user_group, 
        login_link=login_link, 
        access_key_id=access_key_id, 
        secret_access_key=secret_access_key, 
        error=error,
        error_2=error_2
        )



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
