from typer import Typer, Argument, Option
from typing import Annotated


app = Typer(name='ChatBot', help='A Chatbot Agent for Research and Architecture Exploration')


@app.command()
def run(
    cont: Annotated[
        bool,
        Option(
            '--continue',
            '-c',
            help='Continue the most recent conversation in the current directory',
        ),
    ] = False,
    resume: Annotated[
        bool,
        Option(
            '--resume',
            '-r',
            help='Resume a conversation by session ID, or open interactive picker with optional search term',
        ),
    ] = False,
):
    print('Hello from ChatBot!')


def main():
    app()
