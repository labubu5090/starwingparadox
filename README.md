# Starwing Paradox — Private / Offline Server & Toolchain

An operator-owned engineering effort to run the **Starwing Paradox** arcade cabinet game
(FMV mecha fighter) in a controlled, offline environment. This repository contains a
clean-room **Python (FastAPI) game server**, a **local offline launcher**, a **NESYS
named-pipe stub**, and a large body of **reverse-engineering documentation and tooling**
produced through a staged investigation (the "Phase 2A-Gxx" phases).

> **Important** — This repo contains **no proprietary game binaries, no IDA databases,
> and no packet captures**. It holds operator-written source code, documentation, and
> analysis artifacts only. See [Legal & Content Policy](#legal--content-policy).

---

## What's Here

| Area | Path | Description |
|------|------|-------------|
| **Game server** | [`server/`](server/) | FastAPI server (+ TCP listener), SQLite persistence, local player profiles |
| **Offline launcher** | [`tools/local_launcher/`](tools/local_launcher/) | PyQt5 GUI launcher with environment checks, process management, session logging |
| **NESYS pipe stub** | `tools/local_launcher/nesys_pipe.py` | Named-pipe responder for card-select/insert requests |
| **Proxy & network tools** | `tools/g30_proxy.py`, `tools/local_dns.py`, `tools/nesys_*` | DNS / HTTP / NESYS interception for controlled capture |
| **Controller mapper** | [`tools/controller_mapper/`](tools/controller_mapper/) | XInput to keyboard mapping for cabinet play |
| **Profile manager** | `tools/profile_manager/` | Local-profile GUI + status dashboard |
| **RE tooling** | [`tools/ida/`](tools/ida/), [`tools/ida_g21/`](tools/ida_g21/), [`tools/patch/`](tools/patch/) | IDA/Angr/bytescan analysis scripts, patch tooling |
| **Documentation** | [`docs/`](docs/) | Phase reports, contracts, root-cause analyses |
| **Analysis artifacts** | [`artifacts/`](artifacts/) | Evidence JSON per investigative phase |
| **Tests** | [`tests/`](tests/), `server/tests/` | pytest suites (server + clean-room protocol) |

---

## Project Status

The investigation is driven by staged "G-phases"; each phase ends with a final report in
`docs/` and evidence JSON in `artifacts/`. A living summary is maintained in
[`PROGRESS.md`](PROGRESS.md).

Headline state and findings:

- **Onboarding achieved** — the cabinet game completes its full first-time onboarding
  flow and a **tutorial battle** locally (G36).
- **Server/HTTP startup** — game reads `MatchingServer : 127.0.0.1:6666` from the INI
  config and reaches the local matching endpoint successfully (G35/G44/G47).
- **Matching path on-line** — `POST .../mock/matching/server` accepted by the game
  (`IsSuccess=1`, connect address `127.0.0.1:6666`).
- **Clean-room protocol foundation** — evidence-locked transport/session/codec layer
  with a deterministic harness (G17/G18).
- **Local player profiles** — SQLite-backed local profiles + CRUD API + card-style GUI
  (G39/G43).
- **Remaining blocker** — the NESYS/NESiCA card flow. The card-insert gate is coupled to
  NESYS certificate trust and NESICA reception; passing the card screen so the game
  advances to online matchmaking is the current focus (G38/G40/G44/G45/G47/G48).

The matching engine and battle lifecycle remain **not implemented** by design; the work
currently targets getting a single cabinet through the card screen and into the online
matchmaking queue rather than a full feature server.

---

## Quick Start

See [`docs/G46_LOCAL_LAUNCHER_GUIDE.md`](docs/G46_LOCAL_LAUNCHER_GUIDE.md) and
[`server/README.md`](server/README.md) for full instructions. Overview:

**Server:**

```powershell
cd server
# create venv, install deps, configure .env (see .env.example)
uvicorn app.main:app --host 0.0.0.0 --port 4001
```

**Launcher** (`tools/local_launcher/app.py`): PyQt5 GUI that performs environment checks,
starts the required local processes in a strict sequence, launches the game, and logs the
session to JSONL.

**Network tooling** — the repo assumes you run a local DNS/proxy stack so the game's
hardcoded `http://dev.starwing.jp/mock` endpoint resolves to `127.0.0.1` (there is **no
supported client-side endpoint override** — G19). See `tools/setup_dns.py` /
`tools/g30_proxy.py`.

---

## Repository Layout

```
server/        Python (FastAPI) game server + TCP listener + SQLite + tests
tools/         Launcher, proxy/DNS, controller mapper, profiles, RE/patch scripts
docs/          Phase reports, contracts, root-cause write-ups
artifacts/     Structured evidence JSON per investigative phase
tests/         Clean-room protocol / fixture tests
legacy-js/     Reference-only legacy JS server clone (NOT modified)
PROGRESS.md    Living phase/progress tracker
```

---

## Legal & Content Policy

This project is an **operator-owned reverse-engineering and interoperability effort** for
the operator's own hardware. To keep this repository safe for public sharing it
**deliberately excludes**:

- Proprietary game executables / binaries
- IDA databases (`.i64`) and analysis projects
- Packet captures and raw network traces
- Runtime session/log dumps

The code and documents here are the operator's own clean-room implementation and notes.
Nothing in this repo claims to reproduce, redistribute, or emulate the game's proprietary
assets. Operate it only on hardware and software you own.

---

## Testing

```powershell
# server tests
cd server
pytest -v

# clean-room protocol tests
pytest -v tests/
```

Gates used across phases: `pytest` green, `mypy` 0 errors, `ruff` 0 errors, no restricted
imports, no production hostnames/cert/pipe/registry references in the clean-room layer.
