FROM python:3.10.6
# setup pip  environment
COPY ./requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

RUN pip install "arkitekt[cli]"==0.4.128
RUN mkdir /app 
COPY . /app
WORKDIR /app