from abc import ABCMeta, abstractmethod

from ai21.constants import SAGEMAKER_ENDPOINT_KEY, DESTINATION_KEY
from ai21.errors import WrongInputTypeException
from ai21.modules.destination import Destination, SageMakerDestination, AI21Destination, BedrockDestination
from ai21.modules.resources.ai21_module import AI21Module
from ai21.utils import extract_destination, raise_unsupported_destination


class NLPTask(AI21Module, metaclass=ABCMeta):
    @classmethod
    def execute(cls, **params):
        cls._validate_params(params)

        destination = cls._resolve_destination(params)

        if isinstance(destination, BedrockDestination):
            return cls._execute_bedrock_api(destination=destination, params=params)
        if isinstance(destination, SageMakerDestination):
            return cls._execute_sm(destination=destination, params=params)
        if isinstance(destination, AI21Destination):
            return cls._execute_studio_api(params)

        raise WrongInputTypeException(key=DESTINATION_KEY, expected_type=Destination, given_type=type(destination))

    @classmethod
    @abstractmethod
    def _get_call_name(cls) -> str:
        pass

    @classmethod
    @abstractmethod
    def _validate_params(cls, params):
        pass

    @classmethod
    def _resolve_destination(cls, params) -> Destination:
        sm_endpoint = params.pop(SAGEMAKER_ENDPOINT_KEY, None)

        destination = extract_destination(params) or AI21Destination()
        if sm_endpoint:
            destination = SageMakerDestination(endpoint_name=sm_endpoint)

        return destination

    @classmethod
    def _execute_sm(cls, destination: SageMakerDestination, params):
        raise_unsupported_destination(destination=destination, call_name=cls._get_call_name())

    @classmethod
    def _execute_bedrock_api(cls, destination: BedrockDestination, params):
        raise_unsupported_destination(destination=destination, call_name=cls._get_call_name())

    @classmethod
    @abstractmethod
    def _execute_studio_api(cls, params):
        pass
