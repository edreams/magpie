from ai21.ai21_object import AI21Object

from ai21.utils import get_global_configs

from ai21.ai21_studio_client import get_value


class AI21Module(AI21Object):

    @classmethod
    def get_base_url(cls, **params):
        global_configs = get_global_configs()
        api_host = get_value('api_host', params, global_configs, str)
        api_version = get_value('api_version', params, global_configs, str)
        return f'{api_host}/studio/{api_version}'

    @classmethod
    def get_module_url(cls, **params):
        return f'{cls.get_base_url(**params)}/{cls.MODULE_NAME}'




