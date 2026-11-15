"""Installer checks using temporary targets and mocked package managers."""

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
BASH = shutil.which("bash")


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="dotfiles-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / "checkout with spaces"
        self.repo.mkdir()
        shutil.copy2(ROOT / 'install.sh', self.repo / 'install.sh')
        shutil.copy2(ROOT / 'README.md', self.repo / 'README.md')
        shutil.copytree(ROOT / 'configs', self.repo / 'configs')
        self.target = self.root / "shell config"
        self.target.mkdir()
        self.link = self.target / ".zshrc"
        self.source = self.repo / "configs" / ".zshrc"
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self.log = self.root / "commands.log"
        self.env = dict(os.environ, HOME=str(self.root), ZDOTDIR=str(self.target),
                        PATH=str(self.bin) + os.pathsep + '/usr/bin:/bin',
                        UV_INSTALL_DIR=str(self.root / 'uv bin'), TMPDIR=str(self.root),
                        TEST_LOG=str(self.log))
        self.mock("uname", "printf 'Linux\\n'\n")
        self.mock("apt-get", 'printf "apt-get %s\\n" "$*" >> "$TEST_LOG"\n')
        self.mock("apt-cache", '[ "$2" != eza ]\n')
        self.mock("sudo", 'exec "$@"\n')
        self.mock("curl", '''
printf 'curl\\n' >> "$TEST_LOG"
while [ "$1" != -o ]; do shift; done
shift
cat > "$1" <<'INSTALLER'
printf 'uv-installer %s\\n' "$UV_NO_MODIFY_PATH" >> "$TEST_LOG"
mkdir -p "$UV_INSTALL_DIR"
printf '#!/bin/sh\\nexit 0\\n' > "$UV_INSTALL_DIR/uv"
chmod +x "$UV_INSTALL_DIR/uv"
INSTALLER
''')

    def mock(self, name, body):
        file = self.bin / name
        file.write_text("#!/bin/sh\n" + body)
        file.chmod(0o755)

    def run_install(self, *args, success=True):
        result = subprocess.run([BASH, str(self.repo / "install.sh"), *args],
                                env=self.env, text=True, capture_output=True,
                                cwd=self.root)
        if success:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def backups(self):
        return list(self.target.glob(".zshrc.backup.*"))

    def test_fresh_install_and_rerun(self):
        self.run_install()
        self.assertEqual(self.link.resolve(), self.source.resolve())
        self.run_install()
        self.assertEqual(self.backups(), [])

    def test_install_into_source_directory_keeps_source(self):
        original = self.source.read_text()
        alias = self.root / 'source alias'
        alias.symlink_to(self.repo / 'configs', target_is_directory=True)
        for target in (self.repo / 'configs', alias):
            with self.subTest(target=target):
                self.env['ZDOTDIR'] = str(target)
                self.run_install('--with-tools', success=False)
                self.assertFalse(self.source.is_symlink())
                self.assertEqual(self.source.read_text(), original)
                self.assertFalse(self.log.exists())

    def test_existing_config_is_backed_up_and_local_settings_preserved(self):
        self.link.write_text("original config\n")
        local = self.target / ".zshrc.local"
        local.write_text("local settings\n")
        self.run_install()
        self.assertEqual(len(self.backups()), 1)
        self.assertEqual((self.backups()[0] / ".zshrc").read_text(), "original config\n")
        self.assertEqual(local.read_text(), "local settings\n")
        self.assertEqual(self.link.resolve(), self.source.resolve())

    def test_dangling_symlink_is_preserved(self):
        self.link.symlink_to("missing-old-config")
        self.run_install()
        self.assertEqual((self.backups()[0] / ".zshrc").readlink(), Path("missing-old-config"))

    def test_dry_run_does_not_mutate_or_install(self):
        self.link.write_text("keep me")
        self.run_install("--dry-run", "--with-tools")
        self.assertEqual(self.link.read_text(), "keep me")
        self.assertEqual(self.backups(), [])
        self.assertFalse(self.log.exists())

    def test_missing_target_directory(self):
        self.target.rmdir()
        self.run_install("--dry-run")
        self.assertFalse(self.target.exists())
        self.run_install()
        self.assertTrue(self.link.is_symlink())

    def test_directory_and_invalid_option_are_rejected(self):
        self.link.mkdir()
        self.run_install(success=False)
        self.assertTrue(self.link.is_dir())
        self.run_install("--unknown", success=False)
        self.assertEqual(self.backups(), [])

    def test_missing_source_is_rejected(self):
        self.source.unlink()
        self.run_install(success=False)
        self.assertFalse(self.link.exists())

    def test_missing_help_files_leave_existing_config_untouched(self):
        self.link.write_text('original')
        for file in (self.repo / 'README.md', self.repo / 'configs/dothelp.sh'):
            with self.subTest(file=file):
                contents = file.read_text()
                file.unlink()
                result = self.run_install('--with-tools', success=False)
                self.assertIn(str(file), result.stderr)
                self.assertEqual(self.link.read_text(), 'original')
                self.assertEqual(self.backups(), [])
                self.assertFalse(self.log.exists())
                file.write_text(contents)

    @unittest.skipUnless(shutil.which('zsh'), 'Requires Zsh')
    def test_fresh_install_opens_readme_from_another_directory(self):
        self.run_install()
        result = subprocess.run(
            [shutil.which('zsh'), '-f', '-c', 'source "$ZDOTDIR/.zshrc"; dothelp python'],
            cwd=self.root, env=self.env, text=True, capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('## Python without the fuss', result.stdout)
        self.assertNotIn('## Make it yours', result.stdout)

    @unittest.skipUnless(shutil.which('zsh'), 'Requires Zsh')
    def test_new_shell_reads_guide_updates_without_reinstalling(self):
        self.run_install()
        guide = self.repo / 'README.md'
        guide.write_text(guide.read_text().replace(
            '## Python without the fuss', '## Python without the fuss\n\nUpdated guide marker.'))
        result = subprocess.run(
            [shutil.which('zsh'), '-ic', 'dothelp python'],
            cwd=self.root, env=self.env, text=True, capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('Updated guide marker.', result.stdout)
        self.assertIn('## Python without the fuss', result.stdout)
        self.assertNotIn('## Make it yours', result.stdout)

    @unittest.skipUnless(shutil.which('zsh'), 'Requires Zsh')
    def test_documented_restore_recovers_previous_shell(self):
        self.link.write_text('export RESTORED_CONFIG=yes\n')
        self.run_install()
        backup = self.backups()[0] / '.zshrc'
        subprocess.run(['mv', '-i', str(self.link), str(self.target / '.zshrc.dotfiles-link')],
                       check=True, capture_output=True)
        subprocess.run(['mv', '-i', str(backup), str(self.link)],
                       check=True, capture_output=True)
        result = subprocess.run(
            [shutil.which('zsh'), '-ic', 'print -r -- "$RESTORED_CONFIG"'],
            cwd=self.root, env=self.env, text=True, capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), 'yes')
        self.assertFalse(self.link.is_symlink())

    @unittest.skipUnless(shutil.which('zsh'), 'Requires Zsh')
    def test_older_fzf_shell_integration_loads_after_install(self):
        self.mock('fzf', 'exit 1\n')
        shell_dir = self.root / '.fzf/shell'
        shell_dir.mkdir(parents=True)
        (shell_dir / 'key-bindings.zsh').write_text('export FZF_FALLBACK_LOADED=yes\n')
        self.run_install()
        master, slave = os.openpty()
        try:
            result = subprocess.run(
                [shutil.which('zsh'), '-ic', 'dothelp shortcuts; print -r -- "$FZF_FALLBACK_LOADED"'],
                stdin=slave, cwd=self.root, env=self.env, text=True, capture_output=True, timeout=10)
        finally:
            os.close(slave)
            os.close(master)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('## At your fingertips', result.stdout)
        self.assertTrue(result.stdout.rstrip().endswith('yes'))

    def test_unavailable_glow_is_optional(self):
        self.mock('apt-cache', '[ "$2" != glow ]\n')
        result = self.run_install('--with-tools')
        self.assertIn('Skipping unavailable package: glow', result.stderr)
        self.assertNotIn(' glow ', self.log.read_text())
        self.assertTrue(self.link.is_symlink())

    def test_apt_skips_unavailable_package(self):
        result = self.run_install("--with-tools")
        commands = self.log.read_text()
        self.assertIn("apt-get update", commands)
        self.assertIn("apt-get install -y zsh git jq fzf glow zoxide", commands)
        self.assertNotIn(" eza", commands)
        self.assertIn("Skipping unavailable package: eza", result.stderr)

    def test_homebrew_install(self):
        self.mock("uname", "printf 'Darwin\\n'\n")
        self.mock("brew", 'printf "brew %s\\n" "$*" >> "$TEST_LOG"\n')
        self.run_install("--with-tools")
        self.assertIn("brew install zsh git eza jq fzf glow zoxide", self.log.read_text())
        self.assertIn("zsh-syntax-highlighting uv", self.log.read_text())

    def test_uv_installed_without_editing_shell_files(self):
        self.run_install("--with-tools")
        self.assertIn("uv-installer 1", self.log.read_text())
        self.assertTrue((Path(self.env['UV_INSTALL_DIR']) / 'uv').is_file())

    def test_existing_uv_is_kept(self):
        self.mock("uv", "exit 0\n")
        self.run_install("--with-tools")
        self.assertNotIn("curl", self.log.read_text().splitlines())

    def test_failed_uv_download_leaves_existing_config_intact(self):
        self.link.write_text('original')
        self.mock("curl", "exit 1\n")
        self.run_install("--with-tools", success=False)
        self.assertEqual(self.link.read_text(), 'original')
        self.assertEqual(self.backups(), [])
        self.assertEqual(list(self.root.glob('dotfiles-uv.*')), [])

    def test_failed_uv_installer_cleans_download_and_preserves_config(self):
        self.link.write_text('original')
        self.mock('curl', """
while [ "$1" != -o ]; do shift; done
shift
printf 'exit 1\\n' > "$1"
""")
        self.run_install('--with-tools', success=False)
        self.assertEqual(self.link.read_text(), 'original')
        self.assertEqual(list(self.root.glob('dotfiles-uv.*')), [])
        self.assertEqual(self.backups(), [])

    def test_package_failure_leaves_existing_config_intact(self):
        self.link.write_text("original")
        self.mock("apt-get", "exit 1\n")
        self.run_install("--with-tools", success=False)
        self.assertEqual(self.link.read_text(), "original")
        self.assertEqual(self.backups(), [])

    def test_link_failure_restores_backup(self):
        self.link.write_text("original")
        self.mock("ln", "exit 1\n")
        self.run_install(success=False)
        self.assertEqual(self.link.read_text(), "original")


if __name__ == "__main__":
    unittest.main()
