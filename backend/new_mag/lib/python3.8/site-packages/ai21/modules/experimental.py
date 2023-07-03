from ai21.modules.completion import Completion
from ai21.modules.destination import SageMakerDestination
from ai21.modules.resources.ai21_module import AI21Module
from ai21.modules.resources.execution_utils import execute_studio_request, execute_sm_request
from ai21.modules.resources.nlp_task import NLPTask
from ai21.utils import validate_mandatory_field


class Experimental(AI21Module):
    @classmethod
    def embed(cls, **params):
        validate_mandatory_field(key='texts', call_name="embed_experimental", params=params, validate_type=True,
                                 expected_type=list)
        url = cls.get_base_url(**params)
        url = f'{url}/experimental/embed'
        return execute_studio_request(task_url=url, params=params)

    @classmethod
    def answer(cls, **params):
        return _AnswerExperimental.execute(**params)


class _AnswerExperimental(NLPTask):
    MODULE_NAME = 'answer_experimental'

    @classmethod
    def _get_call_name(cls) -> str:
        return cls.MODULE_NAME

    @classmethod
    def _validate_params(cls, params):
        validate_mandatory_field(key='context', call_name="answer_experimental", params=params, validate_type=True,
                                 expected_type=str)
        validate_mandatory_field(key='question', call_name="answer_experimental", params=params, validate_type=True,
                                 expected_type=str)

    @classmethod
    def _execute_sm(cls, destination: SageMakerDestination, params):
        return execute_sm_request(endpoint_name=destination.endpoint_name, params=params)

    @classmethod
    def _execute_studio_api(cls, params):
        url = cls.get_base_url(**params)
        url = f'{url}/experimental/answer'
        return execute_studio_request(task_url=url, params=params)
