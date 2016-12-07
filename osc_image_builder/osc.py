#!/usr/bin/python
# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Author : Enrique Garcia Pablos <engapa@gmail.com>
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import sys
import os
import shutil
import logging

if sys.version_info < (2, 7):
    sys.exit("This script requires Python 2.7 or newer!")


logger = logging.getLogger("OSC-docker")
logging.basicConfig()
logger.setLevel(logging.INFO)


def _clean_dir(basepath, remove=False, create=True):
    if os.path.exists(basepath):
        for filename in os.listdir(basepath):
            filepath = os.path.join(basepath, filename)
            try:
                shutil.rmtree(filepath)
            except OSError:
                os.remove(filepath)
        if remove:
            os.rmdir(basepath)

    elif create:
        os.makedirs(basepath)


def _parse_args():

    import argparse

    parser = argparse.ArgumentParser(
        prog="ocs",
        description="Build a docker image with all Openstack clients"
                    " that you want for a specific upstream branch and python version")
    parser.add_argument('-f', '--config-file', dest='config_file',
                        help='A YAML config file.')
    parser.add_argument('-pv', '--python-version', dest='python_version',
                        help='Python version. For example : 2.7, 3.4')
    parser.add_argument('-r', '--release', dest='release',
                        help='Upstream release.')
    parser.add_argument('-c', '--clients', dest='clients', action='append',
                        default=['openstack'],
                        help='Provide all openstack python client that you want.'
                             'By defaults only python-openstackclient will be installed.')
    parser.add_argument('-sf', '--skip-fails', dest='skip_fails', action='store_true',
                        help='Skip failures and create the image.')
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true',
                        help='Show details.')

    return parser.parse_args()


def _download_tox_module(basepath, release, client):

    import urllib

    url = "https://raw.githubusercontent.com/openstack/" \
          "python-%(client)sclient/%(release)s/tox.ini" % {'release': release, 'client': client}
    with open('%(basepath)s/%(client)s-tox.ini' % {'basepath': basepath, 'client': client}, 'wb') as output:
        output.write(urllib.urlopen(url).read())


def _check_client_pv(basepath, client, py_version):
    py_env = 'py'
    if '.' in py_version:
        py_env += py_version.replace('.', '')[0:2]
    else:
        py_env += py_version[0:2]

    import tox
    config = tox.session.prepare(
        [
            "-c%s/%s-tox.ini" % (basepath, client),
            "-l"
        ]
    )
    return py_env in config.envlist


def _render_dockerfile(basepath, python_version, release, clients):

    from jinja2 import Environment, FileSystemLoader

    template_dir = os.path.abspath('templates')
    env = Environment(loader=FileSystemLoader(searchpath=template_dir))
    template = env.get_template('Dockerfile.j2')
    with open(basepath + '/Dockerfile', 'wb') as dockerfile:
        dockerfile.write(
            template.render(
                python_version=python_version,
                release=release,
                clients=clients
            )
        )


def _build_docker_image(basepath, python_version, release):
    import subprocess
    tag = 'engapa/ocs:{}-{}-latest'.format(python_version, release.replace('/', '_'))
    subprocess.call(['docker', 'build', '-t', tag, basepath])


def main():

    args = _parse_args()

    if args.config_file:
        import yaml
        try:
            with open(args.config_file, 'r') as config_file:
                config = yaml.load(config_file)
            python_version = config.get('python_version')
            if python_version:
                python_version = str(python_version)
            release = config.get('release')
            skip_failures = config.get('skip-failures', False)
            debug = config.get('debug', False)
            clients = [x['name'] for x in config['clients']]
        except yaml.YAMLError as exc:
            logger.error('Unable to load configration from file: {} . Caused by : {}', config_file, exc)
            sys.exit(1)
        except Exception as e:
            logger.error(e)
            sys.exit(1)
    else:
        python_version = args.python_version
        release = args.release
        skip_failures = args.skip_failures
        debug = args.debug

    # Required values :
    assert python_version, 'Required python_version value'
    assert release, 'Required release value'
    assert clients, 'Required clients list'

    if debug:
        logger.setLevel(logging.DEBUG)

    basepath = "../build"

    _clean_dir(basepath)

    cclients = []

    for client in clients:
        try:
            _download_tox_module(basepath, release, client)
            if _check_client_pv(basepath, client, python_version):
                cclients.append(client)
            else:
                logger.error("Not found python env for {} client with version {}.", client, python_version)
        except Exception as e:
            logger.error(e)
            if not skip_failures:
                sys.exit(1)
    if cclients:
        _render_dockerfile(basepath, python_version, release, cclients)
        _build_docker_image(basepath, python_version, release)


if __name__ == "__main__":
    main()
