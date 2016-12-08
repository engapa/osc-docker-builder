[![Code Issues](https://www.quantifiedcode.com/api/v1/project/1a96eb463beb4512a203762481b0c1ab/badge.svg)](https://www.quantifiedcode.com/app/project/1a96eb463beb4512a203762481b0c1ab)
# Docker image builder for Openstack clients (aka OSCs docker builder)

A lot of people need install/update/upgrade/downgrade any Openstack python client in any time.
Within Docker containers is easy to get an isolated environment with all Openstack clients that you wish, for a specific release from upstream .

## Pre-requisites

Openstack python clients project should have following prerequisites :

- docker image: Ensure that there is an official python docker image for provided python version parameter.
- tox : All clients are using tox, and python version parameter will be matched in env list.
- common release: All clients have to have same release, in other case you must specify different release for a client by property 'release' in the osc.yml file to override global release parameter. For example, in the osc.yml you can see that client gnocchi has 'master' release instead of 'stable/newton'

## Build a docker image with OSCs

Ready for action ?, suppose that you want to create a docker image for these python version and Openstack clients:

```
osc.py --python-version 3.4 --clients openstack --clients heat --release stable/newton
```

I recommend you to use a config file (which you could watch under version control system):

```
osc.py -f osc.yml
```

As command execution output we have a docker image ready to be used.
Push your images to your private registry or use my images at <code>engapa</code> account in dockerhub.com

## Run docker container

For example, run a container based on latest image for python client 3.4 and release stable/newton :
```
$ docker run -it -d --name osc engapa/ocs:2.7-stable_newton-latest /bin/bash
1f395d7273b99b734725fcbab4ebd05082f21978e0c4e3104cc8332c7430920d
$ docker ps
CONTAINER ID   IMAGE                               COMMAND     CREATED        STATUS       PORTS  NAMES
1f395d7273b9   engapa/ocs:2.7-stable_newton-latest "/bin/bash" 2 seconds ago  Up 3 seconds        osc
```

Let's see , for example the version of the Heat client in this container:

```
$ docker exec -it 1f395d7273b9 /bin/bash -c "heat --version"
1.5.0
```

If you prefer operate into the container :

```
$ docker exec -it 1f395d7273b9 /bin/bash
root@1f395d7273b9:/# root@1f395d7273b9:/# pip list --format columns | grep -i "^python-.*client"
python-heatclient   1.5.0
python-magnumclient 2.3.2.dev3
python-swiftclient  3.2.0
...
root@1f395d7273b9:/#
```


## Author

Enrique Garcia Pablos <engapa@gmail.com>