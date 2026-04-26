from langchain.chat_models import init_chat_model

deepseek_v4_flash = init_chat_model(
    'deepseek-v4-flash',
    model_provider='deepseek',
    extra_body={'thinking': {'type': 'disabled'}},
)

deepseek_v4_flash_thinking = init_chat_model(
    'deepseek-v4-flash',
    model_provider='deepseek',
    reasoning_effort='high',
    extra_body={'thinking': {'type': 'enabled'}},
)

deepseek_v4_pro = init_chat_model(
    'deepseek-v4-pro',
    model_provider='deepseek',
    extra_body={'thinking': {'type': 'disabled'}},
)

deepseek_v4_pro_thinking = init_chat_model(
    'deepseek-v4-pro',
    model_provider='deepseek',
    reasoning_effort='hign',
    extra_body={'thinking': {'type': 'enabled'}},
)

deepseek_v4_pro_max = init_chat_model(
    'deepseek-v4-pro',
    model_provider='deepseek',
    reasoning_effort='max',
    extra_body={'thinking': {'type': 'enabled'}},
)
