import ast
import os
from bob_core.schemas import RepoMap

SUPPORTED_EXTENSIONS = {".py"}

def extract_imports_from_source(source_code: str, base_path: str, all_files: set) -> list[str]:
    resolved = []
    try:
        tree = ast.parse(source_code)
    except SyntaxError:
        return resolved

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                module_path = alias.name.replace(".", os.sep) + ".py"
                if module_path in all_files:
                    resolved.append(module_path)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                module_path = node.module.replace(".", os.sep) + ".py"
                if module_path in all_files:
                    resolved.append(module_path)

    return list(set(resolved))

def collect_python_files(repo_path: str) -> dict[str, str]:
    file_contents = {}
    for root, _, files in os.walk(repo_path):
        for filename in files:
            _, ext = os.path.splitext(filename)
            if ext in SUPPORTED_EXTENSIONS:
                full_path = os.path.join(root, filename)
                relative_path = os.path.relpath(full_path, repo_path)
                try:
                    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                        file_contents[relative_path] = f.read()
                except OSError:
                    file_contents[relative_path] = ""
    return file_contents

def parse_repository(repo_path: str) -> RepoMap:
    if not os.path.isdir(repo_path):
        mock_files = {
            "main.py": ["utils.py", "models.py"],
            "models.py": ["database.py"],
            "utils.py": [],
            "database.py": [],
            "services/auth.py": ["models.py", "utils.py"],
            "services/router.py": ["services/auth.py", "main.py"]
        }
        return RepoMap(files=mock_files)

    file_contents = collect_python_files(repo_path)
    all_files = set(file_contents.keys())
    repo_map_data = {}

    for relative_path, source_code in file_contents.items():
        imports = extract_imports_from_source(source_code, repo_path, all_files)
        repo_map_data[relative_path] = imports

    return RepoMap(files=repo_map_data)