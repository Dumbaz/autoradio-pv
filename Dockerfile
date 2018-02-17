FROM python:3

COPY . /tmp/
RUN chmod +x /tmp/entrypoint.sh

RUN pip install --no-cache-dir -r /tmp/requirements.txt

RUN python /tmp/manage.py migrate
ENTRYPOINT ["/tmp/entrypoint.sh"]

# Superuser parameters are --username USERNAME and --email EMAIL but there is no password
# RUN python /tmp/manage.py createsuperuser
