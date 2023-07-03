from ai21.ai21_studio_client import AI21StudioClient
from ai21.modules.resources.ai21_module import AI21Module


class RetrievableResource(AI21Module):

    @classmethod
    def get(cls, object_id: str, **params):
        url = f'{cls.get_module_url(**params)}/{object_id}'
        client = AI21StudioClient(**params)
        return client.execute_http_request(method='GET', url=url)



