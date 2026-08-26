"""Legacy regression tests for the Starwing Paradox Python server.

These tests verify that the Python reimplementation produces responses
identical to the original JavaScript server (legacy-js/js/starwing.js).

Each test references:
- Source evidence (file + line range from legacy-js/)
- Fixture file (server/tests/fixtures/legacy/http/)
- Exact assertions for status, headers, and body structure
"""
