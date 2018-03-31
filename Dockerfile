FROM openmatchmaking/docker-base-python-image:3.6

COPY requirements.txt /requirements.txt
RUN pip install -r requirements.txt

COPY strategist /app
WORKDIR /app
