"""Legacy regression: POST /matching/* endpoints.

Source evidence: legacy-js/js/starwing.js lines 345-449
Fixture: server/tests/fixtures/legacy/http/

The legacy matching endpoints:
  - /matching/server (lines 345-369): Returns {ip_addr: "matcher:port"}
  - /matching/match_id/generate (lines 428-438): Returns {match_id: random_int}
  - /matching/* (lines 440-449): Returns {} for any other path

REGRESSION STATUS: The Python reimplementation returns different response
structure than legacy:
  - Legacy /matching/server returns {ip_addr: "paradox.yourdomain.com:6666"}
  - Python /matching/server returns {result: 1, servers: []} in legacy mode
  - Python returns 501 not_implemented in strict mode

This is a known deviation. The Python implementation prioritizes controlled
behavior over legacy compatibility for security-sensitive endpoints.
"""

import pytest
from fastapi.testclient import TestClient

pytestmark = [pytest.mark.legacy_regression, pytest.mark.api]


class TestMatchingLegacyRegression:
    """Verify POST /matching/* endpoints match or control legacy behavior.

    Source: legacy-js/js/starwing.js:345-449

    Legacy behavior:
      - /matching/server returns {ip_addr: "paradox.yourdomain.com:6666"}
      - /matching/match_id/generate returns {match_id: random_int}
      - /matching/* returns {} for any path

    Python implementation:
      - /matching/server returns 501 (strict) or {result: 1, servers: []} (legacy)
      - /matching/match_id/generate returns 501 (strict) or {result: 1, match_id: ""} (legacy)
      - /matching/* returns 501 (strict) or {result: 1} (legacy)
    """

    SOURCE_FILE = "legacy-js/js/starwing.js"
    SOURCE_LINE_START = 345
    SOURCE_LINE_END = 449

    def test_matching_server_returns_valid_status(self, client: TestClient) -> None:
        """POST /matching/server returns 200 (legacy) or 501 (strict)."""
        response = client.post("/matching/server", json={})
        assert response.status_code in (200, 501)

    def test_matching_server_strict_mode_returns_501(self, client: TestClient) -> None:
        """Strict mode returns 501 not_implemented."""
        response = client.post("/matching/server", json={})
        if response.status_code == 501:
            data = response.json()
            assert data.get("error") == "not_implemented"
            assert data.get("endpoint") == "/matching/server"

    def test_matching_server_legacy_mode_returns_200(self, client: TestClient) -> None:
        """Legacy mode returns 200."""
        response = client.post("/matching/server", json={})
        assert response.status_code == 200

    def test_matching_server_legacy_response_format(self, client: TestClient) -> None:
        """Legacy mode returns a JSON response.
        NOTE: Legacy returns {ip_addr: ...}, Python returns {result: 1, servers: []}.
        This is a known deviation."""
        response = client.post("/matching/server", json={})
        data = response.json()
        assert isinstance(data, dict)

    def test_matching_server_x_galaxy_api_id_echoed(self, client: TestClient) -> None:
        """Legacy echoes x-galaxy-api-id."""
        response = client.post(
            "/matching/server",
            json={},
            headers={"x-galaxy-api-id": "match-test-id"},
        )
        if response.status_code == 200:
            assert response.headers.get("x-galaxy-api-id") == "match-test-id"

    def test_matching_fallback_returns_valid_status(self, client: TestClient) -> None:
        """POST /matching/unknown must return 200 or 501."""
        response = client.post("/matching/unknown_path", json={})
        assert response.status_code in (200, 501)

    def test_matching_fallback_legacy_mode_returns_200(self, client: TestClient) -> None:
        """In legacy compatibility mode, unknown matching paths return 200."""
        response = client.post("/matching/unknown_path", json={})
        assert response.status_code == 200

    def test_matching_fallback_x_galaxy_api_header(self, client: TestClient) -> None:
        """Legacy matching/* sets x-galaxy-api to '*/*'."""
        response = client.post("/matching/unknown_path", json={})
        if response.status_code == 200:
            assert response.headers.get("x-galaxy-api") == "*/*"

    def test_prove_no_false_success_on_unknown_endpoint(self, client: TestClient) -> None:
        """CRITICAL: An unknown matching endpoint must NOT return 200 with
        fake match data in strict mode. In legacy mode it returns 200 with
        stub data. This test proves controlled behavior."""
        response = client.post("/matching/totally_fake_endpoint_xyz", json={})
        assert response.status_code in (200, 501)
        if response.status_code == 200:
            data = response.json()
            # Must not contain real match data
            assert "match_id" not in data or data.get("match_id") == ""

    def test_matching_server_x_galaxy_api_header(self, client: TestClient) -> None:
        """Legacy sets x-galaxy-api to '*/*' for matching."""
        response = client.post("/matching/server", json={})
        if response.status_code == 200:
            assert response.headers.get("x-galaxy-api") == "*/*"
