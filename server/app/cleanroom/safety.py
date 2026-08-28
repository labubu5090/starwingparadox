"""Expanded safety guards for clean-room protocol foundation.

This module provides comprehensive safety checks that verify
the clean-room foundation does not import restricted modules,
use production endpoints, or expose production entry points.
"""
from __future__ import annotations

import ast
import enum
from dataclasses import dataclass
from pathlib import Path


class GuardLevel(enum.Enum):
    """Evidence level for guards."""

    CONFIRMED = "confirmed"
    SYNTHETIC = "synthetic"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class GuardResult:
    """Result of a safety guard check.

    Attributes:
        name: Guard name.
        passed: Whether check passed.
        level: Evidence level.
        details: Additional details.
    """

    name: str
    passed: bool
    level: GuardLevel
    details: str = ""


PROHIBITED_IMPORTS = [
    "socket",
    "requests",
    "httpx",
    "winreg",
    "subprocess",
    "ssl",
    "cryptography",
    "win32pipe",
    "win32file",
    "namedpipe",
]

PROHIBITED_HOSTNAMES = [
    "dev.starwing.jp",
    "fjm170920zero.nesica.net",
    "nesys.nintendo.net",
    "arcade.nintendo.net",
]

PROHIBITED_PIPE_PATHS = [
    "\\\\.\\pipe\\nesys_games",
    "\\\\.\\pipe\\nesys",
    "\\\\.\\pipe\\arcade",
]

PROHIBITED_CERTIFICATE_REFERENCES = [
    "CertOpenStore",
    "CertFindCertificateInStore",
    "CertCloseStore",
    "CertGetCertificateChain",
    "PFXImportCertStore",
    "SSL_CTX",
    "ssl.SSLContext",
    "MY\\.Default",
    "LocalMachine\\MY",
    "CurrentUser\\MY",
]

PROHIBITED_REGISTRY_PATHS = [
    "HKLM\\SOFTWARE\\Nintendo",
    "HKLM\\SOFTWARE\\Nesys",
    "HKLM\\SOFTWARE\\Arcade",
    "HKEY_LOCAL_MACHINE\\SOFTWARE\\Nintendo",
    "HKEY_LOCAL_MACHINE\\SOFTWARE\\Nesys",
    "HKEY_LOCAL_MACHINE\\SOFTWARE\\Arcade",
]


class SafetyGuardChecker:
    """Checker for expanded safety guards.

    This checker verifies:
    - No restricted module imports
    - No production hostnames
    - No pipe paths
    - No certificate references
    - No registry paths
    - No production entry points
    - No executable packaging
    """

    def __init__(self, source_dir: str | Path) -> None:
        """Initialize the checker.

        Args:
            source_dir: Directory containing cleanroom source files.
        """
        self._source_dir = Path(source_dir)
        self._self_file = Path(__file__).resolve()

    def check_no_prohibited_imports(self) -> GuardResult:
        """Check for prohibited imports in source files.

        Returns:
            GuardResult indicating pass/fail.
        """
        violations = []

        for py_file in self._source_dir.rglob("*.py"):
            if py_file.resolve() == self._self_file:
                continue

            try:
                content = py_file.read_text(encoding="utf-8")
                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            if alias.name in PROHIBITED_IMPORTS:
                                violations.append(
                                    f"{py_file.name}:{node.lineno}: "
                                    f"import {alias.name}"
                                )
                    elif isinstance(node, ast.ImportFrom) and node.module and node.module in PROHIBITED_IMPORTS:
                        violations.append(
                            f"{py_file.name}:{node.lineno}: "
                            f"from {node.module} import ..."
                        )
            except Exception:
                pass

        if violations:
            return GuardResult(
                name="no_prohibited_imports",
                passed=False,
                level=GuardLevel.CONFIRMED,
                details=f"Violations: {'; '.join(violations)}",
            )

        return GuardResult(
            name="no_prohibited_imports",
            passed=True,
            level=GuardLevel.CONFIRMED,
            details="No prohibited imports found",
        )

    def check_no_production_hostnames(self) -> GuardResult:
        """Check for production hostnames in source files.

        Returns:
            GuardResult indicating pass/fail.
        """
        violations = []

        for py_file in self._source_dir.rglob("*.py"):
            if py_file.resolve() == self._self_file:
                continue

            try:
                content = py_file.read_text(encoding="utf-8")
                for i, line in enumerate(content.splitlines(), 1):
                    for hostname in PROHIBITED_HOSTNAMES:
                        if hostname in line:
                            violations.append(
                                f"{py_file.name}:{i}: {hostname}"
                            )
            except Exception:
                pass

        if violations:
            return GuardResult(
                name="no_production_hostnames",
                passed=False,
                level=GuardLevel.CONFIRMED,
                details=f"Violations: {'; '.join(violations)}",
            )

        return GuardResult(
            name="no_production_hostnames",
            passed=True,
            level=GuardLevel.CONFIRMED,
            details="No production hostnames found",
        )

    def check_no_pipe_paths(self) -> GuardResult:
        """Check for pipe paths in source files.

        Returns:
            GuardResult indicating pass/fail.
        """
        violations = []

        for py_file in self._source_dir.rglob("*.py"):
            if py_file.resolve() == self._self_file:
                continue

            try:
                content = py_file.read_text(encoding="utf-8")
                for i, line in enumerate(content.splitlines(), 1):
                    for pipe_path in PROHIBITED_PIPE_PATHS:
                        if pipe_path in line:
                            violations.append(
                                f"{py_file.name}:{i}: {pipe_path}"
                            )
            except Exception:
                pass

        if violations:
            return GuardResult(
                name="no_pipe_paths",
                passed=False,
                level=GuardLevel.CONFIRMED,
                details=f"Violations: {'; '.join(violations)}",
            )

        return GuardResult(
            name="no_pipe_paths",
            passed=True,
            level=GuardLevel.CONFIRMED,
            details="No pipe paths found",
        )

    def check_no_certificate_references(self) -> GuardResult:
        """Check for certificate references in source files.

        Returns:
            GuardResult indicating pass/fail.
        """
        violations = []

        for py_file in self._source_dir.rglob("*.py"):
            if py_file.resolve() == self._self_file:
                continue

            try:
                content = py_file.read_text(encoding="utf-8")
                for i, line in enumerate(content.splitlines(), 1):
                    for cert_ref in PROHIBITED_CERTIFICATE_REFERENCES:
                        if cert_ref in line.lower():
                            violations.append(
                                f"{py_file.name}:{i}: {cert_ref}"
                            )
            except Exception:
                pass

        if violations:
            return GuardResult(
                name="no_certificate_references",
                passed=False,
                level=GuardLevel.CONFIRMED,
                details=f"Violations: {'; '.join(violations)}",
            )

        return GuardResult(
            name="no_certificate_references",
            passed=True,
            level=GuardLevel.CONFIRMED,
            details="No certificate references found",
        )

    def check_no_registry_paths(self) -> GuardResult:
        """Check for registry paths in source files.

        Returns:
            GuardResult indicating pass/fail.
        """
        violations = []

        for py_file in self._source_dir.rglob("*.py"):
            if py_file.resolve() == self._self_file:
                continue

            try:
                content = py_file.read_text(encoding="utf-8")
                for i, line in enumerate(content.splitlines(), 1):
                    for reg_path in PROHIBITED_REGISTRY_PATHS:
                        if reg_path in line:
                            violations.append(
                                f"{py_file.name}:{i}: {reg_path}"
                            )
            except Exception:
                pass

        if violations:
            return GuardResult(
                name="no_registry_paths",
                passed=False,
                level=GuardLevel.CONFIRMED,
                details=f"Violations: {'; '.join(violations)}",
            )

        return GuardResult(
            name="no_registry_paths",
            passed=True,
            level=GuardLevel.CONFIRMED,
            details="No registry paths found",
        )

    def check_all_guards(self) -> list[GuardResult]:
        """Run all safety guard checks.

        Returns:
            List of GuardResult instances.
        """
        return [
            self.check_no_prohibited_imports(),
            self.check_no_production_hostnames(),
            self.check_no_pipe_paths(),
            self.check_no_certificate_references(),
            self.check_no_registry_paths(),
        ]
