import unittest

from fastapi.testclient import TestClient

from server.core.web import app
from server.logging_conf import *

from .test_data import TestData


class RequestMatchingTests(unittest.TestCase):

    def test_get_request(self):
        with TestData('request'):
            with TestClient(app) as client:
                response = client.get('/endpoint')
                self.assertEqual(200, response.status_code)
                self.assertEqual('Test Response', response.content.decode('utf-8'))

                self.assertTrue('response-header-name' in response.headers)
                self.assertEqual('response-header-value', response.headers['response-header-name'])

                self.assertTrue('response-cookie-name' in response.cookies)
                self.assertEqual('response-cookie-value', response.cookies['response-cookie-name'])

    def test_get_request_with_query_params(self):
        with TestData('request_with_query_params'):
            with TestClient(app) as client:
                response = client.get('/query-endpoint', params={'query-param-name': 'query-param-value'})
                self.assertEqual(200, response.status_code)
                self.assertEqual('Test Query Response', response.content.decode('utf-8'))

                self.assertTrue('query-response-header-name' in response.headers)
                self.assertEqual('query-response-header-value', response.headers['query-response-header-name'])

                self.assertTrue('query-response-cookie-name' in response.cookies)
                self.assertEqual('query-response-cookie-value', response.cookies['query-response-cookie-name'])

    def test_get_request_with_headers(self):
        with TestData('request_with_headers'):
            with TestClient(app) as client:
                response = client.get('/header-endpoint', headers={'header-request-header-name': 'header-request-header-value'})
                self.assertEqual(200, response.status_code)
                self.assertEqual('Test Header Response', response.content.decode('utf-8'))

                self.assertTrue('header-response-header-name' in response.headers)
                self.assertEqual('header-response-header-value', response.headers['header-response-header-name'])

                self.assertTrue('header-response-cookie-name' in response.cookies)
                self.assertEqual('header-response-cookie-value', response.cookies['header-response-cookie-name'])

    def test_get_request_with_cookies(self):
        with TestData('request_with_cookies'):
            with TestClient(app) as client:
                client.cookies = {'cookie-request-cookie-name': 'cookie-request-cookie-value'}
                response = client.get('/cookie-endpoint')
                self.assertEqual(200, response.status_code)
                self.assertEqual('Test Cookie Response', response.content.decode('utf-8'))

                self.assertTrue('cookie-response-header-name' in response.headers)
                self.assertEqual('cookie-response-header-value', response.headers['cookie-response-header-name'])

                self.assertTrue('cookie-response-cookie-name' in response.cookies)
                self.assertEqual('cookie-response-cookie-value', response.cookies['cookie-response-cookie-name'])

    def test_get_request_with_multi(self):
        with TestData('request_with_multi'):
            with TestClient(app) as client:
                client.cookies = {'multi-request-cookie-name': 'multi-request-cookie-value'}
                response = client.get(
                    '/multi-endpoint',
                    headers={'multi-request-header-name': 'multi-request-header-value'},
                    params={'multi-query-param-name': 'multi-query-param-value'}
                )
                self.assertEqual(200, response.status_code)
                self.assertEqual('Test Multi Response', response.content.decode('utf-8'))

                self.assertTrue('multi-response-header-name' in response.headers)
                self.assertEqual('multi-response-header-value', response.headers['multi-response-header-name'])

                self.assertTrue('multi-response-cookie-name' in response.cookies)
                self.assertEqual('multi-response-cookie-value', response.cookies['multi-response-cookie-name'])
