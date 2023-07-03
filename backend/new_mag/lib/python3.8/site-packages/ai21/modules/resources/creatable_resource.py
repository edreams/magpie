from ai21.ai21_studio_client import AI21StudioClient
from ai21.modules.resources.ai21_module import AI21Module


class CreatableResource(AI21Module):

    @classmethod
    def create(cls, **params):
        url = cls.get_module_url(**params)
        client = AI21StudioClient(**params)
        return client.execute_http_request(method='POST', url=url, params=params)



