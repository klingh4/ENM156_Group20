== Group 20 project repository ==

This repository contains code related to ROC and ship simulation.

=== How to set up the submodule ===

Run the following commands in a terminal:
  cd ship_simulator_zenoh
  git submodule init
  cd ..
  git submodule update --remote

=== How to set up the Docker image ===

  cd ship_simulator_zenoh_extras
  docker build -t riseship . (might take a while)

=== How to run the Docker image ===

  docker run -it riseship

=== How to connect a second terminal to the running Docker container ===

  docker ps # note the Container ID
  docker exec -it <container ID> /bin/sh

=== How to run multiple Docker containers ===

  docker run -it --network=host <image> # In one terminal
  docker run -it --network=host <image> # In another terminal

=== Running the python-tkinter gui ===

You need to have tk support installed on your machine (for example by installing your distribution's
tk package).

You also need to have the tkintermapview python package, which can be installed via pip.

TODO: Make dependencies portable somehow.
