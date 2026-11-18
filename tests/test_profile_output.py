"""Postprocessing failures must not be reported as a completed handover."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import profile_output as output


class ProfileOutputChecks(unittest.TestCase):
    def test_missing_environment_fails_before_solver(self):
        with self.assertRaises(FileNotFoundError):
            output.check_plot_python('/nonexistent/first-profile-python')

    def test_failed_plotter_is_not_complete(self):
        with tempfile.TemporaryDirectory() as run:
            with patch.object(output.subprocess, 'run', side_effect=subprocess.CalledProcessError(2, 'plot')):
                with self.assertRaises(subprocess.CalledProcessError):
                    output.make_profiles('vmec', run, 'example', sys.executable)
            self.assertTrue((Path(run) / 'profiles.log').is_file())

    def test_exit_zero_without_artifacts_is_not_complete(self):
        with tempfile.TemporaryDirectory() as run:
            with patch.object(output.subprocess, 'run'):
                with self.assertRaisesRegex(ValueError, 'Missing profile output'):
                    output.make_profiles('chease', run, 'example', sys.executable)
