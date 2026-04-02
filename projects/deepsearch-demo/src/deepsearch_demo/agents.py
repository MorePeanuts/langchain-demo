import json
from langchain.chat_models import init_chat_model
from langchain.messages import SystemMessage, HumanMessage, AIMessage
from langgraph.types import Command
from langgraph.graph import StateGraph, START, END
from loguru import logger
from .state import State, Paragraph
from .schema import ReportStructure, ReflectionSummary, FinalReport
from .tools import tavily_search
from .utils import truncate_content


class DeepSearchAgent:
    def __init__(self):
        self.llm = init_chat_model('deepseek-chat')
        self.max_reflections = 3
        self.agent = (
            StateGraph(State)
            .add_node('generate_report_structure', self.generate_report_structure)
            .add_node('first_search', self.first_search)
            .add_node('first_summary', self.first_summary)
            .add_node('reflection', self.reflection)
            .add_node('reflection_summary', self.reflection_summary)
            .add_node('generate_final_report', self.generate_final_report)
            .add_edge(START, 'generate_report_structure')
            .add_edge('generate_final_report', END)
            .compile()
        )

    def research(self, query: str, save_report: bool = True) -> str:
        logger.info(f'Start research: {query}')
        self.state = State(query=query)
        response = self.agent.invoke(self.state)
        return AIMessage(response['final_report']).pretty_repr()

    def plot_graph(self):
        raise NotImplementedError()

    def generate_report_structure(self, state: State) -> Command:
        logger.info('Generating the report structure based on the following query:')

        prompt = """
You are a deep research assistant. Given a query, you need to plan the structure of a report and the paragraphs it contains. Up to five paragraphs.

Ensure the paragraphs are logically and sequentially ordered.

Once the outline is created, you will be provided with tools to search the web and reflect on each section separately.
"""
        llm_with_structure = self.llm.with_structured_output(ReportStructure)
        try:
            report_structure = llm_with_structure.invoke(
                [
                    SystemMessage(prompt),
                    HumanMessage(state.query),
                ]
            )
            assert isinstance(report_structure, ReportStructure)
        except Exception:
            logger.exception('Exception occurred while generating the report structure.')
            raise

        report_title = f'Deep Research Report on {state.query}'
        paragraphs = []
        for idx, item in enumerate(report_structure.items):
            paragraphs.append(Paragraph(item.title, item.content, order=idx))

        logger.info(
            f'The report structure has been generated, consisting of {len(paragraphs)} paragraphs.'
        )
        for idx, paragraph in enumerate(paragraphs, 1):
            logger.info(f'\t{idx}. {paragraph["title"]}')

        return Command(
            update={
                'report_title': report_title,
                'paragraphs': paragraphs,
                'paragraph_index': 0,
            },
            goto='first_search',
        )

    def first_search(self, state: State) -> Command:
        prompt = """
You are an in-depth research assistant. You will be given the title and expected content of a paragraph from a report.

You can use a web search tool that accepts 'search_query' as a parameter.

Your task is to think about this topic and provide the best web search query to enrich your current knowledge.
"""
        llm_with_tools = self.llm.bind_tools([tavily_search], tool_choice='tavily_search')

        paragraph_index = state.paragraph_index
        paragraphs = state.paragraphs
        paragraph = paragraphs[paragraph_index]
        logger.info(f'Processing paragraph {paragraph_index}, performing first search.')

        user_prompt = f"""
Title: {paragraph.title}
Expected content: {paragraph.content}
"""
        try:
            ai_msg = llm_with_tools.invoke(
                [
                    SystemMessage(prompt),
                    HumanMessage(user_prompt),
                ]
            )
        except Exception:
            logger.exception('Exception while running first_search.')
            raise
        search_results = []
        for tool_call in ai_msg.tool_calls:
            tool_results = tavily_search.invoke(tool_call['args'])
            search_results.append(tool_results)

        logger.info(f'A total of {len(search_results)} search results found')
        paragraph.research.search_history.extend(search_results)

        return Command(update={'paragraphs': paragraphs}, goto='first_summary')

    def first_summary(self, state: State) -> Command:
        prompt = """
You are a deep research assistant. Please write a piece of content that aligns with the paragraph's theme based on the title, desired content of the target paragraph, and the information gathered from searches.

Please generate the content directly, without producing irrelevant information.
"""

        paragraph_index = state.paragraph_index
        paragraphs = state.paragraphs
        paragraph = paragraphs[paragraph_index]
        search_history = paragraph.research.search_history
        logger.info(f'Processing paragraph {paragraph_index}, performing first summary.')

        user_prompt = f"""
Title: {paragraph.title}
Expected content: {paragraph.content}\n
"""
        if len(search_history) > 0:
            user_prompt += f'Search query: {search_history[0].search_query}\n'
        for idx, search_result in enumerate(search_history):
            user_prompt += f'\tSearch result {idx}: {truncate_content(search_result.content)}'

        try:
            response = self.llm.invoke(
                [
                    SystemMessage(prompt),
                    HumanMessage(user_prompt),
                ]
            )
        except Exception:
            logger.exception('Exception while running first_summary.')
            raise
        paragraph.research.latest_summary = response.pretty_repr()
        logger.info(
            f'First summary for paragraph {paragraph_index}: {truncate_content(paragraph.research.latest_summary, 100)}'
        )

        return Command(update={'paragraphs': paragraphs}, goto='reflection')

    def reflection(self, state: State) -> Command:
        prompt = """
You are a deep research assistant, responsible for studying reports and constructing comprehensive paragraphs. You will be provided with paragraph titles, summaries of planned content, and the latest status of paragraphs you have already created.

You can use a web search tool that takes `search_query` as a parameter. Your task is to reflect on the current state of the paragraph text, consider whether any key aspects of the topic have been omitted, and provide the best web search tool query to enrich the latest state.
"""
        llm_with_tools = self.llm.bind_tools([tavily_search], tool_choice='tavily_search')

        paragraph_index = state.paragraph_index
        paragraphs = state.paragraphs
        paragraph = paragraphs[paragraph_index]
        paragraph.research.reflection_iteration += 1
        logger.info(
            f'Iterating through paragraph {paragraph_index}, currently on the {paragraph.research.reflection_iteration} iteration...'
        )

        user_prompt = f"""
Title: {paragraph.title}
Content: {paragraph.content}
Latest state: {paragraph.research.latest_summary}
"""
        try:
            ai_msg = llm_with_tools.invoke(
                [
                    SystemMessage(prompt),
                    HumanMessage(user_prompt),
                ]
            )
        except Exception:
            logger.exception('Exception while running reflection.')
            raise
        search_results = []
        for tool_call in ai_msg.tool_calls:
            tool_results = tavily_search.invoke(tool_call['args'])
            search_results.append(tool_results)

        logger.info(f'A total of {len(search_results)} search results found')
        paragraph.research.search_history.extend(search_results)

        return Command(update={'paragraphs': paragraphs}, goto='reflection_summary')

    def reflection_summary(self, state: State) -> Command:
        prompt = """
You are a deep research assistant.

You will receive search queries, search results, section titles, and the intended content of the report section you are researching.

You are iteratively refining this section, and the latest state of the section will also be provided to you.

Your task is to enrich the current latest status of the paragraph based on search results and expected content.

Do not delete key information from the latest status, try to enrich it, and only add missing information.

If you believe you have obtained sufficient information, you can terminate the iterative reflection process.
"""
        llm_with_structure = self.llm.with_structured_output(ReflectionSummary)

        paragraph_index = state.paragraph_index
        paragraphs = state.paragraphs
        paragraph = paragraphs[paragraph_index]
        reflection_iteration = paragraph.research.reflection_iteration
        search_history = paragraph.research.search_history
        logger.info(
            f'Summarizing paragraph {paragraph_index}, currently on the {paragraph.research.reflection_iteration} iteration...'
        )

        user_prompt = f"""
Title: {paragraph.title}
Content: {paragraph.content}
Paragraph latest state: {paragraph.research.latest_summary}
"""
        if len(search_history) > 0:
            user_prompt += f'Search query: {search_history[0].search_query}\n'
        for idx, search_result in enumerate(search_history):
            user_prompt += f'\tSearch result {idx}: {truncate_content(search_result.content)}'

        try:
            response = llm_with_structure.invoke(
                [
                    SystemMessage(prompt),
                    HumanMessage(user_prompt),
                ]
            )
            assert isinstance(response, ReflectionSummary)
        except Exception:
            logger.exception('Exception occurred while running reflection_summary.')
            raise

        paragraph.research.latest_summary = response.summary
        stop_reflection = response.stop_reflection
        logger.info(
            f'Summary of {reflection_iteration} iteration paragraph {paragraph_index}: {truncate_content(response.summary)}'
        )

        if stop_reflection or reflection_iteration >= self.max_reflections:
            if paragraph_index < len(paragraphs) - 1:
                goto = 'first_search'
                paragraph_index += 1
            else:
                goto = 'generate_final_report'
            paragraph.research.is_completed = True
        else:
            goto = 'reflection'

        return Command(
            update={
                'paragraphs': paragraphs,
                'paragraph_index': paragraph_index,
            },
            goto=goto,
        )

    def generate_final_report(self, state: State) -> Command:
        prompt = """
You are a deep research assistant. You have completed the research and constructed the final version of all paragraphs in the report.

You will receive the title of each paragraph after multiple rounds of iterative reflection and the latest information state.

Your task is to format the report into an aesthetically pleasing form and return it in Markdown format.

If there is no conclusion paragraph, please add a conclusion at the end of the report based on the latest status of the other paragraphs.

Use paragraph headings to create the title of the report.
"""
        user_prompt = """
Below are the title and latest state of each paragraph:
"""
        for paragraph in state.paragraphs:
            user_prompt += f"""
Title: {paragraph.title}
Latest state: {paragraph.research.latest_summary}\n
"""

        llm_with_structure = self.llm.with_structured_output(FinalReport)
        logger.info('Final report generation is in progress...')

        try:
            response = llm_with_structure.invoke(
                [
                    SystemMessage(prompt),
                    HumanMessage(user_prompt),
                ]
            )
            assert isinstance(response, FinalReport)
        except Exception:
            logger.exception('Exception occurred while running generate_final_report.')
            raise

        return Command(
            update={
                'final_report': response.report_content,
                'is_completed': True,
                'report_title': response.report_title,
            }
        )
