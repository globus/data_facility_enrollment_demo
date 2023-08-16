FROM python:3.9

# Flip to 'production' for AWS deployments
ENV ENVIRONMENT=local 

ENV DJANGO_SETTINGS_MODULE=data_facility_enrollment_demo.settings
ENV PYTHONBUFFERED=1

RUN mkdir /srv/logs

RUN apt-get update \
    && apt-get install -y curl \
    && pip install --upgrade pip

COPY requirements.txt /
RUN pip install -r /requirements.txt

COPY ./entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r//' /entrypoint.sh \
    && chmod +x /entrypoint.sh

COPY . /app
WORKDIR /app

EXPOSE 8000
ENTRYPOINT ["/entrypoint.sh"]