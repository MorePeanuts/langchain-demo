# This file contains the model registry for the application.
# It defines the models that are used for chat and embedding.

from enum import Enum


class ChatModelRegistry(Enum):
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


LLM_FAST = ChatModelRegistry.DEEPSEEK_V4_FLASH
LLM_THINKING = ChatModelRegistry.DEEPSEEK_V4_FLASH_THINKING


class EmbeddingModelRegistry(Enum):
    # using openai-compatible endpoint from aihubmix
    TEXT_EMBEDDING_3_SMALL = {
        'model': 'text-embedding-3-small',
        'provider': 'openai',
    }
    TEXT_EMBEDDING_3_LARGE = {
        'model': 'text-embedding-3-large',
        'provider': 'openai',
    }

    def __iter__(self):
        return iter(self.value.items())

    def keys(self):
        return self.value.keys()

    def __getitem__(self, key):
        return self.value[key]


EMBEDDING_SMALL = EmbeddingModelRegistry.TEXT_EMBEDDING_3_SMALL
EMBEDDING_LARGE = EmbeddingModelRegistry.TEXT_EMBEDDING_3_LARGE
