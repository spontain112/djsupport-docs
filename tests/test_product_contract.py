import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "scripts" / "check_product_contract.py"


class ProductContractCliTests(unittest.TestCase):
    def make_product_repo(self, root: Path) -> Path:
        product = root / "djsupport"
        product.mkdir()
        (product / "pyproject.toml").write_text(
            '[project]\nname = "djsupport"\nversion = "0.6.0.dev0"\n', encoding="utf-8"
        )
        (product / "README.md").write_text(
            "Latest final GitHub Release is v0.5.0.\n"
            "Use `djsupport first-transfer --json`.\n"
            "Use `djsupport backup`.\n",
            encoding="utf-8",
        )
        (product / "CONTEXT.md").write_text(
            "\n".join(
                f"**{term}**:" for term in (
                    "Transfer",
                    "Source Selection",
                    "Mirror",
                    "Snapshot",
                    "Preview",
                    "Qualification Draft",
                    "Provisional Playlist",
                    "Approval",
                    "Agent Client",
                )
            ),
            encoding="utf-8",
        )
        return product

    def run_checker(self, product: Path, contract: dict) -> subprocess.CompletedProcess[str]:
        contract_path = product.parent / "contract.json"
        contract_path.write_text(json.dumps(contract), encoding="utf-8")
        return subprocess.run(
            [sys.executable, str(CHECKER), "--product-repo", str(product), "--contract", str(contract_path)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

    def valid_contract(self) -> dict:
        return {
            "stable_version": "0.5.0",
            "commands": ["djsupport first-transfer --json", "djsupport backup"],
            "terms": [
                "Transfer",
                "Source Selection",
                "Mirror",
                "Snapshot",
                "Preview",
                "Qualification Draft",
                "Provisional Playlist",
                "Approval",
                "Agent Client",
            ],
            "source_links": [
                "https://github.com/spontain112/djsupport/blob/main/CONTEXT.md"
            ],
        }

    def test_matching_product_contract_passes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            product = self.make_product_repo(Path(directory))
            result = self.run_checker(product, self.valid_contract())

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("product contract matches", result.stdout)

    def test_drift_reports_each_public_contract_failure(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            product = self.make_product_repo(Path(directory))
            contract = self.valid_contract()
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
