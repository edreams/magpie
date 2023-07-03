
from ai21.errors import EmptyMandatoryListException
from ai21.modules.resources.execution_utils import execute_studio_request
from ai21.modules.resources.nlp_task import NLPTask
from ai21.utils import validate_mandatory_field


class Improvements(NLPTask):
    MODULE_NAME = 'improvements'

    @classmethod
    def _get_call_name(cls) -> str:
        return cls.MODULE_NAME

    @classmethod
    def _validate_params(cls, params):
        validate_mandatory_field(key='text', call_name=cls.MODULE_NAME, params=params, validate_type=True,
                                 expected_type=str)
        if params.get('types') is None or len(params['types']) == 0:
            raise EmptyMandatoryListException('types')

    @classmethod
    def _execute_studio_api(cls, params):
        url = cls.get_base_url(**params)
        url = f'{url}/{cls.MODULE_NAME}'
        return execute_studio_request(task_url=url, params=params)
