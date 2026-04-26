# Agent Lab

Personal collection of explorations, experiments, and prototypes in the Agentic Workflow domain.

## Overview

This project serves as a learning platform for understanding and building intelligent agents using LangChain and related libraries. It combines both example explorations of library usage and practical agent implementations.

## Project Structure

```
agent-lab/
├── langchain-examples/     # Examples exploring LangChain library usage
├── langgraph-examples/     # Examples exploring LangGraph library usage
├── deepagent-examples/     # Examples exploring DeepAgent library usage
├── projects/               # Practical agent demo projects
│   ├── deepsearch-demo/    # Deep search agent demo
│   └── dataagent-demo/     # Data agent demo
├── pyproject.toml          # Workspace configuration
└── README.md               # This file
```

### Examples Directories

The `*-examples` directories contain exploratory code for understanding how to use various libraries in the LangChain ecosystem:

- `langchain-examples/` - Core LangChain functionality (models, prompts, chains, agents, middleware)
- `langgraph-examples/` - State graph-based agent workflows
- `deepagent-examples/` - DeepAgent framework usage

### Projects Directory

The `projects/` directory contains complete, runnable agent demo implementations that showcase real-world patterns and use cases.

## Getting Started

This project uses [uv](https://github.com/astral-sh/uv) for dependency management and virtual environment handling.

### Prerequisites

- Python 3.12+
- uv

### Installation

1. Clone the repository
2. Sync the workspace:

```bash
uv sync
```

### Optional Dependencies

Demo projects are defined as optional dependencies. Install them using extras:

```bash
# Install specific demo projects
uv sync --extra deepsearch
uv sync --extra dataagent

# Install multiple demo projects
uv sync --extra deepsearch --extra dataagent

# Install all demo projects
uv sync --all-extras
```

## Usage

### Running Demo Projects

Once a demo project is installed via extras, you can run it using:

```bash
uv run deepsearch-demo
uv run dataagent-demo
```

### Running Examples

Example scripts can be run directly:

```bash
uv run langchain-examples/model_stream_output.py
```
