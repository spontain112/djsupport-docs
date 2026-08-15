#!/usr/bin/env python3
"""Check public documentation facts against a local DJ Support checkout."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


DOCS_ROOT = Path(__file__).resolve().parents[1]
CANONICAL_PREFIX = "https://github.com/spontain112/djsupport/"


def load_text_files(root: Path, patterns: tuple[str, ...]) -> str:
    paths = sorted({path for pattern in patterns for path in root.rglob(pattern)})
    return "\n".join(path.read_text(encoding="utf-8") for path in paths if path.is_file())


def check_contract(product_repo: Path, contract_path: Path) -> list[str]:
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    readme = (product_repo / "README.md").read_text(encoding="utf-8")
    context = (product_repo / "CONTEXT.md").read_text(encoding="utf-8")
    product_docs = load_text_files(product_repo, ("*.md", "*.py"))
    site_docs = load_text_files(DOCS_ROOT, ("*.md", "*.mdx", "*.json"))
    errors: list[str] = []

    expected_version = contract["stable_version"]
    if f"releases/tag/v{expected_version}" not in readme and f"v{expected_version}" not in readme:
        errors.append(f"stable version drift: product README does not declare v{expected_version}")

    for command in contract["commands"]:
        if command not in product_docs:
            errors.append(f"command drift: product does not document `{command}`")
        if command not in site_docs:
            errors.append(f"command drift: site does not publish `{command}`")

    for term in contract["terms"]:
        if f"**{term}**:" not in context:
            errors.append(f"canonical term drift: `{term}` is missing from CONTEXT.md")

    for link in contract["source_links"]:
        if not link.startswith(CANONICAL_PREFIX):
            errors.append(f"source link drift: `{link}` is not canonical DJ Support source")
        elif link not in site_docs:
            errors.append(f"source link drift: `{link}` is not referenced by the site")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--product-repo", type=Path, required=True)
    parser.add_argument(
        "--contract", type=Path, default=DOCS_ROOT / "product-contract.json"
    )
    args = parser.parse_args()

    errors = check_contract(args.product_repo.resolve(), args.contract.resolve())
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("DJ Support product contract matches the public documentation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
