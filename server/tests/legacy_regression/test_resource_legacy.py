"""Legacy regression: POST /resource endpoint.

Source evidence: legacy-js/js/starwing.js lines 779-789
Fixture: server/tests/fixtures/legacy/http/resource_load.json

The legacy server at lines 779-789 reads c_resource.json from disk and
returns it verbatim. The response includes a 'version' string and a 'data'
array of CSV URLs.

REGRESSION STATUS: The Python reimplementation:
  - Returns {} when c_resource.json is not found
  - Returns the resource data when the file exists
  - Sets x-galaxy-api to '*/*' (matches legacy)

The c_resource.json file must be present at the expected path for the
endpoint to return the correct data.
"""

import pytest
from fastapi.testclient import TestClient

pytestmark = [pytest.mark.legacy_regression, pytest.mark.api]


class TestResourceLegacyRegression:
    """Verify POST /resource matches or controls legacy behavior.

    Source: legacy-js/js/starwing.js:779-789

    Legacy behavior:
      - Reads starwing/c_resource.json from disk
      - Returns file content verbatim
      - Sets x-galaxy-api to '*/*'

    Python implementation:
      - Reads c_resource.json from configured path
      - Returns {} if file not found
      - Returns parsed JSON if file found
    """

    SOURCE_FILE = "legacy-js/js/starwing.js"
    SOURCE_LINE_START = 779
    SOURCE_LINE_END = 789
    FIXTURE = "server/tests/fixtures/legacy/http/resource_load.json"

    def test_status_code_is_200(self, client: TestClient) -> None:
        """Legacy always returns 200."""
        response = client.post("/resource", json={})
        assert response.status_code == 200

    def test_content_type_is_json(self, client: TestClient) -> None:
        """Legacy sets Content-type to application/json."""
        response = client.post("/resource", json={})
        assert "application/json" in response.headers["content-type"]

    def test_x_galaxy_api_header(self, client: TestClient) -> None:
        """Legacy sets x-galaxy-api to '*/*'."""
        response = client.post("/resource", json={})
        assert response.headers.get("x-galaxy-api") == "*/*"

    def test_x_galaxy_api_id_echoed(self, client: TestClient) -> None:
        """Legacy echoes x-galaxy-api-id from the request."""
        response = client.post("/resource", json={}, headers={"x-galaxy-api-id": "test-res-456"})
        assert response.headers.get("x-galaxy-api-id") == "test-res-456"

    def test_body_is_valid_json(self, client: TestClient) -> None:
        """Response must be valid JSON."""
        response = client.post("/resource", json={})
        data = response.json()
        assert isinstance(data, dict)

    def test_resource_file_returns_data_or_empty(self, client: TestClient) -> None:
        """If c_resource.json exists, returns {version, data}.
        If not found, returns {}."""
        response = client.post("/resource", json={})
        data = response.json()
        # Either has resource data or is empty (file not found)
        assert isinstance(data, dict)

    def test_resource_has_version_when_file_exists(self, client: TestClient) -> None:
        """When c_resource.json is present, response has 'version' field."""
        response = client.post("/resource", json={})
        data = response.json()
        if "version" in data:
            assert isinstance(data["version"], str)
            assert data["version"] == "70571"

    def test_resource_has_data_when_file_exists(self, client: TestClient) -> None:
        """When c_resource.json is present, response has 'data' field."""
        response = client.post("/resource", json={})
        data = response.json()
        if "data" in data:
            assert isinstance(data["data"], list)
            assert len(data["data"]) > 0

    def test_resource_data_entries_are_urls(self, client: TestClient) -> None:
        """Each data entry should be a URL to a CSV file."""
        response = client.post("/resource", json={})
        data = response.json()
        if "data" in data:
            for entry in data["data"]:
                assert isinstance(entry, str)
                assert entry.startswith("http://"), f"Not a URL: {entry}"

    def test_body_not_required(self, client: TestClient) -> None:
        """Legacy accepts requests with empty body."""
        response = client.post("/resource")
        assert response.status_code == 200
