[![Code Issues](https://www.quantifiedcode.com/api/v1/project/1a96eb463beb4512a203762481b0c1ab/badge.svg)](https://www.quantifiedcode.com/app/project/1a96eb463beb4512a203762481b0c1ab)
# Docker image builder for Openstack clients (aka OSCs docker builder)

A lot of people need install/update/upgrade/downgrade any Openstack python client in any time.
Within Docker containers is easy to get an isolated environment with all Openstack clients that you wish, for a specific release from upstream .

## Build a docker image with OSCs

For example, suppose that you want to create a docker image for these python version and Openstack clients:

```
osc.py --python-version 2.7 --clients magnum --clients heat
```

I recommend you to use a config file (which you could watch under version control system):

```
osc.py -f osc.yml
```

As command execution output we have a docker image ready to be used.

## Run docker container

```
$ docker run -d engapa/oscs:<python_version>-<release>-<latest> oscs
```

Now , use your env variable to launch the client ...:

```
$ docker exec -it <docker_id> /bin/bash
root@<docker_id>:/# nova list
```

(Use : os-client-config to define clouds)

## Author

Enrique Garcia Pablos <engapa@gmail.com>