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
import multiprocessing
import argparse
import urllib
import tox
import subprocess
import time

from jinja2 import Environment, FileSystemLoader


if sys.version_info < (2, 7):
    sys.exit("This script requires Python 2.7 or newer!")


logger = logging.getLogger("OSC-docker")
logging.basicConfig()
logger.setLevel(logging.INFO)

BASE_PATH = '../build'


def __clean_dir(remove=False, create=True):
    if os.path.exists(BASE_PATH):
        for filename in os.listdir(BASE_PATH):
            filepath = os.path.join(BASE_PATH, filename)
            try:
                shutil.rmtree(filepath)
            except OSError:
                os.remove(filepath)
        if remove:
            os.rmdir(BASE_PATH)

    elif create:
        os.makedirs(BASE_PATH)


def __parse_args():

    parser = argparse.ArgumentParser(
        prog="ocs",
        description="Build a docker image with all Openstack clients"
                    " that you want for a specific upstream branch and python version")
    parser.add_argument('-f', '--config-file', dest='config_file',
                        help='A YAML config file.')
    parser.add_argument('-pv', '--python-version', dest='python_version',
                        help='Python version for docker image base(https://hub.docker.com/_/python/).'
                             'For example : 2.7, 3.5.2')
    parser.add_argument('-r', '--release', dest='release',
                        help='Upstream release.')
    parser.add_argument('-c', '--clients', dest='clients', action='append',
                        help='Provide all openstack python clients that you want.'
                             'By defaults only python-openstackclient will be installed.')
    parser.add_argument('-sf', '--skip-fails', dest='skip_fails', action='store_true',
                        help='Skip failures and create the image.')
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true',
                        help='Show details.')

    return parser.parse_args()


def __download_docker_image_base(python_version):
    child = subprocess.Popen(['docker', 'pull', 'python:{}'.format(python_version)],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = child.communicate()
    logger.debug(output)
    if error and child.returncode != 0:
        logger.error(error)
        raise SystemExit(
            "Unavailable to download docker image for python version {}".format(python_version))


def __download_tox_module(client_url):

    client, url = client_url
    start_time = time.time()
    fname, info = urllib.urlretrieve(url,
                                     filename='{}/{}-tox.ini'.format(BASE_PATH, client))
    end_time = time.time()
    logger.debug(" Downloaded file : %s , size : %s bytes, time: %s",
                 fname, info.get('content-length'),  end_time - start_time)


def __check_client_pv(client, py_version, skip_fails):
    py_env = 'py'
    if '.' in py_version:
        py_env += py_version.replace('.', '')[0:2]
    else:
        py_env += py_version[0:2]

    config = tox.session.prepare(
        [
            "-c%s/%s-tox.ini" % (BASE_PATH, client),
            "-l"
        ]
    )
    found = py_env in config.envlist

    if not found:
        msg = "Not found venv {} for client {}".format(py_env, client)
        if not skip_fails:
            raise SystemExit(msg)
        else:
            logger.warning(msg)

    return found


def __render_templates(python_version, release, clients):

    template_dir = os.path.abspath('templates')
    env = Environment(loader=FileSystemLoader(searchpath=template_dir))
    with open(BASE_PATH + '/requirements.txt', 'wb') as requirements:
        logger.debug("Generating file requirements.txt")
        requirements.write(
            env.get_template('requirements.j2').render(
                release=release,
                clients=clients
            )
        )
    with open(BASE_PATH + '/Dockerfile', 'wb') as dockerfile:
        logger.debug("Generating file Dockerfile")
        dockerfile.write(
            env.get_template('Dockerfile.j2').render(
                python_version=python_version
            )
        )


def __build_docker_image(python_version, release):
    tag = 'engapa/ocs:{}-{}-latest'.format(python_version, release.replace('/', '_'))
    child = subprocess.Popen(['docker', 'build', '-t', tag, BASE_PATH], stdin=subprocess.PIPE)
    output, error = child.communicate()
    if error and child.returncode != 0:
        logger.error(error)
        raise SystemExit(
            "Unavailable to build docker image")


def main():

    args = __parse_args()

    if args.config_file:
        import yaml
        try:
            with open(args.config_file, 'r') as config_file:
                config = yaml.load(config_file)
            python_version = config.get('python_version')
            if python_version:
                python_version = str(python_version)
            release = config.get('release')
            skip_fails = config.get('skip-fails', False)
            verbose = config.get('verbose', False)
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
        skip_fails = args.skip_fails
        verbose = args.verbose
        clients = args.clients

    # Required values :
    assert python_version, 'Required python_version value'
    assert release, 'Required release value'
    assert clients, 'Required clients list'

    if verbose:
        logger.setLevel(logging.DEBUG)

    __clean_dir()

    __download_docker_image_base(python_version)

    cclients = []

    pool = multiprocessing.Pool()
    client_url_list = [
        (client, "https://raw.githubusercontent.com/openstack/python-{}client/{}/tox.ini".format(client, release))
        for client in clients
    ]
    pool.map(__download_tox_module, client_url_list)

    for client in clients:
        if __check_client_pv(client, python_version, skip_fails):
            cclients.append(client)

    if cclients:
        __render_templates(python_version, release, cclients)
        __build_docker_image(python_version, release)

if __name__ == "__main__":
    main()
