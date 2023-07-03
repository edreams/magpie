from ai21.modules.destination import SageMakerDestination
from ai21.modules.resources.execution_utils import execute_sm_request
from ai21.modules.resources.nlp_task import NLPTask
from ai21.utils import validate_mandatory_field


class Answer(NLPTask):
    MODULE_NAME = 'answer'

    @classmethod
    def _get_call_name(cls) -> str:
        return cls.MODULE_NAME

    @classmethod
    def _validate_params(cls, params):
        validate_mandatory_field(key='context', call_name=cls.MODULE_NAME, params=params, validate_type=True,
                                 expected_type=str)
        validate_mandatory_field(key='question', call_name=cls.MODULE_NAME, params=params, validate_type=True,
                                 expected_type=str)

    @classmethod
    def _execute_sm(cls, destination: SageMakerDestination, params):
        return execute_sm_request(endpoint_name=destination.endpoint_name, params=params)

    @classmethod
    def _execute_studio_api(cls, params):
        raise NotImplementedError(f'The module {cls.MODULE_NAME} is not implemented for the non experimental endpoint')
