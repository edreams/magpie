from ai21.modules.resources.listable_resource import ListableResource
from ai21.modules.resources.retrievable_resource import RetrievableResource
from ai21.modules.resources.upload_resource import UploadResource
from ai21.utils import validate_mandatory_field


class Dataset(UploadResource, RetrievableResource, ListableResource):

    MODULE_NAME = 'dataset'

    @classmethod
    def upload(cls, file_path: str, **params):
        validate_mandatory_field(key='dataset_name', call_name=cls.MODULE_NAME, params=params, validate_type=True, expected_type=str)
        super().upload(file_path=file_path, file_param_name='dataset_file', **params)
