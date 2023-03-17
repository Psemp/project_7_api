FROM ubuntu:latest

# Install system packages
RUN apt-get update && apt-get -y upgrade && \
    apt-get -y install python3 python3-pip python3-dev postgresql postgresql-contrib nginx git \
    && apt-get clean

# Create and activate virtual environment
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN python3 -m pip install --upgrade pip setuptools wheel

# Set up Django app
RUN mkdir /app
WORKDIR /app
RUN git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git /app/
RUN pip install -r requirements.txt
RUN python3 manage.py collectstatic --noinput

COPY home_credit_api/api/data/ /app/home_credit_api/api/data/

# Load environment variables from .env file
RUN apt-get install -y python3 python3-pip
RUN python3 -m pip install python-dotenv
COPY .env /app/
RUN python3 -m dotenv /app/.env

# Set up Nginx
COPY nginx.conf /etc/nginx/sites-available/
RUN ln -s /etc/nginx/sites-available/nginx.conf /etc/nginx/sites-enabled/
RUN rm /etc/nginx/sites-enabled/default
RUN service nginx restart

# Set up Postgres, change credentials
USER postgres
RUN /etc/init.d/postgresql start &&\
    psql --command "CREATE USER myuser WITH PASSWORD '$DB_PASSWORD';" &&\
    createdb -O $DB_USER $DB_NAME

USER root

# Expose ports
EXPOSE 80
EXPOSE 8000

# Start Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "myapp.wsgi:application"]
