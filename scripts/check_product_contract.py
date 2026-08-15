#!/usr/bin/env python3
"""Check public documentation facts against a local DJ Support checkout."""

from __future__ import annotations

import argparse
import json
import re
import tomllib
from pathlib import Path


DOCS_ROOT = Path(__file__).resolve().parents[1]
CANONICAL_PREFIX = "https://github.com/spontain112/djsupport/"
LATEST_RELEASE = re.compile(
    r"current Latest release is\s+\[`v(?P<label>\d+\.\d+\.\d+)`\]"
    r"\(https://github\.com/spontain112/djsupport/releases/tag/v(?P<tag>\d+\.\d+\.\d+)\)",
    re.IGNORECASE,
)


def load_text_files(root: Path, patterns: tuple[str, ...]) -> str:
    paths = sorted({path for pattern in patterns for path in root.rglob(pattern)})
    return "\n".join(path.read_text(encoding="utf-8") for path in paths if path.is_file())


def check_contract(product_repo: Path, contract_path: Path) -> list[str]:
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    readme = (product_repo / "README.md").read_text(encoding="utf-8")
    context = (product_repo / "CONTEXT.md").read_text(encoding="utf-8")
    cli = (product_repo / "djsupport" / "cli.py").read_text(encoding="utf-8")
    site_docs = load_text_files(DOCS_ROOT, ("*.md", "*.mdx", "*.json"))
    errors: list[str] = []

    expected_version = contract["stable_version"]
    latest = LATEST_RELEASE.search(readme)
    if not latest or latest.group("label") != expected_version or latest.group("tag") != expected_version:
        errors.append(f"stable version drift: product README latest-final declaration is not v{expected_version}")
    package_version = tomllib.loads((product_repo / "pyproject.toml").read_text())["project"]["version"]
    numeric_package = tuple(map(int, re.match(r"\d+\.\d+\.\d+", package_version).group().split(".")))
    numeric_stable = tuple(map(int, expected_version.split(".")))
    if numeric_package < numeric_stable:
        errors.append(f"stable version drift: package metadata {package_version} is behind v{expected_version}")

    for command in contract["commands"]:
        command_name = command.split()[1]
        if command not in readme:
            errors.append(f"command drift: product README does not document `{command}`")
        if not re.search(rf'@cli\.command\(["\']{re.escape(command_name)}["\']\)', cli):
            errors.append(f"command drift: CLI does not register `{command_name}`")
        if command not in site_docs:
            errors.append(f"command drift: site does not publish `{command}`")

    for term in contract["terms"]:
        if f"**{term}**:" not in context:
            errors.append(f"canonical term drift: `{term}` is missing from CONTEXT.md")

    for link in contract["source_links"]:
        if not link.startswith(CANONICAL_PREFIX):
            errors.append(f"source link drift: `{link}` is not canonical DJ Support source")
            continue
        if link not in site_docs:
            errors.append(f"source link drift: `{link}` is not referenced by the site")
        marker = "/blob/main/" if "/blob/main/" in link else "/tree/main/"
        if marker not in link or not (product_repo / link.split(marker, 1)[1]).exists():
            errors.append(f"source link drift: target does not exist for `{link}`")

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
