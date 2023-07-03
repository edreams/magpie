from dataclasses import dataclass


class Destination:
    pass


class AI21Destination(Destination):
    pass


@dataclass
class AWSDestination(Destination):
    pass


@dataclass
class BedrockDestination(AWSDestination):
    model_id: str


@dataclass
class SageMakerDestination(AWSDestination):
    endpoint_name: str


class BedrockModelID:
    J2_GRANDE_INSTRUCT = 'ai21.j2-grande-instruct'
    J2_JUMBO_INSTRUCT = 'ai21.j2-jumbo-instruct'
