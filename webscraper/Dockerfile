# Use an official Python runtime as a parent image
FROM python:3.12.3-slim

# Set the working directory in the container
WORKDIR /app

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

# Install any needed dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Run the Python script when the container launches
CMD ["python", "main.py"]
