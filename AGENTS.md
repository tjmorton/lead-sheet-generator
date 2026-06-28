# AGENTS.md

## Focused guides

When adding a focused `AGENTS.md` to a subdirectory, update this table with a one-sentence summary.

| File | Read when… |
|------|------------|
| `services/audio-detection/tests/AGENTS.md` | writing or running Python tests (mocking, fixtures, conventions) |
| `services/test-harness/tests/AGENTS.md` | test-harness test conventions (mocking, fixtures, conventions) |

## Repo structure

```
lead-sheet-generator/
├── docker-compose.yml   ← at root (orchestrate all containers across services)
└── services/
    ├── audio-detection/  ← Python 3.11+ / uv / RabbitMQ worker
    ├── test-harness/     ← Python 3.11+ / uv / publishes example messages to RabbitMQ
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
uv run audio-detection         # starts the service (runs model check on startup)

cd services/test-harness
uv sync                        # install deps into .venv
uv run ruff check .            # lint
uv run ruff format --check .   # check formatting
uv run ruff format .           # auto-fix formatting
uv run pytest -v               # all tests
uv run test-harness            # publishes one message to RabbitMQ and exits
```

Docker Compose commands from repo **root**:

```bash
docker compose build
docker compose run --rm audio-detection
docker compose run --rm test-harness   # publishes an example message, then exits
```

## Python conventions (audio-detection, test-harness)

- **Package manager**: `uv`. Always prefix commands with `uv run`.
- **Lint/formatter**: `ruff` (not black/isort/flake8). Config in `pyproject.toml` under `[tool.ruff]`.
- **Tests**: `pytest` with `pytest-cov` and `pytest-dotenv`. See `services/audio-detection/tests/AGENTS.md` or `services/test-harness/tests/AGENTS.md` for full test conventions.
- **Package source**: `src/package_name/`. Entry points in `[project.scripts]` in `pyproject.toml`.
- **Return type annotations**: Every function must have an explicit return type, even `None`. Do not leave it implicit.

  ```python
  # Correct
  def ensure_ml_models() -> None: ...
  def get_model_path(name: str) -> Path: ...
  def maybe_load(name: str) -> Model | None: ...

  # Wrong — missing return type
  def ensure_ml_models(): ...
  ```

## Node conventions (web-app)

- TODO

## Critical conventions

- **Preserve user comments — never delete them without asking.** This includes commented-out code, TODO/NOTE/HACK/FIXME markers, and any explanatory notes. If you need to move or restructure code around a comment, keep the comment. Ask before removing. The `__main__.py` NOTE block from Tom is a standing example — never touch it.
- **Return type annotations**: Every function must have an explicit return type, even `None`. Do not leave it implicit.

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

End-to-end testing is done by running the full stack:

```bash
docker compose up audio-detection        # starts RabbitMQ + audio-detection worker
docker compose run --rm test-harness      # publishes an example message, then exits
```

`test-harness` depends on `audio-detection`, which depends on RabbitMQ (healthy). Running `test-harness` brings up the full dependency chain automatically.

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

### test-harness Dockerfile

Multi-stage build with targets: `dev`, `test`.

- `dev` — publishes an example message to RabbitMQ, then exits
- `test` — runs pytest

Runtime deps are just `pika`. No ML models — a single `uv sync --frozen --no-dev` in the base image. The lockfile must be kept in sync: run `uv lock` in `services/test-harness/` after dependency changes.

# App Behaviour 

- audio-detection gets a RabbitMQ messages with an s3 url to song audio, and song metadata.
- It processes the audio via a pipline
- Sends artifacts to web-app service backend
- test-harness publishes an example message to the audio-detection queue for end-to-end testing
- TODO: web-app behaviour yet to be described

## audio-dection pipeline order (when audio processing is wired up)

rhythm → stems (optional) → harmony → key → structure → MIDI (optional)

