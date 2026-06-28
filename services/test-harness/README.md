- Python service
- Publishes to a RabbitMQ topic with an s3 URL to audio, and song metadata
- Used to test end-to-end flow of audio-detection -> web-app

# Development

The test-harness service uses python, and uv.

- Run `uv sync` in this service directory create a virtual env, and download dependencies.
- When doing development in some code editors, you may need to point it at the python interpreter in your .venv
- In VS Code, open the command pallette and select 'Python: Select Interpreter', and point to a file path: `services/audio-detection/.venv/bin/python`

## Linting/formatter
```bash
uv run ruff check .          # lint
uv run ruff format --check . # check formatting
uv run ruff format .         # auto-fix formatting
```
## Unit Tests

- Our `pyproject.toml` tells pytest how to find and run our tests in tool.pytest.ini_options section

```bash
uv run pytest -v
```

# Running

## Running the app via uv

From this directory:

```bash
uv run --env-file .env test-harness
```

## Running the app via docker compose (recommended)

From the root of the monorepo:

```bash
docker compose run --rm test-harness
```