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

import unittest
import os
import shutil

from osc_docker_builder import osc


class OSCTestCase(unittest.TestCase):
    """
    Docker image builder for OSC tests
    """

    def setUp(self):
        """Run before each test method to initialize test environment."""
        super(OSCTestCase, self).setUp()

    def tearDown(self):
        """Runs after each test method to tear down test environment."""
        super(OSCTestCase, self).tearDown()

    def test_clean_dir_default(self):
        """
        Tests build path creation
        """
        build_path = 'test_build'
        try:
            osc.clean_build_dir(build_path, remove=False, create=True)
            self.assertTrue(os.path.exists(build_path))
        finally:
            os.rmdir(build_path)

    def test_clean_dir_without_creation(self):
        """
        Tests build path creation
        """
        build_path = 'test_build'
        os.makedirs(build_path)
        with open(build_path + '/test', 'wb') as test_file:
            test_file.write('test')
        osc.clean_build_dir(build_path, remove=True, create=False)
        self.assertFalse(os.path.exists(build_path + '/test'))
        self.assertFalse(os.path.exists(build_path))

    def test_parse_args(self):
        """
        Tests pargs
        """

        args = [
            '-bp', 'test',
            '-f', 'test.file.dat',
            '-pv', '3.4.4',
            '-r', 'newton',
            '-c', ('client1', 'client2', 'client3'),
            '-sf',
            '-v'
        ]

        parsed_args = osc.parse_args(args)

        self.assertEqual(parsed_args.build_path, 'test')
        self.assertEqual(parsed_args.config_file, 'test.file.dat')
        self.assertEqual(parsed_args.python_version, '3.4.4')
        self.assertEqual(parsed_args.release, 'newton')
        self.assertEqual(parsed_args.clients, [('client1', 'client2', 'client3')])
        self.assertEqual(parsed_args.skip_fails, True)
        self.assertEqual(parsed_args.verbose, True)

    def test_render_templates(self):
        """
        Tests rendered files
        :return:
        """
        python_version = '2.7'
        client_configs = [{'name': 'myclient', 'release': 'newton'}]
        build_path = 'test_build'

        osc.clean_build_dir(build_path)
        osc.render_templates(python_version, client_configs, build_path)

        if os.path.exists(build_path):
            try:
                for filename in os.listdir(build_path):
                    filepath = os.path.join(build_path, filename)
                    try:
                        if filename in ['Dockerfile', 'requirements.txt']:
                            with open(filepath, 'r') as f:
                                content = f.read()
                            shutil.rmtree(filepath)
                            if filename == 'Dockerfile':
                                self.assertIn('python:{}'.format(python_version),
                                              content,
                                              'Docker file content has to have "python:2.7" string')
                            elif filename == 'requirements.txt':
                                self.assertIn(
                                    'python-{}client@{}'.format(
                                        client_configs[0]['name'], client_configs[0]['release']),
                                    content,
                                    'requirements.txt has to have "python-myclientclient@newton" string')
                        else:
                            shutil.rmtree(filepath)
                            raise Exception('Invalid file name %s', filename)
                    except OSError:
                        os.remove(filepath)
            except Exception as e:
                raise e
            finally:
                os.rmdir(build_path)
        else:
            raise Exception('Test build path not created')

    def test_client_config(self):
        """
        Tests client config
        """
        client_name = 'myclient'
        release = 'release'

        client_config = osc.client_config(client_name, release)

        self.assertDictEqual(
            client_config,
            {
                'name': client_name,
                'release': release,
                'url': "https://raw.githubusercontent.com/openstack/python-myclientclient/release/tox.ini"
            }
        )
