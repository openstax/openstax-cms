from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class SearchSource:
    key: str
    build_results: Callable   # (get_params: QueryDict) -> unpaginated queryset or SearchResults
    to_dict: Callable         # (obj) -> dict for the response


SOURCES = {}


def register(source):
    SOURCES[source.key] = source
