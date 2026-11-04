import importlib.util
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RETRIEVAL_DIR = PROJECT_ROOT / "src/retrieval"

def load_module(filename, module_name):
    """Load an existing retrieval module."""
    path = RETRIEVAL_DIR / filename
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestVerifiedMedicationRetrieval(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Load shared modules and data once for all tests."""
        cls.matching = load_module(
            "02_medication_name_matching.py",
            "medication_matching",
        )
        cls.recognition = load_module(
            "06_medication_entity_recognition.py",
            "medication_recognition",
        )
        cls.resolver = load_module(
            "08_medication_candidate_resolution.py",
            "medication_candidate_resolution",
        )
        cls.verification = load_module(
            "09_medication_identity_verification.py",
            "medication_identity_verification",
        )
        cls.retrieval = load_module(
            "10_verified_medication_retrieval.py",
            "verified_medication_retrieval",
        )

        cls.medications = cls.matching.load_medications()
        cls.document_index = cls.retrieval.load_document_index()

    def prepare(self, query):
        """Prepare candidate verification for a query."""
        return self.verification.prepare_verification(
            query,
            self.resolver,
            self.medications,
            self.matching,
            self.recognition,
        )

    def confirm(self, query, selected_ids):
        """Simulate explicit selection of offered candidates."""
        prepared = self.prepare(query)

        return self.verification.confirm_medications(
            prepared,
            selected_ids,
        )

    def test_01_exact_match_requires_confirmation(self):
        """Exact name matches must still require confirmation."""
        prepared = self.prepare("loratadine")

        self.assertEqual(prepared["status"], "name_matched")
        self.assertTrue(prepared["requires_user_confirmation"])
        self.assertEqual(prepared["selected_medications"], [])

    def test_02_fuzzy_suggestion_requires_confirmation(self):
        """Fuzzy suggestions must not be automatically confirmed."""
        prepared = self.prepare("loratadin")

        self.assertEqual(
            prepared["status"],
            "candidate_suggested",
        )
        self.assertTrue(prepared["requires_user_confirmation"])
        self.assertEqual(prepared["selected_medications"], [])

        candidate_names = [
            candidate["name"]
            for candidate in prepared["candidates"]
        ]

        self.assertIn("loratadine", candidate_names)

    def test_03_retrieval_without_confirmation_is_blocked(self):
        """Retrieval must reject unconfirmed medication identities."""
        prepared = self.prepare("paracetamol")

        with self.assertRaises(ValueError):
            self.retrieval.retrieve_verified_medications(
                prepared,
                self.document_index,
            )

    def test_04_invalid_candidate_selection_is_rejected(self):
        """Users cannot select document IDs outside offered candidates."""
        prepared = self.prepare("loratadine")

        with self.assertRaises(ValueError):
            self.verification.confirm_medications(
                prepared,
                ["TGA_99999"],
            )

    def test_05_empty_selection_is_rejected(self):
        """Confirmation requires at least one selected candidate."""
        prepared = self.prepare("loratadine")

        with self.assertRaises(ValueError):
            self.verification.confirm_medications(
                prepared,
                [],
            )

    def test_06_multiple_medications_are_retrieved(self):
        """Multiple confirmed medications must remain separate."""
        confirmed = self.confirm(
            "Can I take paracetamol and ibuprofen during pregnancy?",
            ["TGA_01250", "TGA_00831"],
        )

        results = self.retrieval.retrieve_verified_medications(
            confirmed,
            self.document_index,
        )

        returned_ids = {
            result["document_id"]
            for result in results
        }

        self.assertEqual(
            returned_ids,
            {"TGA_01250", "TGA_00831"},
        )
        self.assertEqual(len(results), 2)

    def test_07_missing_safety_statement_is_preserved(self):
        """Missing statements must not be replaced with safety claims."""
        confirmed = self.confirm(
            "loratadine",
            ["TGA_01000"],
        )

        results = self.retrieval.retrieve_verified_medications(
            confirmed,
            self.document_index,
        )

        self.assertEqual(len(results), 1)
        self.assertFalse(
            results[0]["safety_statement_available"]
        )
        self.assertIsNone(results[0]["safety_statement"])

    def test_08_missing_document_is_rejected(self):
        """Retrieval must reject IDs missing from the document index."""
        confirmed = self.confirm(
            "paracetamol",
            ["TGA_01250"],
        )

        incomplete_index = dict(self.document_index)
        incomplete_index.pop("TGA_01250")

        with self.assertRaises(KeyError):
            self.retrieval.retrieve_verified_medications(
                confirmed,
                incomplete_index,
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
