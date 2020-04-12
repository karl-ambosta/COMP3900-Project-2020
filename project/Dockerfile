# Use the official image as a parent image.
FROM python:3

# updates
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory.
WORKDIR /usr/src/app

# Copy requirements across
COPY requirements.txt ./

# Run the command inside your image filesystem.
RUN pip install --no-cache-dir -r requirements.txt

# copy all the files to the container
COPY . .

# Inform Docker that the container is listening on the specified port at runtime.
EXPOSE 8000

# Run the command
CMD [ "python", "./waiter/manage.py", "runserver", "0.0.0.0:8000" ]
