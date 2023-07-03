from ai21.modules.resources.execution_utils import execute_studio_request
from ai21.modules.resources.nlp_task import NLPTask
from ai21.utils import validate_mandatory_field


class Segmentation(NLPTask):
    MODULE_NAME = 'segmentation'

    @classmethod
    def _get_call_name(cls) -> str:
        return cls.MODULE_NAME

    @classmethod
    def _validate_params(cls, params):
        validate_mandatory_field(key='sourceType', call_name=cls.MODULE_NAME, params=params, validate_type=True,
                                 expected_type=str)
        validate_mandatory_field(key='source', call_name=cls.MODULE_NAME, params=params, validate_type=True,
                                 expected_type=str)

    @classmethod
    def _execute_studio_api(cls, params):
        url = cls.get_base_url(**params)
        url = f'{url}/{cls.MODULE_NAME}'
        return execute_studio_request(task_url=url, params=params)
