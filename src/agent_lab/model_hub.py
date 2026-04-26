from enum import Enum


class ModelRegistry(Enum):
    DEEPSEEK_V4_FLASH = {
        'model': 'deepseek-v4-flash',
        'model_provider': 'deepseek',
        'extra_body': {'thinking': {'type': 'disabled'}},
    }
    DEEPSEEK_V4_FLASH_THINKING = {
        'model': 'deepseek-v4-flash',
        'model_provider': 'deepseek',
        'reasoning_effort': 'high',
        'extra_body': {'thinking': {'type': 'enabled'}},
    }
    DEEPSEEK_V4_PRO = {
        'model': 'deepseek-v4-pro',
        'model_provider': 'deepseek',
        'extra_body': {'thinking': {'type': 'disabled'}},
    }
    DEEPSEEK_V4_PRO_THINKING = {
        'model': 'deepseek-v4-pro',
        'model_provider': 'deepseek',
        'reasoning_effort': 'high',
        'extra_body': {'thinking': {'type': 'enabled'}},
    }
    DEEPSEEK_V4_PRO_MAX = {
        'model': 'deepseek-v4-pro',
        'model_provider': 'deepseek',
        'reasoning_effort': 'max',
        'extra_body': {'thinking': {'type': 'enabled'}},
    }

    def __iter__(self):
        return iter(self.value.items())

    def keys(self):
        return self.value.keys()

    def __getitem__(self, key):
        return self.value[key]


LLM_FAST = ModelRegistry.DEEPSEEK_V4_FLASH
LLM_THINKING = ModelRegistry.DEEPSEEK_V4_FLASH_THINKING
