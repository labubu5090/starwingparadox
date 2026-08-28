"""Tests for prohibited-import and side-effect guards.

This module ensures that the G17 clean-room package does not import
or invoke prohibited modules.
"""
from __future__ import annotations

import sys

# Modules that are prohibited in the clean-room package
PROHIBITED_MODULES = [
    "socket",
    "requests",
    "httpx",
    "urllib.request",
    "urllib.error",
    "urllib.parse",
    "winreg",
    "subprocess",
    "ctypes",
]


def get_cleanroom_imports() -> set[str]:
    """Recursively find all imports used by the cleanroom package."""
    imports: set[str] = set()
    cleanroom_modules = [
        name for name in sys.modules
        if name.startswith("app.cleanroom")
    ]
    for module_name in cleanroom_modules:
        module = sys.modules.get(module_name)
        if module is None:
            continue
        if hasattr(module, "__file__") and module.__file__ is None:
            continue
        # Check for standard import attributes
        if hasattr(module, "__all__"):
            for attr in module.__all__:
                if isinstance(attr, str):
                    imports.add(attr)
    return imports


class TestProhibitedImports:
    """Test that prohibited modules are not imported by cleanroom."""

    def test_no_socket_import(self):
        """Verify socket is not imported by cleanroom modules."""
        import app.cleanroom.session as session_mod
        import app.cleanroom.synthetic_transport as synth_mod
        import app.cleanroom.transport as transport_mod

        for mod in [transport_mod, synth_mod, session_mod]:
            source = ""
            if hasattr(mod, "__file__") and mod.__file__:
                with open(mod.__file__, encoding="utf-8") as f:
                    source = f.read()
            assert "import socket" not in source
            assert "from socket" not in source

    def test_no_requests_import(self):
        """Verify requests is not imported by cleanroom modules."""
        import app.cleanroom.session as session_mod
        import app.cleanroom.synthetic_transport as synth_mod
        import app.cleanroom.transport as transport_mod

        for mod in [transport_mod, synth_mod, session_mod]:
            source = ""
            if hasattr(mod, "__file__") and mod.__file__:
                with open(mod.__file__, encoding="utf-8") as f:
                    source = f.read()
            assert "import requests" not in source
            assert "from requests" not in source

    def test_no_winreg_import(self):
        """Verify winreg is not imported by cleanroom modules."""
        import app.cleanroom.session as session_mod
        import app.cleanroom.synthetic_transport as synth_mod
        import app.cleanroom.transport as transport_mod

        for mod in [transport_mod, synth_mod, session_mod]:
            source = ""
            if hasattr(mod, "__file__") and mod.__file__:
                with open(mod.__file__, encoding="utf-8") as f:
                    source = f.read()
            assert "import winreg" not in source
            assert "from winreg" not in source

    def test_no_subprocess_import(self):
        """Verify subprocess is not imported by cleanroom modules."""
        import app.cleanroom.session as session_mod
        import app.cleanroom.synthetic_transport as synth_mod
        import app.cleanroom.transport as transport_mod

        for mod in [transport_mod, synth_mod, session_mod]:
            source = ""
            if hasattr(mod, "__file__") and mod.__file__:
                with open(mod.__file__, encoding="utf-8") as f:
                    source = f.read()
            assert "import subprocess" not in source
            assert "from subprocess" not in source


class TestNoProductionEndpoints:
    """Test that no production hostnames appear in cleanroom code."""

    PROHIBITED_HOSTNAMES = [
        "cert3.nesys.jp",
        "data.nesys.jp",
        "nesys.taito.co.jp",
        "fjm170920zero.nesica.net",
        "dev.starwing.jp",
    ]

    def _get_cleanroom_source_files(self) -> list[str]:
        """Get all Python source files in the cleanroom package."""
        import os

        import app.cleanroom

        pkg_dir = os.path.dirname(app.cleanroom.__file__)
        source_files = []
        for root, _dirs, files in os.walk(pkg_dir):
            for f in files:
                if f.endswith(".py"):
                    filepath = os.path.join(root, f)
                    # Exclude safety.py which contains the prohibited lists
                    if os.path.basename(filepath) == "safety.py":
                        continue
                    source_files.append(filepath)
        return source_files

    def test_no_production_hostnames(self):
        """Verify no production hostnames in cleanroom source files."""
        for filepath in self._get_cleanroom_source_files():
            with open(filepath, encoding="utf-8") as f:
                content = f.read()
            for hostname in self.PROHIBITED_HOSTNAMES:
                assert hostname not in content, (
                    f"Production hostname {hostname} found in {filepath}"
                )

    def test_no_pipe_path(self):
        """Verify no production named pipe path in cleanroom source files."""
        pipe_path = r"\\.\pipe\nesys_games"
        for filepath in self._get_cleanroom_source_files():
            with open(filepath, encoding="utf-8") as f:
                content = f.read()
            assert pipe_path not in content, (
                f"Production pipe path found in {filepath}"
            )


class TestNoCertificateMaterial:
    """Test that no certificate material appears in cleanroom code."""

    def _get_cleanroom_source_files(self) -> list[str]:
        """Get all Python source files in the cleanroom package."""
        import os

        import app.cleanroom

        pkg_dir = os.path.dirname(app.cleanroom.__file__)
        source_files = []
        for root, _dirs, files in os.walk(pkg_dir):
            for f in files:
                if f.endswith(".py"):
                    filepath = os.path.join(root, f)
                    # Exclude safety.py which contains the prohibited lists
                    if os.path.basename(filepath) == "safety.py":
                        continue
                    source_files.append(filepath)
        return source_files

    def test_no_certificate_store_references(self):
        """Verify no certificate store references in cleanroom source."""
        prohibited = [
            "CertOpenStore",
            "CertFindCertificateInStore",
            "MY\\.Default",
            "nesys",
        ]
        for filepath in self._get_cleanroom_source_files():
            with open(filepath, encoding="utf-8") as f:
                content = f.read()
            for ref in prohibited:
                # Only check in strings, not in comments explaining restrictions
                lines = content.split("\n")
                for line in lines:
                    stripped = line.strip()
                    if stripped.startswith("#"):
                        continue
                    assert ref not in stripped, (
                        f"Certificate reference {ref} found in {filepath}"
                    )
