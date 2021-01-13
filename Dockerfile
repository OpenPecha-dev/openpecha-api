FROM tiangolo/uvicorn-gunicorn:python3.8

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install python dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

# Copy environment variables
COPY ./.env /app/.env

EXPOSE 80

# add app
COPY ./app /app/app
