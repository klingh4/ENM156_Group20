## Running the CLI ROC simulator (not compatible with later ship simulator versions anymore)

### How to set up the Docker image

```cd ship_simulator_zenoh_extras```
```docker build -t riseship . (might take a while)```

### How to run the Docker image

```docker run -it riseship```

### How to connect a second terminal to the running Docker container

```docker ps # note the Container ID```
```docker exec -it <container ID> /bin/sh```

### How to run multiple Docker containers

```docker run -it --network=host <image> # In one terminal```
```docker run -it --network=host <image> # In another terminal```

