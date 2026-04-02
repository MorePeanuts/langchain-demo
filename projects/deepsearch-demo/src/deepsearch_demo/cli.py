from pathlib import Path
from deepsearch_demo.agents import DeepSearchAgent
from typing import Annotated
from typer import Typer, Argument


app = Typer(name='DeepSearchAgent-Demo', help='')


@app.command()
def research():
    print('hello world!')


@app.command()
def plot_graph(path: Annotated[str | None, Argument(help='')] = None):
    agent = DeepSearchAgent()
    if path is None:
        agent.plot_graph(Path(__file__).parents[2] / 'graph.png')
    else:
        agent.plot_graph(Path(path))


def main():
    print('Hello from DeepSearchAgent-Demo!')
    app()
