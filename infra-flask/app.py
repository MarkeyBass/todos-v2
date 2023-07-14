# pip install (flask, flask_sqlalchemy, flask_migrate)
# flask db init (create dir instance and db migrations)
# flask db migrate -m "profile creation" (create The instance of the database)
# flask db upgrade
# flask db migrate -m "profile add picture" (create The instance of the database)
# flask db upgrade
from utils.jenkins_utils import create_jenkins_job, create_jenkins_user
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



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
