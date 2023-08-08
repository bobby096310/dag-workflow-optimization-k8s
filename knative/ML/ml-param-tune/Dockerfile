FROM python:3.7

ENV PYTHONUNBUFFERED True

RUN apt-get update && apt-get install -y --no-install-recommends apt-utils
RUN apt-get -y install curl
RUN apt-get install libgomp1
RUN pip3 install tensorflow==2.4.0 keras==2.4.3 numpy==1.19.3 pillow==7.0.0 scipy==1.4.1 h5py==2.10.0 matplotlib==3.3.2 opencv-python keras-resnet==0.2.0 lightgbm parliament-functions==0.1.0 minio==7.1.13 Flask==2.2.3
RUN pip3 install gunicorn

COPY utils.py ./
COPY app.py   ./

CMD exec gunicorn --bind 0.0.0.0:8080 --workers 1 --threads 8 --timeout 0 app:app
