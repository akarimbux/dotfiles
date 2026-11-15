"""Help navigation, terminal selection, and renderer fallbacks."""
import os
from pathlib import Path
import pty
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class DothelpTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='dothelp-test-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.bin = self.root / 'bin'
        self.bin.mkdir()
        for tool in ('bash', 'awk', 'cat', 'mktemp', 'rm'):
            (self.bin / tool).symlink_to(shutil.which(tool))
        self.guide = self.root / 'guide with spaces.md'
        self.guide.write_text('''# Guide
## At your fingertips
Keyboard commands.
## Python without the fuss
```sh
## Fake heading inside code
```
Use venv.
## Keep it fresh
Update instructions.
''')
        self.env = dict(os.environ, PATH=str(self.bin),
                        DOTFILES_MANUAL=str(self.guide), TMPDIR=str(self.root))

    def mock(self, name, body):
        script = self.bin / name
        script.write_text('#!/bin/sh\n' + body + '\n')
        script.chmod(0o755)

    def run_help(self, *args, terminal=False):
        cmd = [shutil.which('bash'), str(ROOT / 'configs/dothelp.sh'), *args]
        if not terminal:
            return subprocess.run(cmd, env=self.env, text=True, capture_output=True,
                                  timeout=5)
        master, slave = pty.openpty()
        try:
            result = subprocess.run(cmd, stdin=slave, stdout=slave,
                                    stderr=subprocess.PIPE, env=self.env,
                                    text=True, timeout=5)
            os.close(slave)
            slave = None
            chunks = []
            while True:
                try:
                    chunk = os.read(master, 4096)
                except OSError:
                    break
                if not chunk:
                    break
                chunks.append(chunk)
            result.stdout = b''.join(chunks).decode()
            return result
        finally:
            os.close(master)
            if slave is not None:
                os.close(slave)

    def test_topic_alias_and_section_boundary(self):
        result = self.run_help('python')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('Use venv.', result.stdout)
        self.assertNotIn('Update instructions.', result.stdout)
        self.assertEqual(list(self.root.glob('dothelp.*')), [])

    def test_topic_works_with_bsd_style_mktemp(self):
        (self.bin / 'mktemp').unlink()
        self.mock('mktemp', '''
case "$1" in
  *XXXXXX) exec /usr/bin/mktemp "$@" ;;
  *) printf 'mktemp: template must end in XXXXXX\\n' >&2; exit 1 ;;
esac
''')
        result = self.run_help('python')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('Use venv.', result.stdout)
        self.assertEqual(list(self.root.glob('dothelp.*')), [])

    def test_renderer_failure_cleans_temporary_topic(self):
        self.mock('glow', 'exit 42')
        self.assertEqual(self.run_help('python', terminal=True).returncode, 42)
        self.assertEqual(list(self.root.glob('dothelp.*')), [])

    def test_fzf_failure_is_reported(self):
        self.mock('fzf', 'cat >/dev/null; exit 42')
        self.assertEqual(self.run_help(terminal=True).returncode, 42)

    def test_redirected_default_is_full_guide_even_with_glow(self):
        self.mock('glow', 'exit 99')
        result = self.run_help()
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, self.guide.read_text())

    def test_unknown_ambiguous_and_invalid_option(self):
        for query in ('missing', 'it', '--invalid'):
            with self.subTest(query=query):
                self.assertEqual(self.run_help(query).returncode, 2)

    def test_fzf_selection_and_glow_rendering(self):
        self.mock('fzf', "cat >/dev/null; printf 'Python without the fuss\\n'")
        self.mock('glow', 'printf "STYLED\\n"; cat "$2"')
        result = self.run_help(terminal=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('STYLED', result.stdout)
        self.assertIn('Use venv.', result.stdout)
        self.assertNotIn('Update instructions.', result.stdout)

    def test_fzf_cancel_is_success(self):
        self.mock('fzf', 'cat >/dev/null; exit 130')
        result = self.run_help(terminal=True)
        self.assertEqual(result.returncode, 0)
        self.assertNotIn('Use venv.', result.stdout)

    def test_without_fzf_opens_full_guide(self):
        result = self.run_help(terminal=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('Keyboard commands.', result.stdout)
        self.assertIn('Use venv.', result.stdout)

    def test_less_fallback(self):
        self.mock('less', 'printf "PAGER\\n"; cat "$1"')
        result = self.run_help('python', terminal=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('PAGER', result.stdout)

    @unittest.skipUnless(shutil.which('zsh'), 'Zsh is needed for integration')
    def test_shell_wrapper_follows_installed_symlink_and_passes_topic(self):
        home = self.root / 'home'
        home.mkdir()
        link = home / '.zshrc'
        link.symlink_to(ROOT / 'configs/.zshrc')
        env = dict(os.environ, HOME=str(home), ZDOTDIR=str(home),
                   PATH='/usr/bin:/bin', TEST_CONFIG=str(link))
        result = subprocess.run(
            [shutil.which('zsh'), '-f', '-c', 'source "$TEST_CONFIG"; dothelp python'],
            env=env, text=True, capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('## Python without the fuss', result.stdout)
        self.assertNotIn('## Make it yours', result.stdout)

    def test_missing_guide_and_help(self):
        self.guide.unlink()
        self.assertEqual(self.run_help('python').returncode, 1)
        self.assertEqual(self.run_help('--help').returncode, 0)


if __name__ == '__main__':
    unittest.main()
