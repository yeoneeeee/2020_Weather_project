FROM python:3.7
RUN apt-get update

RUN mkdir -p /usr/src/app
COPY run.sh /usr/src/app/run2.sh
WORKDIR /usr/src/app
COPY . ./
RUN chmod 755 ./run.sh
RUN pip install -r requirements.txt

EXPOSE 8000

CMD ./run.sh

