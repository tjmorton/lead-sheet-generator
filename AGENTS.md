# AGENTS.md

## Focused guides

When adding a focused `AGENTS.md` to a subdirectory, update this table with a one-sentence summary.

| File | Read when… |
|------|------------|
| `services/audio-detection/tests/AGENTS.md` | writing or running Python tests (mocking, fixtures, conventions) |

## Repo structure

```
lead-sheet-generator/
├── docker-compose.yml   ← at root (orchestrate all containers across services)
└── services/
    ├── audio-detection/  ← Python 3.11+ / uv / RabbitMQ worker
    └── web-app/          ← Next.js — receives analysis results, serves chord charts & scores
```

Docker Compose lives at the monorepo root. All services are under `services/`.

## Commands

Everything is run from the **service directory**, not the repo root:

```bash
cd services/audio-detection
uv sync                        # install deps into .venv
uv run ruff check .            # lint
uv run ruff format --check .   # check formatting
uv run ruff format .           # auto-fix formatting
uv run pytest -v               # all tests (ML models are mocked — tests run in seconds)
uv run download-models         # check + trigger model weight downloads
```

Docker Compose commands from repo **root**:

```bash
docker compose build
docker compose run --rm audio-detection
```

## Python conventions (audio-detection)

- **Package manager**: `uv`. Always prefix commands with `uv run`.
- **Lint/formatter**: `ruff` (not black/isort/flake8). Config in `pyproject.toml` under `[tool.ruff]`.
- **Tests**: `pytest` with `pytest-cov` and `pytest-dotenv`. Never load real ML models in tests — mock them entirely. See `services/audio-detection/tests/AGENTS.md` for full test conventions.
- **Package source**: `src/audio_detection/`. Entry points in `[project.scripts]` in `pyproject.toml`.

## Node conventions (web-app)

- TODO

## Critical dependency pins

All exist because `crema` is unmaintained:

| Pin | Why |
|-----|-----|
| `tensorflow <2.16` | crema uses Keras 2.x; TF 2.16+ ships Keras 3 |
| `numpy <2` | TF <2.16 was compiled against NumPy 1.x |
| `scikit-learn <1.7` | crema/pumpp `LabelEncoder` breaks on 1.7+ |
| `setuptools <81` | crema uses deprecated `pkg_resources` at runtime |

If crema is replaced, all four pins go away. Do not remove them otherwise.

## Model weights

| Model | Source |
|-------|--------|
| demucs (htdemucs) | Downloads ~80 MB at runtime → `~/.cache/torch/hub/` |
| basic-pitch | Bundled in pip package — no runtime download |
| crema | Bundled in pip package — no runtime download |
| madmom | Bundled in pip package — no runtime download |

# Docker Compose

Currenlty only audio-detection - which is not yet finished.

**Dev target** (Docker Compose) volume-mounts `pretrained_models/` subdirectories over the cache paths so weights survive container rebuilds. The entrypoint auto-seeds empty volumes from a build-time stash.

**Production target** bakes weights into the image. No volumes, no entrypoint.

## Dockerfiles

Once each per service

### audio-detection Dockerfile

Multi-stage build with targets: `dev`, `production`, `test`.

- `dev` — uses `docker-entrypoint-dev-model-download.sh` to seed volume mounts
- `production` — pre-downloads demucs during build, no entrypoint
- `test` — runs pytest

The build uses `--frozen` with `uv sync`. The lockfile must be kept in sync: run `uv lock` in `services/audio-detection/` after dependency changes.

### web-app Dockerfile

- TODO

# App Behaviour 

- audio-detection gets a RabbitMQ messages with an s3 url to song audio, and song metadata.
- It processes the audio via a pipline
- Sends artifacts to web-app service backend
- TODO: web-app behaviour yet to be described

## audio-dection pipeline order (when audio processing is wired up)

rhythm → stems (optional) → harmony → key → structure → MIDI (optional)

