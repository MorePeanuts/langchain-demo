from dataclasses import dataclass, field
from .schema import ReportStructure
from .tools import SearchResult


@dataclass
class Research:
    search_history: list[SearchResult] = field(default_factory=list)
    latest_summary: str = ''
    reflection_iteration: int = 0
    is_completed: bool = False


@dataclass
class Paragraph:
    title: str = ''
    content: str = ''
    research: Research = field(default_factory=Research)
    order: int = 0


@dataclass
class State:
    query: str = ''
    report_title: str = ''
    paragraphs: list[Paragraph] = field(default_factory=list)
    paragraph_index: int = 0
    final_report: str = ''
    is_completed: bool = False
