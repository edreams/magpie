from typing import Dict

from ai21.api_resources import supported_resources


def construct_ai21_object(obj):
    if not isinstance(obj, dict):
        return obj
    class_type = AI21Object
    type_key = obj.get("type", None)
    if type_key is not None:
        class_type = supported_resources().get(type_key, AI21Object)
    instance = class_type(obj)
    return instance


class AI21Object:

    def __init__(self, prop):
        self.values = prop

        if isinstance(prop, dict):
            for key, value in prop.items():
                if isinstance(value, dict):
                    setattr(self, key, construct_ai21_object(value))
                elif isinstance(value, list):
                    setattr(self, key, [construct_ai21_object(i) for i in value])
                else:
                    setattr(self, key, value)

    def __repr__(self):
        return str(self.values)

    def __getitem__(self, item):
        return getattr(self, item)

