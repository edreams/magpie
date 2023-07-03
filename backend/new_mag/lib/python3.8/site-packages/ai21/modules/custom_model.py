from ai21.modules.resources.creatable_resource import CreatableResource
from ai21.modules.resources.listable_resource import ListableResource
from ai21.modules.resources.retrievable_resource import RetrievableResource
from ai21.utils import validate_mandatory_field


class CustomModel(CreatableResource, RetrievableResource, ListableResource):
    MODULE_NAME = 'custom-model'

    @classmethod
    def create(cls, **params):
        validate_mandatory_field(key='dataset_id', call_name=cls.MODULE_NAME, params=params, validate_type=True, expected_type=str)
        validate_mandatory_field(key='model_name', call_name=cls.MODULE_NAME, params=params, validate_type=True, expected_type=str)
        validate_mandatory_field(key='model_type', call_name=cls.MODULE_NAME, params=params, validate_type=True, expected_type=str)
        super().create(**params)
