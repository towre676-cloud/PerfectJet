"""Math Lab requests cross the local HTTP boundary without finite-model inputs."""
import json
import sys
import threading
import types
import unittest
from unittest.mock import patch
from urllib.request import Request, urlopen

from perfectjet.observatory.workbench import evaluate, make_server


class MathLabWorkbenchTests(unittest.TestCase):
    def test_math_routes_do_not_compile_a_finite_model(self):
        calls = []
        module = types.ModuleType('perfectjet.mathlab')
        module.catalogue = lambda: {'labs': [{'id': 'recover'}], 'equations': []}
        module.evaluate = lambda request: calls.append(request) or {'title': 'Computed'}
        request = {'operation': 'math-lab', 'lab': 'recover', 'params': {'H': [[1, 0]]}}
        with patch.dict(sys.modules, {'perfectjet.mathlab': module}):
            with patch('perfectjet.observatory.workbench.compile_payload', side_effect=AssertionError('finite-model compilation')):
                self.assertEqual(evaluate({'operation': 'math-catalog'})['labs'][0]['id'], 'recover')
                self.assertEqual(evaluate(request), {'title': 'Computed'})
        self.assertEqual(calls, [request])

    def test_math_view_and_authenticated_http_route(self):
        module = types.ModuleType('perfectjet.mathlab')
        module.catalogue = lambda: {'labs': [{'id': 'recover'}], 'equations': []}
        module.evaluate = lambda request: {'title': 'Computed', 'metrics': [{'label': 'rank', 'value': 1}]}
        server = make_server(0)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        url = f'http://127.0.0.1:{server.server_port}'
        try:
            with urlopen(url) as response:
                page = response.read().decode()
            self.assertIn('id="mathLabView"', page)
            self.assertIn('id="observatoryView" hidden', page)
            self.assertIn('id="atlasSearch"', page)
            token = page.split("token='")[1].split("'")[0]
            headers = {'X-Observatory-Token': token, 'Content-Type': 'application/json'}
            request = Request(url+'/api/evaluate', json.dumps({'operation': 'math-lab', 'lab': 'recover', 'params': {}}).encode(), headers)
            with patch.dict(sys.modules, {'perfectjet.mathlab': module}):
                with urlopen(request) as response:
                    answer = json.load(response)
            self.assertEqual(answer['metrics'][0]['value'], 1)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)


if __name__ == '__main__':
    unittest.main()
