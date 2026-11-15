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

    def test_no_environment_and_no_repository(self):
        self.assertEqual(self.shell('python_env_prompt; git_prompt\n', self.root), '')

    def test_environment_changes_are_reflected_immediately(self):
        output = self.shell('''
VIRTUAL_ENV=/projects/demo/.venv
python_env_prompt
VIRTUAL_ENV=/envs/analysis
python_env_prompt
unset VIRTUAL_ENV
python_env_prompt
''')
        self.assertEqual(output.splitlines(), [
            '%F{magenta}[py:demo/.venv]%f ', '%F{magenta}[py:analysis]%f'])

    def test_conda_and_virtualenv_precedence(self):
        output = self.shell('''
CONDA_DEFAULT_ENV=science
python_env_prompt
VIRTUAL_ENV=/projects/demo/.venv
python_env_prompt
''')
        self.assertIn('[py:science]', output)
        self.assertIn('[py:demo/.venv]', output)

    def test_root_branch_and_clean_status(self):
        output = self.shell('git_prompt\n')
        self.assertIn('my-project%f | main', output)
        self.assertIn('✔', output)

    def test_nested_location_and_dirty_status(self):
        (self.repo / 'untracked').write_text('test')
        output = self.shell('git_prompt\n', self.repo / 'src' / 'package')
        self.assertIn('my-project/src/package%f | main', output)
        self.assertIn('✗', output)

    def test_detached_head_and_worktree(self):
        self.git('-c', 'user.name=Test', '-c', 'user.email=test@example.invalid',
                 'commit', '--allow-empty', '-qm', 'initial')
        self.git('checkout', '-q', '--detach')
        self.assertIn('detached@' + self.git('rev-parse', '--short', 'HEAD'),
                      self.shell('git_prompt\n'))
        worktree = self.root / 'other-worktree'
        self.git('worktree', 'add', '-qb', 'feature', str(worktree))
        self.assertIn('other-worktree%f | feature', self.shell('git_prompt\n', worktree))

    def test_percent_signs_are_escaped(self):
        self.git('checkout', '-qb', 'feature%test')
        output = self.shell('VIRTUAL_ENV=/envs/test%env\npython_env_prompt\ngit_prompt\n')
        self.assertIn('test%%env', output)
        self.assertIn('feature%%test', output)


if __name__ == '__main__':
    unittest.main()
