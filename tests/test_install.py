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
        shutil.copytree(ROOT, self.repo, ignore=shutil.ignore_patterns("__pycache__"))
        self.target = self.root / "shell config"
        self.target.mkdir()
        self.link = self.target / ".zshrc"
        self.source = self.repo / "configs" / ".zshrc"
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self.log = self.root / "commands.log"
        self.env = dict(os.environ, ZDOTDIR=str(self.target),
                        PATH=str(self.bin) + os.pathsep + '/usr/bin:/bin',
                        UV_INSTALL_DIR=str(self.root / 'uv bin'),
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
        self.assertEqual(self.link.readlink(), self.source)
        self.run_install()
        self.assertEqual(self.backups(), [])

    def test_existing_config_is_backed_up_and_local_settings_preserved(self):
        self.link.write_text("original config\n")
        local = self.target / ".zshrc.local"
        local.write_text("local settings\n")
        self.run_install()
        self.assertEqual(len(self.backups()), 1)
        self.assertEqual((self.backups()[0] / ".zshrc").read_text(), "original config\n")
        self.assertEqual(local.read_text(), "local settings\n")
        self.assertEqual(self.link.readlink(), self.source)

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

    def test_apt_skips_unavailable_package(self):
        result = self.run_install("--with-tools")
        commands = self.log.read_text()
        self.assertIn("apt-get update", commands)
        self.assertIn("apt-get install -y zsh git jq fzf zoxide", commands)
        self.assertNotIn(" eza", commands)
        self.assertIn("Skipping unavailable package: eza", result.stderr)

    def test_homebrew_install(self):
        self.mock("uname", "printf 'Darwin\\n'\n")
        self.mock("brew", 'printf "brew %s\\n" "$*" >> "$TEST_LOG"\n')
        self.run_install("--with-tools")
        self.assertIn("brew install zsh git eza jq fzf zoxide", self.log.read_text())
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
