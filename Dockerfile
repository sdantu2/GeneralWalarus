FROM python:3 
WORKDIR /usr/src/app

ENV CMD_PREFIX=!
ENV ENV_NAME=production

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get -y install ffmpeg

COPY . .

CMD [ "python", "./run.py" ]