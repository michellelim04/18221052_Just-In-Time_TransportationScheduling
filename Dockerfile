FROM python:3.10-alpine3.17

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . /app

CMD ["uvicorn", "driver:app", "--reload"]