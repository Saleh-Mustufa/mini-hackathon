# Testing Skill

## Stdlib Unittest
- Use `unittest.TestCase` for all tests
- Use `unittest.main()` as test runner
- Test files named `test_*.py` are auto-discovered

## Test Structure
```python
import unittest
import tempfile
import os
from pathlib import Path

class TestFeature(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_something(self):
        result = some_function()
        self.assertEqual(result, expected)

if __name__ == "__main__":
    unittest.main()
```

## Edge Case Testing
- Test empty inputs
- Test missing files
- Test permission errors
- Test binary content
- Test non-UTF-8 content
- Test determinism (repeat runs)
- Test performance (3000+ files)
