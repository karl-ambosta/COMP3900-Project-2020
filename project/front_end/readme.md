# Getting Started
## Building docker image
```bash
$ docker build -t your-docker-repo/image_name .
$ docker push your-docker-repo/image_name`
```

# Running Locally
## Django Server
Ensure Django is running locally by navigating to `../waiter/` and following the readme instructions.

## Accessing locally without docker
Navigate to `public-html/` and launch `index.html` in Chrome or Firefox.

## Accessing locally via docker
```bash
$ docker run -dit --name my-app-name --rm -p 8080:80 your-docker-repo/image_name
```
Load using http://localhost:8080