FROM python:3.10-slim

RUN mkdir /starnavi

COPY /dist/strarnavi-0.0.1.tar.gz /starnavi/

RUN pip3 install /starnavi/strarnavi-0.0.1.tar.gz

COPY starnavi/ /starnavi/

WORKDIR /starnavi/

CMD ["python3", "main.py"]
