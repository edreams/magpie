import json
import re

import boto3
from botocore.exceptions import ClientError

import ai21
from ai21.errors import ServerError, ServiceUnavailable, BadRequest, APIError
from ai21.http_client import handle_non_success_response
from ai21.utils import convert_to_ai21_object, log_error

sm_runtime = boto3.client("sagemaker-runtime", region_name=ai21.aws_region)


def invoke_sm_endpoint(endpoint_name: str, input_json: str):
    try:
        response = sm_runtime.invoke_endpoint(
            EndpointName=endpoint_name,
            ContentType="application/json",
            Accept="application/json",
            Body=input_json,
        )

        response_body = json.load(response["Body"])

        return convert_to_ai21_object(response_body)
    except ClientError as sm_client_error:
        handle_sagemaker_client_error(sm_client_error)
    except Exception as exception:
        log_error(f'Calling {endpoint_name} failed with Exception: {exception}')
        raise exception


def handle_sagemaker_client_error(client_exception: ClientError):
    error_response = client_exception.response
    error_message = error_response.get('Error', {}).get('Message', '')
    status_code = error_response.get('ResponseMetadata', {}).get('HTTPStatusCode', None)
    # According to https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_runtime_InvokeEndpoint.html#API_runtime_InvokeEndpoint_Errors
    if status_code == 400:
        raise BadRequest(details=error_message)
    if status_code == 424:
        error_message_template = re.compile(
            r'Received client error \((.*?)\) from primary with message \"(.*?)\". See .* in account .* for more information.')
        model_status_code = int(error_message_template.search(error_message).group(1))
        model_error_message = error_message_template.search(error_message).group(2)
        handle_non_success_response(model_status_code, model_error_message)
    if status_code == 429 or status_code == 503:
        raise ServiceUnavailable(details=error_message)
    if status_code == 500:
        raise ServerError(details=error_message)
    raise APIError(status_code, details=error_message)
