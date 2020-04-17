# Getting Started
## Building docker image
`$ docker build -t your-docker-repo/image_name .`
`$ docker push your-docker-repo/image_name`

## Running image locally
`$ docker run -dit --name my-app-name --rm -p 8080:80 your-docker-repo/image_name`
