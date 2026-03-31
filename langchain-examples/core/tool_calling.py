from langchain.messages import HumanMessage, AIMessage
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain.tools import tool
from pprint import pprint

model = init_chat_model('deepseek-chat')
prompt = 'What is the weather like in Boston and Tokyo?'


@tool
def get_weather(location: str) -> str:
    """Get the weather at a location"""
    return f"It's sunny in {location}"


def model_output():
    model_with_tools = model.bind_tools([get_weather])
    messages = [HumanMessage(prompt)]
    ai_msg = model_with_tools.invoke(messages)
    # pprint(ai_msg)
    ai_msg.pretty_print()
    messages.append(ai_msg)  # type: ignore

    for tool_call in ai_msg.tool_calls:
        print('Tool: ', tool_call['name'])
        print('Args: ', tool_call['args'])
        tool_result = get_weather.invoke(tool_call)
        print('Result: ', tool_result)
        tool_result.pretty_print()
        messages.append(tool_result)

    response = model_with_tools.invoke(messages)
    pprint(response)


def agent_output():
    agent = create_agent(model, tools=[get_weather])
    response = agent.invoke({'messages': HumanMessage(prompt)})
    pprint(response)


if __name__ == '__main__':
    print('Model output:')
    model_output()

    print('Agent output:')
    agent_output()
