import json

from django import test

from nose.tools import eq_


class TestCase(test.TestCase):

    def assert2x(self, response):
        assert str(response.status_code).startswith('2'), (
                'Unexpected status code: {0}'.format(response.status_code))

    def json(self, response, expected_status=200,
             expected_type='application/json'):
        eq_(response.status_code, expected_status, response.content)
        eq_(response['Content-Type'], expected_type, response.content)
        return json.loads(response.content)