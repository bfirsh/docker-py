import json

import pytest

from .. import base
from .api_test import DockerClientTest, url_prefix, fake_request

class ServiceTest(DockerClientTest):
    @base.requires_api_version('1.24')
    def test_list_services(self):
        services = self.client.services()
        self.assertEqual(len(services), 1)
        self.assertIn('ID', services[0])

        args = fake_request.call_args
        self.assertEqual(args[0][0], 'GET')
        self.assertEqual(args[0][1], url_prefix + 'services')

    @base.requires_api_version('1.21')
    def test_create_service(self):
        result = self.client.create_volume('testservice')
        self.assertIn('ID', result)

        args = fake_request.call_args
        self.assertEqual(args[0][0], 'POST')
        self.assertEqual(args[0][1], url_prefix + 'services/create')
        self.assertEqual(json.loads(args[1]['data']), {'Name': name})
