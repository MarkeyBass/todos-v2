# pip install (flask, flask_sqlalchemy, flask_migrate)
# flask db init (create dir instance and db migrations)
# flask db migrate -m "profile creation" (create The instance of the database)
# flask db upgrade
# flask db migrate -m "profile add picture" (create The instance of the database)
# flask db upgrade
from utils.jenkins_utils import create_jenkins_job, create_jenkins_user, get_jenkins_job_last_build_info, run_jenkins_job
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
        job_param = None if job_option == "TEST_PROD_BOTH" else job_option

        # res = run_jenkins_job(job_to_build, {'KEY': job_param})
        res = {'success': 'None', 'message': 'None', 'job_url': 'None'}
        success = res['success'] or "None" 
        message = res['message'] or "None" 
        job_url = res['job_url'] or "None" 
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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
