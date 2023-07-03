from ai21.modules.destination import SageMakerDestination
from ai21.modules.resources.execution_utils import execute_sm_request, execute_studio_request

from ai21.modules.resources.nlp_task import NLPTask
from ai21.utils import validate_mandatory_field


class GEC(NLPTask):
    MODULE_NAME = 'gec'

    @classmethod
    def _get_call_name(cls) -> str:
        return cls.MODULE_NAME

    @classmethod
    def _validate_params(cls, params):
        validate_mandatory_field(key='text', call_name=cls.MODULE_NAME, params=params, validate_type=True,
                                 expected_type=str)

    @classmethod
    def _execute_sm(cls, destination: SageMakerDestination, params):
        return execute_sm_request(endpoint_name=destination.endpoint_name, params=params)

    @classmethod
    def _execute_studio_api(cls, params):
        url = cls.get_base_url(**params)
        url = f'{url}/{cls.MODULE_NAME}'
        return execute_studio_request(task_url=url, params=params)
