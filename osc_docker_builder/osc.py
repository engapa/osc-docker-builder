#!/usr/bin/env python
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
import yaml

from jinja2 import Environment, FileSystemLoader


if sys.version_info < (2, 7):
    sys.exit("This script requires Python 2.7 or newer!")


LOG = logging.getLogger("osc-builder")
logging.basicConfig()
LOG.setLevel(logging.INFO)

BUILD_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'build')
TEMPLATES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')


def clean_build_dir(build_path, remove=False, create=True):
    """
    Clean build directory
    :param build_path: Build path
    :param remove: Remove root build directory, by default False
    :param create: Create root build directory, by default True
    :return: void
    """
    if os.path.exists(build_path):
        for filename in os.listdir(build_path):
            filepath = os.path.join(build_path, filename)
            try:
                shutil.rmtree(filepath)
            except OSError:
                os.remove(filepath)
        if remove:
            os.rmdir(build_path)

    elif create:
        os.makedirs(build_path)


def parse_args(args):
    """
    Parses args
    :param args: arguments
    :return: parsed args
    """

    parser = argparse.ArgumentParser(
        prog="ocs",
        description="Build a docker image with all Openstack clients"
                    " that you want for a specific upstream branch and python version")
    parser.add_argument('-bp', '--build-path', dest='build_path',
                        help='The build path where files are written.')
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

    return parser.parse_args(args)


def download_docker_image_base(python_version):
    """
    Download docker image base
    :param python_version: python version
    :return: void, pull the suitable docker image
    """
    child = subprocess.Popen(['docker', 'pull', 'python:{}'.format(python_version)],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = child.communicate()
    LOG.debug(output)
    if error and child.returncode != 0:
        LOG.error(error)
        raise SystemExit(
            "Unavailable to download docker image for python version {}".format(python_version))


def download_tox_module(args):
    """
    Download tox.ini file from openstack client
    :param args: client_name, url ,build path
    :return: void, create a <client>-tox.ini file into build directory
    """
    client_name, url, build_path = args
    start_time = time.time()
    fname, info = urllib.urlretrieve(url,
                                     filename='{}/{}-tox.ini'.format(build_path, client_name))
    end_time = time.time()
    LOG.debug(" Downloaded file : %s, size : %s bytes, time: %s",
              fname, info.get('content-length'), end_time - start_time)


def check_client_pv(client_name, py_version, skip_fails, build_path):
    """
    Matches python version with tox env
    :param client_name: name of openstack client
    :param py_version: python version
    :param skip_fails: skip fails for this client and continue
    :param build_path: Build path
    :return: True if matches, False in other case
    """
    py_env = 'py'
    if '.' in py_version:
        py_env += py_version.replace('.', '')[0:2]
    else:
        py_env += py_version[0:2]

    config = tox.session.prepare(
        [
            "-c{}/{}-tox.ini".format(build_path, client_name),
            "-l"
        ]
    )
    found = py_env in config.envlist

    if not found:
        msg = "Not found venv {} for client {}".format(py_env, client_name)
        if not skip_fails:
            raise SystemExit(msg)
        else:
            LOG.warning(msg)

    return found


def render_templates(python_version, client_configs, build_path):
    """
    Render Dockerfile.j2 and requirements.txt.j2 templates in files into build directory
    :param python_version: python version
    :param client_configs: openstack client configs
    :param build_path: Build path
    :return: void, rendered files into build directory
    """

    env = Environment(loader=FileSystemLoader(searchpath=TEMPLATES_PATH))
    with open(build_path + '/requirements.txt', 'wb') as requirements:
        LOG.debug("Generating file requirements.txt")
        requirements.write(
            env.get_template('requirements.j2').render(
                client_configs=client_configs
            )
        )
    with open(build_path + '/Dockerfile', 'wb') as dockerfile:
        LOG.debug("Generating file Dockerfile")
        dockerfile.write(
            env.get_template('Dockerfile.j2').render(
                python_version=python_version
            )
        )


def build_docker_image(python_version, release, build_path):
    """
    Build docker image by calling docker local daemon
    :param python_version: python version
    :param release: upstream release
    :param build_path: Build path
    :return: void, get docker local image
    """
    tag = 'engapa/osc:{}-{}-latest'.format(python_version, release.replace('/', '_'))
    child = subprocess.Popen(['docker', 'build', '-t', tag, build_path], stdin=subprocess.PIPE)
    output, error = child.communicate()
    if error and child.returncode != 0:
        LOG.error(error)
        raise SystemExit("Unavailable to build docker image")


def client_config(client_name, release, egg=None):
    """
    Gets Openstack client config
    :param client_name: Name of client
    :param release: Release
    :param egg: egg name
    :return: Client config
    """
    return dict(
        name=client_name,
        release=release,
        url="https://raw.githubusercontent.com/openstack/"
            "python-{}client/{}/tox.ini".format(client_name, release),
        egg=egg if egg else "python-{}client".format(client_name)
    )


def main():
    """
    Main function
    """

    args = parse_args(sys.argv[1:])

    if args.config_file:
        try:
            with open(args.config_file, 'r') as config_file:
                config = yaml.load(config_file)
            python_version = config.get('python_version')
            if python_version:
                python_version = str(python_version)
            release = config.get('release')
            skip_fails = config.get('skip-fails', False)
            verbose = config.get('verbose', False)
            build_path = config.get('build_path', BUILD_PATH)
            client_configs = [
                client_config(x['name'], x.get('release', release), x.get('egg')) for x in config['clients']]
        except yaml.YAMLError as exc:
            LOG.error('Unable to load configuration from file: {} . Caused by : {}', config_file, exc)
            sys.exit(1)
        except Exception as e:
            LOG.error(e)
            sys.exit(1)
    else:
        python_version = args.python_version
        release = args.release
        skip_fails = args.skip_fails
        verbose = args.verbose
        build_path = args.build_path or BUILD_PATH
        client_configs = [client_config(client, release) for client in args.clients]

    # Required values :
    assert python_version, 'Required python_version value'
    assert release, 'Required release value'
    assert client_configs, 'Required clients list'

    if verbose:
        LOG.setLevel(logging.DEBUG)

    clean_build_dir(build_path)

    download_docker_image_base(python_version)

    pool = multiprocessing.Pool()
    download_tox_module_args = [(client['name'], client['url'], build_path) for client in client_configs]
    pool.map(download_tox_module, download_tox_module_args)

    cclients = []

    for client in client_configs:
        if check_client_pv(client['name'], python_version, skip_fails, build_path):
            cclients.append(client)

    if cclients:
        render_templates(python_version, client_configs, build_path)
        build_docker_image(python_version, release, build_path)


if __name__ == "__main__":
    main()
