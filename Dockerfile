from python

copy *.py requirements.txt /src/
workdir /src
run pip install -r requirements.txt

cmd ["python", "main.py"]
