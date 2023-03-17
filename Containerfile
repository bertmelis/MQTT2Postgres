FROM python:3

RUN apt-get update && apt-get install -y nano

WORKDIR /app

ADD mqtt2postgres.py /app/
ADD messagehandler.py /app/
ADD postgres.py /app/
ADD regexmatcher.py /app/
ADD requirements.txt /app/

RUN pip install -r /app/requirements.txt

CMD [ "python", "/app/mqtt2postgres.py" ]
