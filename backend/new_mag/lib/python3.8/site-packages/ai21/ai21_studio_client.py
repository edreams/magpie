from typing import Optional, Dict
from ai21.errors import MissingApiKeyException, WrongInputTypeException
from ai21.http_client import HttpClient
from ai21.utils import get_global_configs, convert_to_ai21_object, get_value
from ai21.version import __version__


def build_ai21_user_agent():
    global_configs = get_global_configs()
    user_agent = f'ai21 studio SDK {__version__}'
    organization = global_configs['organization']
    if organization is not None:
        user_agent = f'{user_agent} organization: {organization}'
    application = global_configs['application']
    if application is not None:
        user_agent = f'{user_agent} application: {application}'
    return user_agent


class AI21StudioClient:
    def __init__(self, **params):
        global_configs = get_global_configs()
        api_key = get_value('api_key', params, global_configs, str)
        if api_key is None:
            raise MissingApiKeyException()
        self.api_key = api_key
        headers = self.build_default_headers()
        passed_headers = params.get('headers', None)
        if passed_headers is not None:
            if not isinstance(passed_headers, Dict):
                raise WrongInputTypeException('headers', Dict, type(passed_headers))
            headers.update(passed_headers)
        timeout_sec = get_value('timeout_sec', params, global_configs, int)
        num_retries = get_value('num_retries', params, global_configs, int)
        self.http_client = HttpClient(timeout_sec=timeout_sec, num_retries=num_retries, headers=headers)

    def build_default_headers(self):
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'User-Agent': build_ai21_user_agent()
        }
        return headers

    def execute_http_request(self, method: str, url: str, params: Optional[Dict] = None, files=None):
        response = self.http_client.execute_http_request(method=method, url=url, params=params, files=files)
        return convert_to_ai21_object(response)
