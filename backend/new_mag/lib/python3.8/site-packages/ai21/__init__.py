from ai21.constants import STUDIO_HOST, DEFAULT_API_VERSION
from ai21.modules.completion import Completion
from ai21.modules.dataset import Dataset
from ai21.modules.tokenization import Tokenization
from ai21.modules.custom_model import CustomModel
from ai21.modules.experimental import Experimental
from ai21.modules.paraphrase import Paraphrase
from ai21.modules.summarize import Summarize
from ai21.modules.segmentation import Segmentation
from ai21.modules.improvements import Improvements
from ai21.modules.question_answering import Answer
from ai21.modules.gec import GEC
from ai21.modules.destination import BedrockDestination, AI21Destination, BedrockModelID, SageMakerDestination


api_key = None
organization = None
application = None
api_version = DEFAULT_API_VERSION
api_host = STUDIO_HOST
timeout_sec = None
num_retries = None
aws_region = None
log_level = 'error'
