import unittest
from asset_codes import valid_asset_code

class AssetCodeTests(unittest.TestCase):
    def test_valid_codes(self):
        for value in ["AST-0001", "AST-9999"]:
            with self.subTest(value=value):
                self.assertTrue(valid_asset_code(value))

    def test_invalid_codes(self):
        for value in ["", "ast-0001", "AST-123", "AST-12345",
                      "AST-ABCD", " AST-0001"]:
            with self.subTest(value=value):
                self.assertFalse(valid_asset_code(value))

    def test_non_string_values(self):
        for value in [None, 1234]:
            with self.subTest(value=value):
                self.assertFalse(valid_asset_code(value))

    def test_custom_symbols(self):
        for value in ["AST-####", "AST-12@4"]:
            with self.subTest(value=value):
                self.assertFalse(valid_asset_code(value))

if __name__ == "__main__":
    unittest.main()
