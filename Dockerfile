from python

copy *.py *.txt /src/
workdir /src
run pip install -r requirements.txt

cmd ["python", "main.py"]
