import unittest

from fastapi.testclient import TestClient

from server.core.web import app
from server.logging_conf import *

from .test_data import TestData


class IntegrationTests(unittest.TestCase):

    def test_match_request(self):
        with TestData('request_matching'):
            with TestClient(app) as client:
                client.cookies = {'request-cookie-name': 'request-cookie-value'}
                response = client.post(
                    '/matching/endpoint',
                    headers={'request-header-name': 'request-header-value'},
                    params={'query-param-name': 'query-param-value'},
                    json={
                        'name': 'test_name',
                        'password': 'test_password'
                    }
                )
                self.assertEqual(200, response.status_code)
                self.assertEqual('Test Matching Response', response.content.decode('utf-8'))

                self.assertTrue('response-header-name' in response.headers)
                self.assertEqual('response-header-value', response.headers['response-header-name'])

                self.assertTrue('response-cookie-name' in response.cookies)
                self.assertEqual('response-cookie-value', response.cookies['response-cookie-name'])

    def test_rewrite_response(self):
        with TestData('rewrite_response'):
            with TestClient(app) as client:
                response = client.get('/rewrite/endpoint')
                self.assertEqual(200, response.status_code)
                self.assertEqual('Test Rewrite Response', response.content.decode('utf-8'))

                self.assertFalse('request-header-name' in response.headers)
                self.assertTrue('second-response-header-name' in response.headers)
                self.assertEqual('second-response-header-value', response.headers['second-response-header-name'])

                self.assertFalse('response-cookie-name' in response.cookies)
                self.assertTrue('second-response-cookie-name' in response.cookies)
                self.assertEqual('second-response-cookie-value', response.cookies['second-response-cookie-name'])
    
    def test_metrics(self):
        with TestData('metrics'):
            with TestClient(app) as client:
                response = client.get('/matching/endpoint')
                self.assertEqual(200, response.status_code)

                metric_response = client.get('/__metrics__')
                self.assertEqual(200, metric_response.status_code)

                body = metric_response.json()
                self.assertEqual(1, len(body))
                self.assertEqual('test-entry-1', body[0]['entry_id'])
                self.assertEqual(1, len(body[0]['requests']))
                self.assertIsNotNone(body[0].get('response'))

