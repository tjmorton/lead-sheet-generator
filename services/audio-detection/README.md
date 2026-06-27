- Python service
- Listens on a RabbitMQ topic with an s3 URL to audio, and song metadata
- Extracts song chords, song stems, and generates midi from stem audio
- Uploads chords json blob, song metadata, and midi and audio stems to web-app backend.

# Development

The audio-dection service uses python, and uv.

- Run `uv sync` in this service directory create a virtual env, and download dependencies.
- When doing development in some code editors, you may need to point it at the python interpreter in your .venv
- In VS Code, open the command pallette and select 'Python: Select Interpreter', and point to a file path: `services/audio-detection/.venv/bin/python`

## Linting/formatter:
```bash
uv run ruff check .          # lint
uv run ruff format --check . # check formatting
uv run ruff format .         # auto-fix formatting
```

# Running

# Clean test
```bash
# From monorepo root (where the docker compose lives)
rm -rf services/audio-detection/pretrained_models/*/
docker compose build
docker compose run --rm audio-detection   # first run: populates volumes, downloads demucs
docker compose run --rm audio-detection   # second run: should be instant (no "populating" messages)
Prod:
docker build -t audio-detection:prod \
  -f services/audio-detection/Dockerfile \
  --target production \
  services/audio-detection
docker run --rm audio-detection:prod
```

