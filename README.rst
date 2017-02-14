Docker image builder for Openstack clients (aka OSCs docker builder)
====================================================================

|Latest Version| |Downloads| |Code Issues| |codecov| |CircleCI|

A lot of people need install/update/upgrade/downgrade any Openstack
python client in any time. Thanks to Docker containers it is easy to get
an isolated environment with all Openstack clients of specific upstream
versions that you wish.

Pre-requisites
==============

List of prerequisites :

-  docker image: Ensure that there is an official python docker image
   for the provided python version parameter.
-  tox : All clients are using tox, and python version parameter will be
   matched in env list.
-  common release: All clients have to have the same release, in other
   cases you must specify a different release (by property 'release' in
   the osc.yml file) to override global release parameter. For example,
   in the osc.yml you may see that gnocchi client has 'master' release
   instead of 'stable/newton'.

Build a docker image with OSCs
==============================

This module can be installed by pip:

::

    $ pip install osc-docker-builder

Best way to get help about the command is :

::

    osc-builder --help
    usage: ocs [-h] [-bp BUILD_PATH] [-f CONFIG_FILE] [-pv PYTHON_VERSION]
               [-r RELEASE] [-c CLIENTS] [-sf] [-v]

    Build a docker image with all Openstack clients that you want for a specific
    upstream branch and python version

    optional arguments:
      -h, --help            show this help message and exit
      -bp BUILD_PATH, --build-path BUILD_PATH
                            The build path where files are written.
      -f CONFIG_FILE, --config-file CONFIG_FILE
                            A YAML config file.
      -pv PYTHON_VERSION, --python-version PYTHON_VERSION
                            Python version for docker image
                            base(https://hub.docker.com/_/python/).For example :
                            2.7, 3.5.2
      -r RELEASE, --release RELEASE
                            Upstream release.
      -c CLIENTS, --clients CLIENTS
                            Provide all openstack python clients that you want.By
                            defaults only python-openstackclient will be
                            installed.
      -sf, --skip-fails     Skip failures and create the image.
      -v, --verbose         Show details.

Ready for action ?, suppose that you want to create a docker image for
these python version and Openstack clients:

::

    osc-builder --python-version 3.4 --clients openstack --clients heat --release stable/newton --build-path /tmp/osc-docker-builder

I recommend using a config file (which could be controlled by a version
control system):

::

    osc-builder -f osc.yml

This command can be launched form the source code. The main function
will be found in osc\_docker\_builder package :

::

    $ osc.py -f osc.yml -bp /tmp/osc-builder

As command execution output we have a docker image ready to be used.
Push your images to your private registry or use my images at "engapa"
account in dockerhub.com

Running and using docker container
==================================

For example, run a container based on latest image for python client 2.7
and release stable/newton :

::

    $ docker run -it -d --name osc engapa/osc:2.7-stable_newton-latest
    1f395d7273b99b734725fcbab4ebd05082f21978e0c4e3104cc8332c7430920d
    $ docker ps
    CONTAINER ID   IMAGE                               COMMAND     CREATED        STATUS       PORTS  NAMES
    1f395d7273b9   engapa/osc:2.7-stable_newton-latest "/bin/bash" 2 seconds ago  Up 3 seconds        osc

For example let's view the version of the Heat client installed in this
container:

::

    $ docker exec -it 1f395d7273b9 /bin/bash -c "heat --version"
    1.5.0

If you prefer operate within the container :

::

    $ docker attach 1f395d7273b9
    root@1f395d7273b9:# pip list --format columns | grep -i "^python-.*client"
    python-openstackclient         3.2.1.dev10 /src/python-openstackclient
    python-saharaclient            0.18.1.dev1 /src/python-saharaclient
    python-searchlightclient       1.0.1.dev1  /src/python-searchlightclient
    python-senlinclient            1.0.1.dev14 /src/python-senlinclient
    python-solumclient             2.1.2.dev2  /src/python-solumclient
    python-swiftclient             3.1.1.dev1  /src/python-swiftclient
    ...
    root@1f395d7273b9:/#

If you want to update all python client versions (if provided release
was a branch , e.g. : master) just execute this command within the
container:

::

    $ docker attach 1f395d7273b9
    root@1f395d7273b9:/root# pip install -U -r requirements.txt

An interesting module of openstack is 'os-client-config', it aims you to
use a cloud configuration file shared by volume mount point (at "/root",
"/root/.config/openstack" or "/etc/openstack" directory):

::

    $ cat << EOF > cloud.yml
    > clouds:
    >   spaincloud:
    >     auth:
    >       username: engapa
    >       password: XXXXXXXXX
    >       project_name: OSOOS
    >       auth_url: 'https://spaincloud.com:5001/v2.0'
    >     region_name: SpainSalamanca
    >     dns_api_version: 1
    > EOF
    $ docker run -it --name osc -v $(pwd)/clouds.yml:/root/.config/openstack/clouds.yml engapa/osc:2.7-stable_newton-latest
    root@1536ac361c6c:~# openstack --os-cloud spaincloud server list
    ...

Developer mode
==============

Main tasks with code are managed by
`tox <https://tox.readthedocs.io/en/latest/>`__

To launch tests just type:

::

    $ tox -r
    ...

    Name                        Stmts   Miss  Cover
    -----------------------------------------------
    osc_docker_builder.py           0      0   100%
    osc_docker_builder/osc.py     129    102    70%
    -----------------------------------------------
    TOTAL                         129    102    70%
    ----------------------------------------------------------------------
    Ran 5 tests in 0.097s

    OK
    ___________________________________________________________________________ summary ____________________________________________________________________________
      pep8: commands succeeded
      py27: commands succeeded
      py35: commands succeeded
      congratulations :)

Load the virtualenv and build a docker image :

::

    $ source .tox/py27/bin/activate
    $(py27) osc-builder -f osc.yml

Author
======

Enrique Garcia Pablos engapa@gmail.com

.. |Latest Version| image:: https://img.shields.io/pypi/v/osc-docker-builder.svg
   :target: https://pypi.python.org/pypi/osc-docker-builder/
.. |Downloads| image:: https://img.shields.io/pypi/dm/osc-docker-builder.svg
   :target: https://pypi.python.org/pypi/osc-docker-builder/
.. |Code Issues| image:: https://www.quantifiedcode.com/api/v1/project/1a96eb463beb4512a203762481b0c1ab/badge.svg
   :target: https://www.quantifiedcode.com/app/project/1a96eb463beb4512a203762481b0c1ab
.. |codecov| image:: https://codecov.io/gh/engapa/osc-docker-builder/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/engapa/osc-docker-builder
.. |CircleCI| image:: https://circleci.com/gh/engapa/osc-docker-builder/tree/master.svg?style=svg
   :target: https://circleci.com/gh/engapa/osc-docker-builder/tree/master