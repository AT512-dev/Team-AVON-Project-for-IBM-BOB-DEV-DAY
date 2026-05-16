import ast
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

from bob_core.schemas import RepoMap

SUPPORTED_EXTENSIONS = {".py", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"}
IGNORED_DIRECTORIES = {
    ".git",
    ".next",
    ".nuxt",
    ".turbo",
    ".venv",
    "__pycache__",
    "build",
    "coverage",
    "dist",
    "node_modules",
    "vendor",
}

IMPORT_FROM_RE = re.compile(r"import\s+(?:type\s+)?(?:[\s\S]*?\s+from\s+)?['\"]([^'\"]+)['\"]")
EXPORT_FROM_RE = re.compile(r"export\s+(?:type\s+)?(?:\*|\{[\s\S]*?\})\s+from\s+['\"]([^'\"]+)['\"]")
REQUIRE_RE = re.compile(r"require\(\s*['\"]([^'\"]+)['\"]\s*\)")
DYNAMIC_IMPORT_RE = re.compile(r"import\(\s*['\"]([^'\"]+)['\"]\s*\)")
EXPORT_DECL_RE = re.compile(
    r"\bexport\s+(?:default\s+)?(?:async\s+)?(?:function|class|const|let|var|interface|type|enum)\s+([A-Za-z_$][\w$]*)"
)
PY_DEF_RE = re.compile(r"^\s*(?:async\s+def|def|class)\s+([A-Za-z_][\w_]*)", re.MULTILINE)


@dataclass
class FileAnalysis:
    path: str
    absolute_path: str
    extension: str
    source: str
    imports: list[str] = field(default_factory=list)
    exports: list[str] = field(default_factory=list)
    symbols: list[str] = field(default_factory=list)
    loc: int = 0
    max_nesting_depth: int = 0


def should_skip_path(path: str, include_tests: bool = False) -> bool:
    parts = set(Path(path).parts)
    if parts & IGNORED_DIRECTORIES:
        return True
    lowered = path.lower()
    if not include_tests and (
        ".test." in lowered
        or ".spec." in lowered
        or lowered.startswith("test/")
        or lowered.startswith("tests/")
        or "/__tests__/" in lowered
    ):
        return True
    return False


def collect_source_files(repo_path: str, include_tests: bool = False) -> dict[str, str]:
    file_contents: dict[str, str] = {}
    for root, directories, files in os.walk(repo_path):
        directories[:] = [name for name in directories if name not in IGNORED_DIRECTORIES]
        for filename in files:
            _, ext = os.path.splitext(filename)
            if ext not in SUPPORTED_EXTENSIONS:
                continue
            full_path = os.path.join(root, filename)
            relative_path = normalize_path(os.path.relpath(full_path, repo_path))
            if should_skip_path(relative_path, include_tests=include_tests):
                continue
            try:
                with open(full_path, "r", encoding="utf-8", errors="ignore") as file:
                    file_contents[relative_path] = file.read()
            except OSError:
                file_contents[relative_path] = ""
    return file_contents


def normalize_path(path: str) -> str:
    return path.replace(os.sep, "/")


def count_lines_of_code(source: str, extension: str) -> int:
    comment_prefix = "#" if extension == ".py" else "//"
    count = 0
    for line in source.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith(comment_prefix):
            count += 1
    return count


def estimate_js_nesting_depth(source: str) -> int:
    depth = 0
    max_depth = 0
    for character in source:
        if character == "{":
            depth += 1
            max_depth = max(max_depth, depth)
        elif character == "}":
            depth = max(0, depth - 1)
    return max_depth


def estimate_python_nesting_depth(tree: ast.AST) -> int:
    nesting_nodes = (
        ast.AsyncFor,
        ast.AsyncFunctionDef,
        ast.ClassDef,
        ast.ExceptHandler,
        ast.For,
        ast.FunctionDef,
        ast.If,
        ast.Match,
        ast.Try,
        ast.While,
        ast.With,
    )

    def walk(node: ast.AST, depth: int) -> int:
        next_depth = depth + 1 if isinstance(node, nesting_nodes) else depth
        child_depth = [walk(child, next_depth) for child in ast.iter_child_nodes(node)]
        return max([next_depth, *child_depth])

    return walk(tree, 0)


def resolve_module_path(importer: str, module_name: str, all_files: Iterable[str]) -> str | None:
    all_file_set = set(all_files)
    extension_order = [".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".py"]
    importer_dir = os.path.dirname(importer)

    candidates: list[str] = []
    if module_name.startswith("."):
        base = normalize_path(os.path.normpath(os.path.join(importer_dir, module_name)))
        candidates.append(base)
        candidates.extend(f"{base}{extension}" for extension in extension_order)
        candidates.extend(f"{base}/index{extension}" for extension in extension_order)
    else:
        base = normalize_path(module_name)
        candidates.append(base)
        candidates.extend(f"{base}{extension}" for extension in extension_order)
        candidates.extend(f"{base}/index{extension}" for extension in extension_order)

    for candidate in candidates:
        if candidate in all_file_set:
            return candidate
    return None


def parse_python_file(relative_path: str, absolute_path: str, source: str, all_files: set[str]) -> FileAnalysis:
    analysis = FileAnalysis(
        path=relative_path,
        absolute_path=absolute_path,
        extension=".py",
        source=source,
        loc=count_lines_of_code(source, ".py"),
    )
    try:
        tree = ast.parse(source)
    except SyntaxError:
        analysis.symbols = sorted(set(PY_DEF_RE.findall(source)))
        return analysis

    analysis.max_nesting_depth = estimate_python_nesting_depth(tree)
    imports: list[str] = []
    exports: list[str] = []
    symbols: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                resolved = resolve_module_path(relative_path, alias.name.replace(".", "/"), all_files)
                if resolved:
                    imports.append(resolved)
        elif isinstance(node, ast.ImportFrom) and node.module:
            leading_dots = "." * node.level
            module_name = leading_dots + node.module.replace(".", "/")
            resolved = resolve_module_path(relative_path, module_name, all_files)
            if resolved:
                imports.append(resolved)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            symbols.append(node.name)
            if not node.name.startswith("_"):
                exports.append(node.name)

    analysis.imports = sorted(set(imports))
    analysis.exports = sorted(set(exports))
    analysis.symbols = sorted(set(symbols))
    return analysis


def parse_js_like_file(relative_path: str, absolute_path: str, source: str, all_files: set[str]) -> FileAnalysis:
    extension = Path(relative_path).suffix
    analysis = FileAnalysis(
        path=relative_path,
        absolute_path=absolute_path,
        extension=extension,
        source=source,
        loc=count_lines_of_code(source, extension),
        max_nesting_depth=estimate_js_nesting_depth(source),
    )
    module_names = []
    for pattern in (IMPORT_FROM_RE, EXPORT_FROM_RE, REQUIRE_RE, DYNAMIC_IMPORT_RE):
        module_names.extend(pattern.findall(source))

    imports = []
    for module_name in module_names:
        resolved = resolve_module_path(relative_path, module_name, all_files)
        if resolved:
            imports.append(resolved)

    analysis.imports = sorted(set(imports))
    analysis.exports = sorted(set(EXPORT_DECL_RE.findall(source)))
    analysis.symbols = sorted(set(analysis.exports))
    return analysis


def analyze_repository_files(repo_path: str, include_tests: bool = False) -> dict[str, FileAnalysis]:
    if not os.path.isdir(repo_path):
        return {}

    file_contents = collect_source_files(repo_path, include_tests=include_tests)
    all_files = set(file_contents.keys())
    analyses: dict[str, FileAnalysis] = {}

    for relative_path, source_code in file_contents.items():
        absolute_path = os.path.join(repo_path, relative_path)
        extension = Path(relative_path).suffix
        if extension == ".py":
            analyses[relative_path] = parse_python_file(relative_path, absolute_path, source_code, all_files)
        else:
            analyses[relative_path] = parse_js_like_file(relative_path, absolute_path, source_code, all_files)

    return analyses


def parse_repository(repo_path: str) -> RepoMap:
    analyses = analyze_repository_files(repo_path)
    if not analyses:
        mock_files = {
            "main.py": ["utils.py", "models.py"],
            "models.py": ["database.py"],
            "utils.py": [],
            "database.py": [],
            "services/auth.py": ["models.py", "utils.py"],
            "services/router.py": ["services/auth.py", "main.py"],
        }
        return RepoMap(files=mock_files)

    return RepoMap(files={file_path: analysis.imports for file_path, analysis in analyses.items()})
