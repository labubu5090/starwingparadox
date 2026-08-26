# Legacy Source Integrity Report

Generated: 2026-08-26
Project Root: `C:\Users\KAHO\Pictures\新增資料夾`

---

## Source Integrity Statement

> **This project is NOT a Git repository.** No version history, no commit log, no diff
> capability exists. All integrity assessments below are **snapshot-based only** and
> cannot determine whether any file has been modified from its original state.

---

## Legacy Source Files (legacy-js/)

### Files and Locations

| # | Relative Path | Size | Classification |
|---|--------------|------|----------------|
| 1 | `legacy-js/README.md` | 434 B | LEGACY_ORIGINAL |
| 2 | `legacy-js/html/index.html` | 41 B | LEGACY_ORIGINAL |
| 3 | `legacy-js/js/nginx.vhost.conf` | 1,225 B | LEGACY_ORIGINAL |
| 4 | `legacy-js/js/starwing.js` | 28,579 B | LEGACY_ORIGINAL |
| 5 | `legacy-js/js/starwingMessage.proto` | 10,442 B | LEGACY_ORIGINAL |
| 6 | `legacy-js/js/starwing/API-NOTES.txt` | 41,228 B | LEGACY_ORIGINAL |
| 7 | `legacy-js/js/starwing/any.proto` | 6,065 B | LEGACY_ORIGINAL |
| 8 | `legacy-js/js/starwing/battleRecorder.js` | 1,907 B | LEGACY_ORIGINAL |
| 9 | `legacy-js/js/starwing/burstMode.js` | 9,574 B | LEGACY_ORIGINAL |
| 10 | `legacy-js/js/starwing/c_rankingEvent.json` | 120 B | LEGACY_ORIGINAL |
| 11 | `legacy-js/js/starwing/c_rankingNational.json` | 26,120 B | LEGACY_ORIGINAL |
| 12 | `legacy-js/js/starwing/c_rankingNational_2on2.json` | 26,988 B | LEGACY_ORIGINAL |
| 13 | `legacy-js/js/starwing/c_rankingPrefecture.json` | 26,159 B | LEGACY_ORIGINAL |
| 14 | `legacy-js/js/starwing/c_rankingPrefecture_2on2.json` | 27,019 B | LEGACY_ORIGINAL |
| 15 | `legacy-js/js/starwing/c_rankingStore.json` | 26,169 B | LEGACY_ORIGINAL |
| 16 | `legacy-js/js/starwing/c_rankingStore_2on2.json` | 27,029 B | LEGACY_ORIGINAL |
| 17 | `legacy-js/js/starwing/c_rankingWeapon_r1.json` | 2,070 B | LEGACY_ORIGINAL |
| 18 | `legacy-js/js/starwing/c_rankingWeapon_r2.json` | 2,073 B | LEGACY_ORIGINAL |
| 19 | `legacy-js/js/starwing/c_rankingWeapon_r3.json` | 2,073 B | LEGACY_ORIGINAL |
| 20 | `legacy-js/js/starwing/c_rankingWeapon_r4.json` | 2,073 B | LEGACY_ORIGINAL |
| 21 | `legacy-js/js/starwing/c_resource.json` | 9,393 B | LEGACY_ORIGINAL |
| 22 | `legacy-js/js/starwing/io.txt` | 343 B | LEGACY_ORIGINAL |
| 23 | `legacy-js/js/starwing/playerProfile.js` | 38,215 B | LEGACY_ORIGINAL |
| 24 | `legacy-js/js/starwing/rankingCooker.js` | 5,302 B | LEGACY_ORIGINAL |
| 25 | `legacy-js/js/starwing/rankingDeps.json` | 1,131 B | LEGACY_ORIGINAL |
| 26 | `legacy-js/js/starwing/rankingEvent.json` | 95 B | LEGACY_ORIGINAL |
| 27 | `legacy-js/js/starwing/rankingNational.json` | 19,010 B | LEGACY_ORIGINAL |
| 28 | `legacy-js/js/starwing/rankingNational_.json` | 1,884 B | LEGACY_ORIGINAL |
| 29 | `legacy-js/js/starwing/rankingNational_2on2.json` | 10,483 B | LEGACY_ORIGINAL |
| 30 | `legacy-js/js/starwing/rankingPrefecture.json` | 10,328 B | LEGACY_ORIGINAL |
| 31 | `legacy-js/js/starwing/rankingPrefecture_2on2.json` | 10,508 B | LEGACY_ORIGINAL |
| 32 | `legacy-js/js/starwing/rankingStore.json` | 10,339 B | LEGACY_ORIGINAL |
| 33 | `legacy-js/js/starwing/rankingStore_2on2.json` | 10,519 B | LEGACY_ORIGINAL |
| 34 | `legacy-js/paradox.sql` | 92,160 B | LEGACY_ORIGINAL |

**Total: 34 legacy source files**

### Duplicate / Backup Check

- **No unchanged duplicate exists** within this directory tree. Each legacy file is
  present exactly once under `legacy-js/`.
- There is a separate `.proto` copy at `server/app/protocol/proto/starwingMessage.proto`
  (10,051 B) — this is the **server-side working copy** used for code generation. Its
  SHA-256 hash differs from the legacy original (`legacy-js/js/starwingMessage.proto` at
  10,442 B), confirming they are **not byte-identical**.

### Modification Status

**Unknown.** Without Git history or an external reference hash, it is impossible to
determine whether any legacy file has been modified from its original state. The SHA-256
hashes recorded in `LEGACY_SOURCE_SHA256.txt` serve as a **baseline snapshot** — any
future run of the same script will reveal changes made after this point.

---

## Python Rewrite Files (server/app/)

| Count | Classification |
|-------|----------------|
| 60 | PYTHON_REWRITE |
| 2 | GENERATED |
| 21 | TEST |
| 15 | DOCUMENTATION |
| 13 | UNCLASSIFIED |

### Generated Code

- `server/app/protocol/generated/__init__.py` (0 B)
- `server/app/protocol/generated/starwingMessage_pb2.py` (23,635 B)

These are protobuf-generated Python files produced from the `.proto` source files. They
should **not** be hand-edited.

### Test Files

21 test files under `server/tests/` covering API endpoints, protocol codec, unit tests,
and fixtures.

### Unclassified Server Files

These are server infrastructure/config files that don't fit the Python-rewrite or test
categories:

- `server/.env.example`, `server/.gitignore`, `server/Dockerfile`, `server/README.md`
- `server/alembic.ini`, `server/alembic/env.py`, `server/alembic/script.py.mako`
- `server/alembic/versions/.gitkeep`
- `server/docker-compose.yml`, `server/pyproject.toml`
- `server/scripts/compare_responses.py`, `server/scripts/generate_proto.py`,
  `server/scripts/inspect_legacy_schema.py`

---

## Recommendations

1. **Initialize Git immediately** — without version control, provenance of all files is
   permanently unverifiable.
2. **Pin legacy hashes** — store the SHA-256 manifest somewhere immutable (e.g., a
   private gist or signed document) as a reference baseline.
3. **Mark server proto copy** — the `server/app/protocol/proto/starwingMessage.proto`
   file should ideally be symlinked or copied from `legacy-js/js/starwingMessage.proto`
   to maintain a single source of truth. Currently they diverge.
4. **No capture/fixture binary files** (`.cap`, `.capture`, `.pcap`) were found in the
   project.

---

## Companion Files

- **`LEGACY_SOURCE_SHA256.txt`** — Full SHA-256 manifest (145 files, one per line)
- **`LEGACY_SOURCE_INTEGRITY.md`** — This document
