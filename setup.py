#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
# pylint: disable=
# Copyright 2015 BBVA-Cloud (Innovation in Technology).
# Author : Enrique Garcia Pablos <enrique.garcia.pablos@bbva.com , engapa@gmail.com>
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

import setuptools
import os


def get_contents(filename, splitlines=False):
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)), filename)
    if splitlines:
        open(path).read().splitlines()
    return open(path).read()


setuptools.setup(
    name="osc-docker-builder",
    version='2.1',
    author='Enrique Garcia Pablos',
    author_email='engapa@gmail.com',
    url="http://github.com/engapa/osc-docker-builder.git",
    description='Docker image builder for Openstack python clients',
    long_description=get_contents('README.rst'),
    license="Apache 2.0",
    test_suite="osc_docker_builder.tests",
    packages=setuptools.find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Operating System :: OS Independent"
    ],
    zip_safe=False,
    package_data={'osc_docker_builder': ['templates/Dockerfile.j2', 'templates/requirements.j2']},
    entry_points={
        'console_scripts': [
            "osc-builder = osc_docker_builder.osc:main"
        ]
    }

)
