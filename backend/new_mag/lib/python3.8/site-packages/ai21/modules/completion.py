from ai21.modules.destination import BedrockDestination, SageMakerDestination
from ai21.modules.resources.execution_utils import execute_sm_request, execute_bedrock_request, execute_studio_request
from ai21.modules.resources.nlp_task import NLPTask
from ai21.utils import validate_mandatory_field


class Completion(NLPTask):
    MODULE_NAME = 'complete'

    @classmethod
    def _get_call_name(cls) -> str:
        return cls.MODULE_NAME

    @classmethod
    def _validate_params(cls, params):
        validate_mandatory_field(key='prompt', call_name=cls.MODULE_NAME, params=params, validate_type=True,
                                 expected_type=str)

        if params.get('stopSequences', None) is None:
            params['stopSequences'] = []

    @classmethod
    def _execute_bedrock_api(cls, destination: BedrockDestination, params):
        return execute_bedrock_request(
            model_id=destination.model_id,
            unsupported_fields=['model', 'custom_model'],
            params=params,
        )

    @classmethod
    def _execute_sm(cls, destination: SageMakerDestination, params):
        return execute_sm_request(
            endpoint_name=destination.endpoint_name,
            unsupported_fields=['model', 'custom_model'],
            params=params,
        )

    @classmethod
    def _execute_studio_api(cls, params):
        validate_mandatory_field(
            key='model', call_name=cls._get_call_name(), params=params, validate_type=True,
            expected_type=str
        )

        model = params.get('model', None)
        custom_model = params.get('custom_model', None)
        experimental_mode = params.get('experimental_mode', False)

        if experimental_mode:
            model = f'experimental/{model}'

        url = f'{cls.get_base_url(**params)}/{model}'

        if custom_model is not None:
            url = f'{url}/{custom_model}'

        url = f'{url}/{cls.MODULE_NAME}'

        return execute_studio_request(task_url=url, params=params)

