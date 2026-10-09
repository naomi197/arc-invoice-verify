import importlib.util
import unittest
from pathlib import Path

class AppImport(unittest.TestCase):
    def test_module_import_is_safe(self):
        path=Path(__file__).parents[1]/"app.py"
        spec=importlib.util.spec_from_file_location("arc_app_test",path)
        module=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertTrue(callable(module.main))

if __name__ == "__main__": unittest.main()
