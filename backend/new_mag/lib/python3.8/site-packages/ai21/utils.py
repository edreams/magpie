import logging
from typing import Dict, Callable, Any, Optional, Type

import ai21
from ai21.ai21_object import construct_ai21_object
from ai21.constants import DESTINATION_KEY
from ai21.errors import MissingInputException, WrongInputTypeException, UnsupportedInputException, \
    UnsupportedDestinationException
from ai21.modules.destination import Destination, SageMakerDestination, BedrockDestination, AI21Destination

logger = logging.getLogger("ai21")


def log_info(message):
    if ai21.log_level == "debug":
        print(message)
        logger.debug(message)
    elif ai21.log_level == "info":
        logger.info(message)


def log_error(message):
    logger.error(message)


def convert_to_ai21_object(obj: Dict):
    if isinstance(obj, list):
        return [construct_ai21_object(i) for i in obj]

    return construct_ai21_object(obj)


def validate_mandatory_field(key: str, call_name: str, params: Dict, validate_type: bool = False,
                             expected_type: type = None):
    value = params.get(key, None)
    if value is None:
        raise MissingInputException(field_name=key, call_name=call_name)
    if not validate_type:
        pass
    if not isinstance(value, expected_type):
        raise WrongInputTypeException(key=key, expected_type=expected_type, given_type=type(value))


def validate_mandatory_fields(key_to_type: Dict, params: Dict, call_name: str):
    [validate_mandatory_field(key=key, call_name=call_name, params=params, validate_type=True, expected_type=key_type)
     for key, key_type in key_to_type]


def validate_unsupported_field(key: str, call_name: str, params: Dict):
    if key in params:
        raise UnsupportedInputException(field_name=key, call_name=call_name)


def raise_unsupported_destination(destination: Destination, call_name) -> None:
    raise UnsupportedDestinationException(destination_name=str(type(destination).__name__), call_name=call_name)


def get_global_configs() -> Dict[str, Any]:
    from ai21 import api_key, organization, application, api_version, api_host, timeout_sec, num_retries, aws_region
    return {
        'api_key': api_key,
        'organization': organization,
        'application': application,
        'api_version': api_version,
        'api_host': api_host,
        'timeout_sec': timeout_sec,
        'num_retries': num_retries,
        'aws_region': aws_region,
    }


def get_value(key: str, params: Dict, global_configs: Dict, expected_type: type):
    passed_value = params.get(key, None)
    if passed_value is not None:
        if not isinstance(passed_value, expected_type):
            raise WrongInputTypeException(key, expected_type, type(passed_value))
        return passed_value

    global_value = global_configs[key]

    if global_value is not None and not isinstance(global_value, expected_type):
        raise WrongInputTypeException(key, global_value, type(global_value))
    return global_value


def extract_destination(params) -> Optional[Destination]:
    return params.pop(DESTINATION_KEY, None)
