## Useful Commands
### Docker
See all running containers
```
docker ps
```

See all docker images on this device:
```
docker images
```


## How to build and run the api in a Docker container
To build the docker container first (cd /server/backend):
```
docker build -t api .
```

Then, to run in detached mode:
```
docker run --name api -d \
    -p 8000:8000 \
    -v /home/erichan/media:/media \
    -v /home/erichan/auth:/auth \
    api
```
To stop the container after it was launched in detached mode:
```
docker stop api
```

Or to run in the foreground:
```
docker run --name api -p 8000:8000 api
```

If a container is stopped, you will need to remove it to launch a new container with the same name:
```
sudo docker rm api
```

### Bind Mount for simple file access
The bind mount maps files from the host machine, allowing containers to read/write to them from within the container. This command must be run every time the container is restarted.
This is achieved with the -v flag when starting the container. Two drives are currently mounted: /media, and /auth.
Once the container is stopped and removed, the mount is no longer in use.