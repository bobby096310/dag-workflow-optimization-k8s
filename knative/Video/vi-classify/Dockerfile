FROM python:3.7

RUN pip3 install tensorflow==2.4.0

RUN pip3 install keras==2.4.3 numpy==1.19.3 pillow==7.0.0 scipy==1.4.1 h5py==2.10.0 matplotlib==3.3.2 opencv-python keras-resnet==0.2.0 parliament-functions==0.1.0 minio==7.1.13 Flask==2.2.3

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

RUN pip3 install imageai==2.1.6

RUN mkdir -p ~/models
RUN mkdir -p ~/images
RUN mkdir -p ~/tmp_out

COPY models/yolo-tiny.h5 ~/models/yolo-tiny.h5
COPY images/* ~/images/

RUN pip3 install gunicorn

COPY utils.py ./
COPY func.py   ./

CMD exec gunicorn --bind 0.0.0.0:8080 --workers 1 --threads 8 --timeout 0 func:app
