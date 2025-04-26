# Create the project directory
mkdir provisioning_portal
cd provisioning_portal

# Create a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows use `.\venv\Scripts\activate`

# Install Django and requests
pip install django requests python-dotenv

# Create the Django project
django-admin startproject provisioning_portal .

# Create the Django app
python manage.py startapp requests_app

# Create templates directory
mkdir -p requests_app/templates/requests_app

# Create requirements.txt in the project root:
Django>=4.0,<5.0
requests>=2.20.0
python-dotenv>=0.19.0