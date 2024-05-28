# Python runtime parent image
FROM python:3.12.3-slim

# Set the working directory in the container
WORKDIR /app

# Copy only requirements.txt contents into the container at /app to use to for pip next step. Build cache optimization.
COPY requirements.txt /app

# Install any needed dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && \
    apt-get install -y curl

# Install ODBC driver dependencies
RUN apt-get update && \
    apt-get install -y unixodbc unixodbc-dev && \
    apt-get clean

# Install ODBC driver for SQL Server
RUN apt-get update && \
    apt-get install -y curl gnupg && \
    curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql17 && \
    apt-get clean

# Set environment variables for ODBC driver
ENV ODBCINI /etc/odbc.ini
ENV ODBCSYSINI /etc

# Copy the current directory contents into the container at /app
COPY . /app

# Expose the port the app runs on
EXPOSE 3001

# Define environment variable
ENV FLASK_APP app.py

# Run the application
CMD ["python", "app.py"]