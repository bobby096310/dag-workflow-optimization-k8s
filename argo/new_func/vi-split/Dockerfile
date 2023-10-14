FROM python:3.8

RUN mkdir -p ./var
COPY var/* ./var/
COPY utils.py ./
COPY func.py   ./
COPY requirements.txt ./

RUN pip3 install -r requirements.txt


