import os
from collections import Counter
from pathlib import Path

from bob_core.schemas import (
    ClusterSummary,
    DependencyEdge,
    DependencyIntelligencePayload,
    DependencyNode,
    IntelligenceSummary,
    RoadmapItem,
)
from engine.metrics import (
    build_reverse_graph,
    compute_importance_score,
    compute_numeric_complexity,
    dependency_depth,
    detect_circular_dependencies,
    infer_architectural_layer,
    learning_reason,
    reachable_count,
    shortest_distance_to_foundation,
)
from engine.parser import analyze_repository_files

LAYER_ORDER = {
    "Configuration": 0,
    "Foundation": 1,
    "Data Model": 2,
    "Database Layer": 3,
    "Shared Utility": 4,
    "Business Logic": 5,
    "API Layer": 6,
    "Application Logic": 7,
    "UI Layer": 8,
}


def build_dependency_intelligence(repo_path: str, include_tests: bool = False) -> DependencyIntelligencePayload:
    if not os.path.isdir(repo_path):
        raise ValueError(f"Repository path does not exist: {repo_path}")

    analyses = analyze_repository_files(repo_path, include_tests=include_tests)
    graph = {file_path: analysis.imports for file_path, analysis in analyses.items()}
    reverse_graph = build_reverse_graph(graph)
    circular_dependencies = detect_circular_dependencies(graph)

    intermediate_nodes = []
    layer_counts: Counter[str] = Counter()

    for file_path, analysis in analyses.items():
        incoming_count = len(reverse_graph.get(file_path, []))
        outgoing_count = len(graph.get(file_path, []))
        downstream_impact = reachable_count(file_path, reverse_graph)
        depth = dependency_depth(file_path, graph)
        radius = shortest_distance_to_foundation(file_path, graph)
        layer = infer_architectural_layer(file_path, outgoing_count, incoming_count)
        complexity_score = compute_numeric_complexity(analysis, incoming_count, downstream_impact, depth)
        importance_score = compute_importance_score(incoming_count, outgoing_count, downstream_impact, depth)
        layer_counts[layer] += 1

        intermediate_nodes.append({
            "file_path": file_path,
            "analysis": analysis,
            "incoming_count": incoming_count,
            "outgoing_count": outgoing_count,
            "downstream_impact": downstream_impact,
            "depth": depth,
            "radius": radius,
            "layer": layer,
            "complexity_score": complexity_score,
            "importance_score": importance_score,
        })

    ordered = sorted(
        intermediate_nodes,
        key=lambda item: (
            LAYER_ORDER.get(item["layer"], 99),
            item["radius"],
            item["outgoing_count"],
            item["complexity_score"],
            -item["incoming_count"],
            item["file_path"],
        ),
    )
    order_by_file = {item["file_path"]: index + 1 for index, item in enumerate(ordered)}

    nodes: list[DependencyNode] = []
    roadmap: list[RoadmapItem] = []
    for item in intermediate_nodes:
        file_path = item["file_path"]
        analysis = item["analysis"]
        nodes.append(
            DependencyNode(
                id=file_path,
                file=file_path,
                label=Path(file_path).name,
                extension=analysis.extension,
                loc=analysis.loc,
                imports_count=len(analysis.imports),
                exports_count=len(analysis.exports),
                incoming_dependency_count=item["incoming_count"],
                outgoing_dependency_count=item["outgoing_count"],
                downstream_impact=item["downstream_impact"],
                dependency_radius=item["radius"],
                complexity_score=item["complexity_score"],
                importance_score=item["importance_score"],
                architectural_layer=item["layer"],
                recommended_learning_order=order_by_file[file_path],
                dependencies=graph.get(file_path, []),
                dependents=reverse_graph.get(file_path, []),
                symbols=analysis.symbols[:20],
            )
        )
        roadmap.append(
            RoadmapItem(
                step=order_by_file[file_path],
                file=file_path,
                architectural_layer=item["layer"],
                complexity_score=item["complexity_score"],
                dependency_radius=item["radius"],
                learning_reason=learning_reason(
                    file_path,
                    item["layer"],
                    item["incoming_count"],
                    item["outgoing_count"],
                    item["complexity_score"],
                ),
                prerequisites=graph.get(file_path, []),
            )
        )

    nodes.sort(key=lambda node: node.recommended_learning_order)
    roadmap.sort(key=lambda item: item.step)

    edges = [
        DependencyEdge(source=source, target=target)
        for source, targets in graph.items()
        for target in targets
    ]
    clusters = [
        ClusterSummary(
            layer=layer,
            files=[node.file for node in nodes if node.architectural_layer == layer],
        )
        for layer in sorted(layer_counts, key=lambda value: LAYER_ORDER.get(value, 99))
    ]

    foundational_files = [
        node.file for node in nodes
        if node.outgoing_dependency_count == 0 or node.architectural_layer in {"Configuration", "Foundation", "Data Model"}
    ][:8]
    hub_files = sorted(
        nodes,
        key=lambda node: (node.incoming_dependency_count + node.downstream_impact, node.importance_score),
        reverse=True,
    )[:5]
    risky_files = sorted(
        nodes,
        key=lambda node: (node.complexity_score, node.incoming_dependency_count, node.outgoing_dependency_count),
        reverse=True,
    )[:5]

    summary = IntelligenceSummary(
        total_files=len(nodes),
        total_edges=len(edges),
        circular_dependency_count=len(circular_dependencies),
        architectural_layers=dict(layer_counts),
        foundational_files=foundational_files,
        hub_files=[node.file for node in hub_files],
        risky_files=[node.file for node in risky_files],
    )

    return DependencyIntelligencePayload(
        repository=os.path.abspath(repo_path),
        summary=summary,
        nodes=nodes,
        edges=edges,
        roadmap=roadmap,
        clusters=clusters,
        circular_dependencies=circular_dependencies,
        adjacency=graph,
        reverse_adjacency=reverse_graph,
    )
