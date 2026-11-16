"""Keep installation reversible and help usable through the installed link."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class InstallTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.repo = self.root / 'checkout with spaces'
        self.repo.mkdir()
        for name in ('install.sh', 'README.md'):
            shutil.copy2(ROOT / name, self.repo / name)
        shutil.copytree(ROOT / 'configs', self.repo / 'configs')
        self.home = self.root / 'home'
        self.home.mkdir()
        self.link = self.home / '.zshrc'
        self.env = dict(os.environ, HOME=str(self.home), ZDOTDIR=str(self.home),
                        PATH='/usr/bin:/bin', skip_global_compinit='1')

    def install(self, *args, success=True):
        result = subprocess.run(['bash', str(self.repo / 'install.sh'), *args],
                                env=self.env, capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode == 0, success, result.stdout + result.stderr)

    def test_backup_repeat_and_restore(self):
        self.link.write_text('original config')
        self.install()
        self.install()
        self.assertEqual(self.link.resolve(), (self.repo / 'configs/.zshrc').resolve())
        backups = list(self.home.glob('.zshrc.backup.*'))
        self.assertEqual(len(backups), 1)
        self.link.rename(self.home / '.zshrc.dotfiles-link')
        (backups[0] / '.zshrc').rename(self.link)
        self.assertEqual(self.link.read_text(), 'original config')

    @unittest.skipUnless(shutil.which('zsh'), 'Requires Zsh')
    def test_installed_help_reads_guide_updates(self):
        self.install()
        guide = self.repo / 'README.md'
        guide.write_text(guide.read_text().replace(
            '## Python without the fuss', '## Python without the fuss\nUpdated help.'))
        result = subprocess.run(['zsh', '-ic', 'dothelp python'], cwd=self.root,
                                env=self.env, capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, '')
        self.assertIn('Updated help.', result.stdout)
        self.assertNotIn('## Make it yours', result.stdout)

    def test_dry_run_preserves_existing_config(self):
        self.link.write_text('original config')
        self.install('--dry-run')
        self.assertEqual(self.link.read_text(), 'original config')
        self.assertEqual(list(self.home.glob('.zshrc.backup.*')), [])

    def test_source_directory_cannot_be_overwritten(self):
        alias = self.root / 'source alias'
        alias.symlink_to(self.repo / 'configs', target_is_directory=True)
        self.env['ZDOTDIR'] = str(alias)
        self.install(success=False)
        source = self.repo / 'configs/.zshrc'
        self.assertFalse(source.is_symlink())
        self.assertEqual(source.read_text(), (ROOT / 'configs/.zshrc').read_text())

    def test_failed_link_restores_original(self):
        self.link.write_text('original config')
        bin_dir = self.root / 'bin'
        bin_dir.mkdir()
        fake_ln = bin_dir / 'ln'
        fake_ln.write_text('#!/bin/sh\nexit 1\n')
        fake_ln.chmod(0o755)
        self.env['PATH'] = str(bin_dir) + ':/usr/bin:/bin'
        self.install(success=False)
        self.assertEqual(self.link.read_text(), 'original config')
