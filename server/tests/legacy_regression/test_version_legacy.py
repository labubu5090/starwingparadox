"""Legacy regression: POST /version endpoint.

Source evidence: legacy-js/js/starwing.js lines 407-426
Fixture: server/tests/fixtures/legacy/http/version_check.json

The legacy server at lines 407-426 constructs the response by string
concatenation with hardcoded version numbers (70571) and an empty stage_ids
array. The response is returned with headers:
  - x-galaxy-api: */*
  - x-galaxy-api-id: echoed from request
"""

import pytest
from fastapi.testclient import TestClient

from tests.fixtures.legacy.http.version_check import (  # noqa: F401
    LEGACY_LINE_END,
    LEGACY_LINE_START,
    LEGACY_SOURCE_FILE,
)

pytestmark = [pytest.mark.legacy_regression, pytest.mark.api]


class TestVersionLegacyRegression:
    """Verify POST /version matches legacy JavaScript behavior exactly.

    Source: legacy-js/js/starwing.js:407-426
    The legacy handler:
        res.set('Content-type','application/json');
        res.set('x-galaxy-api', '*/*');
        res.set('x-galaxy-api-id', req.header('x-galaxy-api-id'));
        res.send("{\\n" +
            "\\t\\\"client_version\\\": \\\"" + version_main + "\\\",\\n" +
            "\\t\\\"data_version\\\": \\\"" + version_data + "\\\",\\n" +
            "\\t\\\"stage_ids\\\": []" +
            "}");
        res.status(200).end();
    """

    SOURCE_FILE = "legacy-js/js/starwing.js"
    SOURCE_LINE_START = 407
    SOURCE_LINE_END = 426
    FIXTURE = "server/tests/fixtures/legacy/http/version_check.json"

    def test_status_code_is_200(self, client: TestClient) -> None:
        """Legacy always returns 200."""
        response = client.post("/version", json={})
        assert response.status_code == 200

    def test_content_type_is_json(self, client: TestClient) -> None:
        """Legacy sets Content-type to application/json."""
        response = client.post("/version", json={})
        assert response.headers["content-type"] == "application/json"

    def test_x_galaxy_api_header(self, client: TestClient) -> None:
        """Legacy sets x-galaxy-api to '*/*'."""
        response = client.post("/version", json={})
        assert response.headers.get("x-galaxy-api") == "*/*"

    def test_x_galaxy_api_id_echoed(self, client: TestClient) -> None:
        """Legacy echoes x-galaxy-api-id from the request."""
        response = client.post("/version", json={}, headers={"x-galaxy-api-id": "test-abc-123"})
        assert response.headers.get("x-galaxy-api-id") == "test-abc-123"

    def test_x_galaxy_api_id_absent_when_not_sent(self, client: TestClient) -> None:
        """Legacy omits x-galaxy-api-id when not in request (conditional set)."""
        response = client.post("/version", json={})
        # The Python impl sets it only if present. Legacy does the same.
        # When not sent, the header should either be absent or empty.
        api_id = response.headers.get("x-galaxy-api-id", "")
        assert api_id in ("", None)

    def test_body_has_client_version(self, client: TestClient) -> None:
        """Response body must contain 'client_version' field."""
        response = client.post("/version", json={})
        data = response.json()
        assert "client_version" in data

    def test_body_has_data_version(self, client: TestClient) -> None:
        """Response body must contain 'data_version' field."""
        response = client.post("/version", json={})
        data = response.json()
        assert "data_version" in data

    def test_body_has_stage_ids(self, client: TestClient) -> None:
        """Response body must contain 'stage_ids' field as a list."""
        response = client.post("/version", json={})
        data = response.json()
        assert "stage_ids" in data
        assert isinstance(data["stage_ids"], list)

    def test_client_version_is_70571(self, client: TestClient) -> None:
        """Legacy version_main is 70571. Must be returned as string '70571'."""
        response = client.post("/version", json={})
        data = response.json()
        assert data["client_version"] == "70571"

    def test_data_version_is_70571(self, client: TestClient) -> None:
        """Legacy version_data is 70571. Must be returned as string '70571'."""
        response = client.post("/version", json={})
        data = response.json()
        assert data["data_version"] == "70571"

    def test_stage_ids_is_empty(self, client: TestClient) -> None:
        """Legacy returns stage_ids as empty array."""
        response = client.post("/version", json={})
        data = response.json()
        assert data["stage_ids"] == []

    def test_body_exactly_three_fields(self, client: TestClient) -> None:
        """Legacy response contains exactly 3 fields: client_version, data_version, stage_ids."""
        response = client.post("/version", json={})
        data = response.json()
        assert set(data.keys()) == {"client_version", "data_version", "stage_ids"}

    def test_version_values_are_strings_not_integers(self, client: TestClient) -> None:
        """Legacy concatenates version into string; values must be strings, not ints."""
        response = client.post("/version", json={})
        data = response.json()
        assert isinstance(data["client_version"], str)
        assert isinstance(data["data_version"], str)
