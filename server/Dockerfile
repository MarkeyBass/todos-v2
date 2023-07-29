FROM python:3.9 

WORKDIR /app

EXPOSE 5000

RUN pip install --upgrade pip

COPY docker-requirements.txt .

# RUN pip install --no-cache-dir -r docker-requirements.txt

RUN pip install --no-cache-dir -r docker-requirements.txt --index-url=https://pypi.org/simple/

RUN pip install prometheus_flask_exporter

COPY . ./

CMD ["python", "app.py"]
