from typing import Literal
from langchain.messages import HumanMessage
from langgraph.graph import MessagesState
from langchain.tools import tool
from langgraph.types import interrupt
from langchain.chat_models import init_chat_model
from agent_lab.model_hub import LLM_FAST
from langgraph.graph import START, END, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import InMemorySaver
from langchain.messages import SystemMessage, AIMessageChunk
from langgraph.types import Command
from rich.console import Console


@tool
def send_email(to: str, subject: str, body: str):
    """Send an email to a recipient."""

    # Pause before sending; payload surfaces in result["__interrupt__"]
    response = interrupt(
        {
            'action': 'send_email',
            'to': to,
            'subject': subject,
            'body': body,
            'message': 'Approve sending this email? (y/n)',
        }
    )

    if response.get('action') == 'approve':
        final_to = response.get('to', to)
        final_subject = response.get('subject', subject)
        final_body = response.get('body', body)

        # Actually send the email (your implementation here)
        print(f'[send_email] to={final_to} subject={final_subject} body={final_body}')
        return f'Email sent to {final_to}'

    return 'Email cancelled by user'


llm = init_chat_model(**LLM_FAST).bind_tools([send_email])


class State(MessagesState):
    pass


def user_input(state: State) -> Command[Literal['llm_call', '__end__']]:
    user_prompt = interrupt(
        {
            'action': 'user_input',
            'message': 'USER: ',
        }
    )
    if user_prompt == '/exit':
        return Command(goto='__end__')
    else:
        return Command(update={'messages': [HumanMessage(user_prompt)]}, goto='llm_call')


async def llm_call(state: State):
    ai_msg = await llm.ainvoke(state['messages'])
    print()
    return {'messages': [ai_msg]}


agent = (
    StateGraph(State)  # type: ignore
    .add_node(user_input)
    .add_node(llm_call)
    .add_node('send_email', ToolNode([send_email]))
    .add_edge(START, 'user_input')
    .add_conditional_edges(
        'llm_call',
        tools_condition,
        {
            'tools': 'send_email',
            END: 'user_input',
        },
    )
    .add_edge('send_email', 'llm_call')
    .compile(checkpointer=InMemorySaver())
)


async def main():
    console = Console()

    initial_input = {
        'messages': [SystemMessage('You are a helpful assistant that can send emails for user.')],
    }
    config = {'configurable': {'thread_id': 'thread-1'}}

    while True:
        async for chunk in agent.astream(  # type: ignore
            initial_input,
            stream_mode=['messages', 'updates'],
            config=config,
            version='v2',
        ):
            if chunk['type'] == 'messages':
                # Handle streaming message content
                msg, _ = chunk['data']
                if isinstance(msg, AIMessageChunk) and msg.content:
                    console.print(msg.content, style='blue', end='')

            elif chunk['type'] == 'updates':
                # Check for interrupts in the updates data
                if '__interrupt__' in chunk['data']:
                    interrupt_info = chunk['data']['__interrupt__'][0].value
                    user_input = input(interrupt_info['message'])
                    if interrupt_info['action'] == 'user_input':
                        initial_input = Command(resume=user_input)
                    elif interrupt_info['action'] == 'send_email':
                        initial_input = Command(
                            resume={
                                'action': 'approve' if user_input == 'y' else 'reject',
                            }
                        )
                    break
        goto = agent.get_state(config).next  # type: ignore
        if len(goto) == 0:
            console.print('See you again!', style='blue')
            break


if __name__ == '__main__':
    import asyncio

    asyncio.run(main())
