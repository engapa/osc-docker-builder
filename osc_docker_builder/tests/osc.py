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
        osc.clean_build_dir(build_path, remove=False, create=False)
        self.assertFalse(os.path.exists(build_path))
