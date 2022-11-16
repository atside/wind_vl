from python:alpine

copy requirements.txt /src/
workdir /src
run pip install -r requirements.txt
copy *.py /src/


cmd ["python", "main.py"]
