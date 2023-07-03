from ai21.ai21_studio_client import AI21StudioClient
from ai21.modules.resources.ai21_module import AI21Module


class ListableResource(AI21Module):

    @classmethod
    def list(cls, **params):
        url = cls.get_module_url(**params)
        client = AI21StudioClient(**params)
        return client.execute_http_request(method='GET', url=url)



