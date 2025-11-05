FROM python:3.14.0-alpine3.21

EXPOSE 5000

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY app.py .

CMD [ "python", "app.py" ]
