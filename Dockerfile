FROM python:3.10

WORKDIR /root

ADD requirements.txt ./

RUN pip3 install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--no-access-log", "--no-use-colors"]