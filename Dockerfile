# Dockerfile

# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install dependencies
# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project code into the container
COPY . .

# ** Add this line to collect static files **
# It needs DJANGO_SECRET_KEY to run, but since it's just collecting files,
# a dummy value is acceptable if .env isn't copied yet or if you want to avoid reading it.
# However, copying .env before this is simpler for this stage.
# Ensure your .env file exists before building if you rely on it here.
# Alternatively, set a dummy SECRET_KEY env var just for this step if needed.
RUN python manage.py collectstatic --noinput --clear

# Expose port 8000 for the Django app
EXPOSE 8000

# Command to run the application using gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "provisioning_portal.wsgi:application"]