import os

COMPLEXITY_THRESHOLDS = {
    "import_weight": {
        "medium": 3,
        "hard": 7
    },
    "loc_weight": {
        "medium": 100,
        "hard": 300
    }
}

def count_lines_of_code(file_path: str) -> int:
    if not os.path.isfile(file_path):
        estimated = hash(file_path) % 200 + 50
        return estimated
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        return sum(1 for line in lines if line.strip() and not line.strip().startswith("#"))
    except OSError:
        return 0

def score_by_imports(import_count: int) -> int:
    thresholds = COMPLEXITY_THRESHOLDS["import_weight"]
    if import_count >= thresholds["hard"]:
        return 2
    elif import_count >= thresholds["medium"]:
        return 1
    return 0

def score_by_loc(loc: int) -> int:
    thresholds = COMPLEXITY_THRESHOLDS["loc_weight"]
    if loc >= thresholds["hard"]:
        return 2
    elif loc >= thresholds["medium"]:
        return 1
    return 0

def compute_complexity(file_path: str, imports: list[str]) -> str:
    import_score = score_by_imports(len(imports))
    loc = count_lines_of_code(file_path)
    loc_score = score_by_loc(loc)
    total_score = import_score + loc_score

    if total_score >= 3:
        return "Hard"
    elif total_score >= 1:
        return "Medium"
    return "Easy"

def rank_files_by_importance(repo_map: dict[str, list[str]]) -> list[tuple[str, int]]:
    import_frequency: dict[str, int] = {}
    for imports in repo_map.values():
        for imported_file in imports:
            import_frequency[imported_file] = import_frequency.get(imported_file, 0) + 1

    ranked = sorted(import_frequency.items(), key=lambda x: x[1], reverse=True)
    return ranked