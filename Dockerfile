FROM python:3.11

RUN mkdir -p /usr/app
WORKDIR /usr/app

COPY . .

RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["python", "src/app.py"]
