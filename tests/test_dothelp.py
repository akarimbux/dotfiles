"""Test topic extraction and plain output; CI exercises the real renderer."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class DothelpTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.guide = Path(temp.name) / 'guide with spaces.md'
        self.guide.write_text('## Python\n```sh\n## Example\n```\nvenv\n## Other\nDone.\n')

    def help(self, *args):
        return subprocess.run(['bash', str(ROOT / 'configs/dothelp.sh'), *args],
                              env=dict(os.environ, DOTFILES_MANUAL=str(self.guide),
                                       TMPDIR=str(self.guide.parent)),
                              capture_output=True, text=True, timeout=5)

    def test_topic_preserves_code_and_stops_at_next_heading(self):
        result = self.help('python')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('## Example', result.stdout)
        self.assertIn('venv', result.stdout)
        self.assertNotIn('## Other', result.stdout)
        self.assertEqual(list(self.guide.parent.glob('dothelp.*')), [])

    def test_redirected_default_is_complete_plain_guide(self):
        result = self.help()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, self.guide.read_text())

    def test_unknown_topic_returns_helpful_error(self):
        result = self.help('missing')
        self.assertEqual(result.returncode, 2)
        self.assertIn('Python', result.stderr)
