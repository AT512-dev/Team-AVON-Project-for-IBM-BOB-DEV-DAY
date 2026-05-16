import argparse
import json

from engine.dependency_intelligence import build_dependency_intelligence


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Compass AI dependency intelligence JSON.")
    parser.add_argument("repo_path", help="Path to the repository to analyze.")
    parser.add_argument("--include-tests", action="store_true", help="Include test/spec files in analysis.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    args = parser.parse_args()

    report = build_dependency_intelligence(args.repo_path, include_tests=args.include_tests)
    payload = report.model_dump() if hasattr(report, "model_dump") else report.dict()
    print(json.dumps(payload, indent=2 if args.pretty else None))


if __name__ == "__main__":
    main()
