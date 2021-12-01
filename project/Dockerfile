FROM python:3.9.6-alpine

WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install psycopg2 dependencies
RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev libffi libffi-dev 

# install dependencies
ADD requirements.txt .
RUN pip install --upgrade pip -r requirements.txt

# copy entrypoint.sh
ADD ./entrypoint.sh .
RUN sed -i 's/\r$//g' /app/entrypoint.sh && chmod +x /app/entrypoint.sh

COPY . .

RUN python manage.py collectstatic --no-input

# run entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]