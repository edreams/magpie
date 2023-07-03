from ai21.ai21_studio_client import AI21StudioClient
from ai21.modules.resources.ai21_module import AI21Module


class UploadResource(AI21Module):

    @classmethod
    def upload(cls, file_path: str, file_param_name: str, **params):
        files = {file_param_name: open(file_path, 'rb')}
        url = cls.get_module_url(**params)
        client = AI21StudioClient(**params)
        return client.execute_http_request(method='POST', url=url, params=params, files=files)



