- Python service
- Listens on a RabbitMQ topic with an s3 URL to audio, and song metadata
- Extracts song chords, song stems, and generates midi from stem audio
- Uploads chords json blob, song metadata, and midi and audio stems to web-app backend.

# Running

# Clean test
```bash
# From services/audio-decetion
-rf pretrained_models/*/
# From monorepo root (where the docker compose lives)
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

# Linting/formatter:
```bash
uv run ruff check .          # lint
uv run ruff format --check . # check formatting
uv run ruff format .         # auto-fix formatting
```