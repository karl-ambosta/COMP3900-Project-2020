# Getting Started
## Building docker image
```bash
$ docker build -t your-docker-repo/image_name .
$ docker push your-docker-repo/image_name`
```

# Running Django
## Running locally via terminal
```bash
$ python3 manage.py runserver
```

## Running locally via docker
```bash
$ docker run -dit --name my-app-name --rm -p 8000:8000 your-docker-repo/image_name
```
Load using http://localhost:8000
