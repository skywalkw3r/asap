# Dockerfile

FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Collect static files (CSS, JS, images) into STATIC_ROOT
# Run this before migrate as migrate might need staticfiles if using static template tags in migrations (unlikely here)
RUN python manage.py collectstatic --noinput --clear

EXPOSE 8000

# Run migrations and then start Gunicorn
CMD python manage.py migrate --noinput && gunicorn --bind 0.0.0.0:8000 provisioning_portal.wsgi:application
