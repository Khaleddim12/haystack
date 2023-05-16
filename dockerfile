# pull official base image
FROM python:3.11-alpine

# Set up Django project directory
WORKDIR /django

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk update && apk add gcc python3-dev

# install python dependencies
RUN pip freeze > requirements.txt
COPY requirements.txt /django/requirements.txt

# Install packages
RUN pip install --upgrade pip
RUN pip install  -r /django/requirements.txt

# copy project
COPY . .

RUN python manage.py collectstatic --noinput
RUN python manage.py makemigrations
RUN python manage.py makemigrations rest_app

# run migrations at the end
CMD python manage.py migrate && python manage.py search_index --rebuild
COPY . .