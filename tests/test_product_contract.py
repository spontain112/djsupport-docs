import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "scripts" / "check_product_contract.py"


def valid_contract() -> dict:
    return {
        "stable_version": "0.5.0",
        "commands": ["djsupport first-transfer --json", "djsupport backup"],
        "terms": [
            "Transfer", "Source Selection", "Mirror", "Snapshot", "Preview",
            "Qualification Draft", "Provisional Playlist", "Approval", "Agent Client",
        ],
        "source_links": [
            "https://github.com/spontain112/djsupport/blob/main/CONTEXT.md"
        ],
    }


class ProductContractCliTests(unittest.TestCase):
    def make_product_repo(self, root: Path, contract: dict) -> Path:
        product = root / "djsupport"
        (product / "djsupport").mkdir(parents=True)
        (product / "pyproject.toml").write_text(
            '[project]\nname = "djsupport"\nversion = "0.6.0.dev0"\n', encoding="utf-8"
        )
        version = contract["stable_version"]
        (product / "README.md").write_text(
            "The current Latest release is\n"
            f"[`v{version}`](https://github.com/spontain112/djsupport/releases/tag/v{version}).\n"
            + "\n".join(f"Use `{command}`." for command in contract["commands"]),
            encoding="utf-8",
        )
        command_names = [command.split()[1] for command in contract["commands"]]
        (product / "djsupport" / "cli.py").write_text(
            "\n".join(f'@cli.command("{name}")' for name in command_names), encoding="utf-8"
        )
        (product / "CONTEXT.md").write_text(
            "\n".join(f"**{term}**:" for term in contract["terms"]), encoding="utf-8"
        )
        return product

    def run_checker(self, product: Path, contract: dict) -> subprocess.CompletedProcess[str]:
        contract_path = product.parent / "contract.json"
        contract_path.write_text(json.dumps(contract), encoding="utf-8")
        return subprocess.run(
            [sys.executable, str(CHECKER), "--product-repo", str(product), "--contract", str(contract_path)],
            cwd=ROOT, capture_output=True, text=True, check=False,
        )

    def test_matching_product_contract_passes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            contract = valid_contract()
            product = self.make_product_repo(Path(directory), contract)
            result = self.run_checker(product, contract)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("product contract matches", result.stdout)

    def test_historical_version_mention_does_not_count_as_latest(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            contract = valid_contract()
            product = self.make_product_repo(Path(directory), contract)
            readme = product / "README.md"
            readme.write_text(
                readme.read_text().replace(
                    "v0.5.0`](https://github.com/spontain112/djsupport/releases/tag/v0.5.0)",
                    "v0.6.0`](https://github.com/spontain112/djsupport/releases/tag/v0.6.0)",
                )
                + "\nHistorical release: v0.5.0.\n"
            )
            result = self.run_checker(product, contract)

        self.assertEqual(result.returncode, 1)
        self.assertIn("stable version", result.stdout)

    def test_missing_canonical_target_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            contract = valid_contract()
            contract["source_links"] = [
                "https://github.com/spontain112/djsupport/blob/main/docs/missing.md"
            ]
            product = self.make_product_repo(Path(directory), contract)
            result = self.run_checker(product, contract)

        self.assertEqual(result.returncode, 1)
        self.assertIn("target does not exist", result.stdout)

    def test_drift_reports_each_public_contract_failure(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = valid_contract()
            product = self.make_product_repo(Path(directory), fixture)
            contract = valid_contract()
            contract["stable_version"] = "0.4.0"
            contract["commands"] = ["djsupport missing-command"]
            contract["terms"] = ["Unknown Term"]
            contract["source_links"] = ["https://example.invalid/not-canonical"]
            result = self.run_checker(product, contract)

        self.assertEqual(result.returncode, 1)
        self.assertIn("stable version", result.stdout)
        self.assertIn("command", result.stdout)
        self.assertIn("canonical term", result.stdout)
        self.assertIn("source link", result.stdout)


if __name__ == "__main__":
    unittest.main()
