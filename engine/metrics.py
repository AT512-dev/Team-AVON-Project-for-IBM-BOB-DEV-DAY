import os
from collections import deque
from pathlib import Path

from engine.parser import FileAnalysis


def count_lines_of_code(file_path: str) -> int:
    if not os.path.isfile(file_path):
        return 0
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
            return sum(1 for line in file if line.strip() and not line.strip().startswith(("#", "//")))
    except OSError:
        return 0


def normalize_score(value: float, high_water_mark: float) -> int:
    if high_water_mark <= 0:
        return 0
    return max(0, min(100, round((value / high_water_mark) * 100)))


def build_reverse_graph(graph: dict[str, list[str]]) -> dict[str, list[str]]:
    reverse_graph = {file_path: [] for file_path in graph}
    for source, targets in graph.items():
        for target in targets:
            reverse_graph.setdefault(target, []).append(source)
    return {file_path: sorted(set(dependents)) for file_path, dependents in reverse_graph.items()}


def reachable_count(start: str, graph: dict[str, list[str]]) -> int:
    visited = set()
    queue = deque(graph.get(start, []))
    while queue:
        current = queue.popleft()
        if current in visited:
            continue
        visited.add(current)
        queue.extend(graph.get(current, []))
    return len(visited)


def shortest_distance_to_foundation(file_path: str, graph: dict[str, list[str]]) -> int:
    if not graph.get(file_path):
        return 0

    visited = {file_path}
    queue = deque((dependency, 1) for dependency in graph.get(file_path, []))
    while queue:
        current, distance = queue.popleft()
        if not graph.get(current):
            return distance
        for dependency in graph.get(current, []):
            if dependency not in visited:
                visited.add(dependency)
                queue.append((dependency, distance + 1))
    return 0


def dependency_depth(file_path: str, graph: dict[str, list[str]]) -> int:
    seen: set[str] = set()

    def visit(current: str, stack: set[str]) -> int:
        if current in stack:
            return 0
        stack.add(current)
        seen.add(current)
        children = graph.get(current, [])
        if not children:
            stack.remove(current)
            return 0
        depth = 1 + max(visit(child, stack) for child in children)
        stack.remove(current)
        return depth

    return visit(file_path, set())


def detect_circular_dependencies(graph: dict[str, list[str]]) -> list[list[str]]:
    cycles: list[list[str]] = []
    visiting: set[str] = set()
    visited: set[str] = set()
    stack: list[str] = []

    def visit(node: str) -> None:
        if node in visiting:
            start = stack.index(node)
            cycle = stack[start:] + [node]
            normalized = cycle[:-1]
            smallest = min(range(len(normalized)), key=lambda index: normalized[index])
            rotated = normalized[smallest:] + normalized[:smallest]
            rotated.append(rotated[0])
            if rotated not in cycles:
                cycles.append(rotated)
            return
        if node in visited:
            return

        visiting.add(node)
        stack.append(node)
        for dependency in graph.get(node, []):
            visit(dependency)
        stack.pop()
        visiting.remove(node)
        visited.add(node)

    for node in graph:
        visit(node)

    return cycles


def infer_architectural_layer(file_path: str, outgoing_count: int, incoming_count: int) -> str:
    lowered = file_path.lower()
    if any(token in lowered for token in ("config", "setting", "env", "constant")):
        return "Configuration"
    if any(token in lowered for token in ("schema", "model", "entity", "types", "interface")):
        return "Data Model"
    if any(token in lowered for token in ("database", "db", "repository", "dao", "migration")):
        return "Database Layer"
    if any(token in lowered for token in ("route", "router", "controller", "api", "endpoint")):
        return "API Layer"
    if any(token in lowered for token in ("service", "manager", "engine", "core", "usecase")):
        return "Business Logic"
    if any(token in lowered for token in ("component", "page", "view", "screen", "ui", ".tsx", ".jsx")):
        return "UI Layer"
    if outgoing_count == 0 and incoming_count > 0:
        return "Foundation"
    if incoming_count >= 3:
        return "Shared Utility"
    return "Application Logic"


def compute_numeric_complexity(
    analysis: FileAnalysis,
    incoming_count: int,
    downstream_impact: int,
    dependency_depth_value: int,
) -> int:
    loc_score = normalize_score(analysis.loc, 350) * 0.20
    import_score = normalize_score(len(analysis.imports), 12) * 0.18
    export_score = normalize_score(len(analysis.exports), 10) * 0.10
    incoming_score = normalize_score(incoming_count, 10) * 0.20
    nesting_score = normalize_score(analysis.max_nesting_depth, 8) * 0.12
    impact_score = normalize_score(downstream_impact, 20) * 0.12
    depth_score = normalize_score(dependency_depth_value, 8) * 0.08
    return max(0, min(100, round(sum((
        loc_score,
        import_score,
        export_score,
        incoming_score,
        nesting_score,
        impact_score,
        depth_score,
    )))))


def compute_importance_score(
    incoming_count: int,
    outgoing_count: int,
    downstream_impact: int,
    dependency_depth_value: int,
) -> int:
    score = (
        normalize_score(incoming_count, 12) * 0.40
        + normalize_score(downstream_impact, 20) * 0.30
        + normalize_score(outgoing_count, 12) * 0.15
        + normalize_score(dependency_depth_value, 8) * 0.15
    )
    return max(0, min(100, round(score)))


def compute_complexity(file_path: str, imports: list[str]) -> str:
    loc = count_lines_of_code(file_path)
    if len(imports) >= 7 or loc >= 300:
        return "Hard"
    if len(imports) >= 3 or loc >= 100:
        return "Medium"
    return "Easy"


def rank_files_by_importance(repo_map: dict[str, list[str]]) -> list[tuple[str, int]]:
    import_frequency: dict[str, int] = {}
    for imports in repo_map.values():
        for imported_file in imports:
            import_frequency[imported_file] = import_frequency.get(imported_file, 0) + 1

    return sorted(import_frequency.items(), key=lambda item: item[1], reverse=True)


def learning_reason(
    file_path: str,
    layer: str,
    incoming_count: int,
    outgoing_count: int,
    complexity_score: int,
) -> str:
    label = Path(file_path).name
    if outgoing_count == 0:
        return f"Start with {label} because it has no internal prerequisites and anchors the {layer.lower()}."
    if incoming_count >= 3:
        return f"Study {label} early because several modules depend on it, making it a shared architectural reference."
    if complexity_score >= 75:
        return f"Study {label} after its prerequisites because it is high-impact and carries heavier logic."
    return f"Study {label} to understand how the {layer.lower()} connects to nearby modules."
