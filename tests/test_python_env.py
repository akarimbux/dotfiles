"""Exercise the shell helper with a fake uv; no Python downloads needed."""

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which('zsh'), 'Zsh is needed for environment helper tests')
class PythonEnvTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='dotfiles-python-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.bin = self.root / 'bin'
        self.bin.mkdir()
        uv = self.bin / 'uv'
        uv.write_text('''#!/bin/sh
if [ "$1" = venv ]; then
  printf '%s\\n' "$*" >> "$TEST_LOG"
  [ "${FAIL_UV:-0}" = 0 ] || exit 7
  mkdir -p .venv/bin
  printf 'export TEST_ACTIVATED=yes\\n' > .venv/bin/activate
fi
''')
        uv.chmod(0o755)
        self.log = self.root / 'uv.log'
        self.env = dict(os.environ, HOME=str(self.root), PATH=str(self.bin) + ':/usr/bin:/bin',
                        ZDOTDIR=str(self.root), TEST_LOG=str(self.log),
                        TEST_CONFIG=str(ROOT / 'configs/.zshrc'))

    def run_shell(self, script):
        result = subprocess.run(['zsh', '-f'], input='source "$TEST_CONFIG"\n' + script,
                                text=True, env=self.env, cwd=self.root,
                                capture_output=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_create_with_version_activate_and_reuse(self):
        self.run_shell('''
[[ ! -e .venv ]] || exit 1
venv 3.13 || exit 2
[[ $TEST_ACTIVATED == yes ]] || exit 3
unset TEST_ACTIVATED
venv || exit 4
[[ $TEST_ACTIVATED == yes ]] || exit 5
''')
        self.assertEqual(self.log.read_text(), 'venv --python 3.13 .venv\n')

    def test_default_environment_and_existing_version_guard(self):
        self.run_shell('''
venv || exit 1
venv 3.12 && exit 2
exit 0
''')
        self.assertEqual(self.log.read_text(), 'venv .venv\n')

    def test_failed_creation_is_not_activated(self):
        self.env['FAIL_UV'] = '1'
        self.run_shell('''
venv && exit 1
[[ -z $TEST_ACTIVATED && ! -e .venv ]] || exit 2
''')

    def test_existing_invalid_environment_is_preserved(self):
        (self.root / '.venv').write_text('keep me')
        self.run_shell('venv && exit 1\nexit 0\n')
        self.assertEqual((self.root / '.venv').read_text(), 'keep me')
        self.assertFalse(self.log.exists())

    def test_missing_uv_is_reported(self):
        (self.bin / 'uv').unlink()
        self.run_shell('venv && exit 1\nexit 0\n')
        self.assertFalse((self.root / '.venv').exists())


if __name__ == '__main__':
    unittest.main()
