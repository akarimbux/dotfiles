"""Check environment and Git location labels using real temporary repositories."""

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which('zsh') and shutil.which('git'), 'Requires Zsh and Git')
class PromptTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='dotfiles-prompt-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / 'my-project'
        self.repo.mkdir()
        (self.repo / 'src' / 'package').mkdir(parents=True)
        self.git('init', '-q', '-b', 'main')
        self.env = dict(os.environ, HOME=str(self.root), ZDOTDIR=str(self.root),
                        TEST_CONFIG=str(ROOT / 'configs/.zshrc'),
                        PATH='/usr/bin:/bin')
        for name in ['VIRTUAL_ENV', 'CONDA_DEFAULT_ENV']:
            self.env.pop(name, None)

    def git(self, *args):
        return subprocess.run(['git', *args], cwd=self.repo, check=True,
                              text=True, capture_output=True).stdout.strip()

    def shell(self, script, cwd=None):
        result = subprocess.run(['zsh', '-f'], input='source "$TEST_CONFIG"\n' + script,
                                cwd=cwd or self.repo, env=self.env,
                                text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result.stdout.strip()

    def test_environment_precedence_and_prompt_escaping(self):
        output = self.shell('''
CONDA_DEFAULT_ENV=science
python_env_prompt
VIRTUAL_ENV=/projects/demo%name/.venv
python_env_prompt
unset VIRTUAL_ENV CONDA_DEFAULT_ENV
python_env_prompt
''')
        self.assertEqual(output.splitlines(), [
            '%F{magenta}[py:science]%f ', '%F{magenta}[py:demo%%name/.venv]%f'])

    def test_git_location_branch_and_changes(self):
        self.git('checkout', '-qb', 'feature%test')
        clean = self.shell('git_prompt\n')
        self.assertIn('my-project%f | feature%%test', clean)
        self.assertIn('✔', clean)
        (self.repo / 'untracked').write_text('test')
        dirty = self.shell('git_prompt\n', self.repo / 'src/package')
        self.assertIn('my-project/src/package%f | feature%%test', dirty)
        self.assertIn('✗', dirty)
        self.assertEqual(self.shell('git_prompt\n', self.root), '')
