"""G34 Runtime validation tests for INI config path.

Verifies that the game reads DefaultMatchingServerAddress from
[/Script/NetworkModule.NetworkConfig] in DefaultGame.ini and uses it
to establish TCP connection without NESYS certificate trust.

Classification: INI_CONFIG_PATH_RUNTIME_CONFIRMED
"""

from __future__ import annotations

import json
import hashlib
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS = PROJECT_ROOT / "artifacts" / "phase_2a_g34"
DECISION_JSON = ARTIFACTS / "g34_decision.json"
CAPTURE_LOG = ARTIFACTS / "g34_ini_config_capture.log"
DEFAULT_GAME_INI = Path("X:/StarwingParadox/WindowsNoEditor/AcrGame/Config/DefaultGame.ini")
BACKUP_INI = Path("X:/StarwingParadox/WindowsNoEditor/AcrGame/Config/DefaultGame.ini.backup-g34")

# Expected SHA-256 of DefaultGame.ini (with our modifications)
EXPECTED_INI_HASH = "37AE67B38CE6DB41E99F8D9BEE59BEE4E7AD7B53A3DEF05162D53AAE12BFBF62"

# Critical log keywords that form the evidence chain
EVIDENCE_KEYWORDS = [
    "HttpRequestMatchingServer",
    "OnReceiveResponseMatchingServer / _IsSuccess[1] IPAddress[127.0.0.1:6666]",
    "FAcrNetworkConfig::Init / port[7777]",
    "MatchingServer : 127.0.0.1:6666 (UseConfigMatchingServer : 1)",
    "Use Config(.ini)MatchingServer address:127.0.0.1:6666",
    "Decide connect type INI file address",
    "Success to connect. / GetTargetAddress[127.0.0.1:6666]",
    "OnReceivePong / WebServer Revived!",
]

# Keywords that should NOT appear as boot blockers
NON_BLOCKER_KEYWORDS = [
    "Error No MatchingServer so initialize Nesys before.",
]


class TestG34DecisionJSON:
    """Test the g34_decision.json artifact."""

    def test_decision_json_exists(self):
        assert DECISION_JSON.exists(), f"Decision JSON not found: {DECISION_JSON}"

    def test_decision_json_valid(self):
        data = json.loads(DECISION_JSON.read_text(encoding="utf-8"))
        assert "g34_validation_result" in data
        assert data["g34_validation_result"] == "INI_CONFIG_PATH_RUNTIME_CONFIRMED"

    def test_classification_matches(self):
        data = json.loads(DECISION_JSON.read_text(encoding="utf-8"))
        assert data["classification"] == "INI_CONFIG_PATH_RUNTIME_CONFIRMED"

    def test_evidence_chain_has_required_entries(self):
        data = json.loads(DECISION_JSON.read_text(encoding="utf-8"))
        chain = data.get("evidence_chain", [])
        assert len(chain) >= 10, f"Expected >=10 evidence entries, got {len(chain)}"
        keywords = [e["keyword"] for e in chain]
        assert any("Decide connect type" in k for k in keywords), "Missing 'Decide connect type' in evidence"
        assert any("UseConfigMatchingServer" in k for k in keywords), "Missing 'UseConfigMatchingServer' in evidence"
        assert any("Success to connect" in k for k in keywords), "Missing TCP success in evidence"

    def test_config_source_section(self):
        data = json.loads(DECISION_JSON.read_text(encoding="utf-8"))
        config = data.get("config_source", {})
        assert config.get("section") == "[/Script/NetworkModule.NetworkConfig]"
        props = config.get("properties_used", {})
        assert props.get("DefaultMatchingServerAddress") == "127.0.0.1:6666"

    def test_decision_path_flow_steps(self):
        data = json.loads(DECISION_JSON.read_text(encoding="utf-8"))
        flow = data.get("decision_path_flow", {})
        assert len(flow) >= 9, f"Expected >=9 flow steps, got {len(flow)}"
        assert "INI file address" in str(flow)


class TestG34CaptureLog:
    """Test the g34_ini_config_capture.log artifact."""

    def test_capture_log_exists(self):
        assert CAPTURE_LOG.exists(), f"Capture log not found: {CAPTURE_LOG}"

    def test_capture_log_has_evidence(self):
        content = CAPTURE_LOG.read_text(encoding="utf-8", errors="replace")
        for keyword in EVIDENCE_KEYWORDS:
            assert keyword in content, f"Missing evidence keyword: {keyword}"

    def test_capture_log_connect_type_ini(self):
        content = CAPTURE_LOG.read_text(encoding="utf-8", errors="replace")
        assert "Decide connect type INI file address" in content

    def test_capture_log_tcp_success(self):
        content = CAPTURE_LOG.read_text(encoding="utf-8", errors="replace")
        assert "Success to connect. / GetTargetAddress[127.0.0.1:6666]" in content

    def test_capture_log_ping_pong(self):
        content = CAPTURE_LOG.read_text(encoding="utf-8", errors="replace")
        assert "OnReceivePong / WebServer Revived!" in content

    def test_capture_log_not_blocked_by_nesys_error(self):
        """Error No MatchingServer should NOT prevent TCP connection."""
        content = CAPTURE_LOG.read_text(encoding="utf-8", errors="replace")
        has_error = "Error No MatchingServer so initialize Nesys before." in content
        has_success = "Success to connect. / GetTargetAddress[127.0.0.1:6666]" in content
        # Both can exist: error is bootstrap, not blocker
        if has_error:
            assert has_success, "Error No MatchingServer appeared without TCP success - may be a blocker"


class TestG34DefaultGameINI:
    """Test the DefaultGame.ini configuration."""

    def test_default_game_ini_exists(self):
        assert DEFAULT_GAME_INI.exists(), f"DefaultGame.ini not found: {DEFAULT_GAME_INI}"

    def test_default_game_ini_hash(self):
        content = DEFAULT_GAME_INI.read_bytes()
        sha256 = hashlib.sha256(content).hexdigest().upper()
        assert sha256 == EXPECTED_INI_HASH, f"INI hash mismatch: {sha256} != {EXPECTED_INI_HASH}"

    def test_network_config_section_exists(self):
        content = DEFAULT_GAME_INI.read_text(encoding="utf-8")
        assert "[/Script/NetworkModule.NetworkConfig]" in content

    def test_matching_server_address(self):
        content = DEFAULT_GAME_INI.read_text(encoding="utf-8")
        assert "DefaultMatchingServerAddress=127.0.0.1:6666" in content

    def test_backup_exists(self):
        assert BACKUP_INI.exists(), f"Backup INI not found: {BACKUP_INI}"


class TestG34Classification:
    """Test the classification document."""

    def test_classification_file_exists(self):
        classification_file = ARTIFACTS / "g34_classification.md"
        assert classification_file.exists(), f"Classification not found: {classification_file}"

    def test_classification_contains_key_findings(self):
        classification_file = ARTIFACTS / "g34_classification.md"
        content = classification_file.read_text(encoding="utf-8")
        assert "INI_CONFIG_PATH_RUNTIME_CONFIRMED" in content
        assert "Decide connect type INI file address" in content
        assert "127.0.0.1:6666" in content
        assert "DefaultGame.ini" in content
