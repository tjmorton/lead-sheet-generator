"""App config via environment variables module

Loads and validate environment variables at import time (ideally app startup),
ensureing all required configuration is present before the application runs
"""

import os


def _get_required_env(var_name: str) -> str:
    """Get a required environment variable. Raises a ValueError if missing"""
    value = os.getenv(var_name)
    if not value:
        raise ValueError(f"{var_name} environment variable is required but not set")
    return value


def _get_env_with_default(var_name: str, default_value: str) -> str:
    """Get an environment variable. Returns default_value if missing"""
    value = os.getenv(var_name)
    if not value:
        return default_value
    return value


def _get_env_as_boolean(var_name: str, default_value: bool) -> bool:
    """Get an environment variable. Returns default_value if missing"""
    value = os.getenv(var_name)

    # If the value is missing, return the default
    # TODO: (tjm) I should get rid of this concept - feature flags should always be set
    # as True or False
    if not value:
        return default_value

    value_is_truthy = (value == "True") or (value == "true")
    value_is_falsey = (value == "False") or (value == "false")

    if not value_is_truthy and not value_is_falsey:
        raise ValueError(f"{var_name} is required to be True or False")

    return value_is_truthy


# TODO: (tjm) I should make this a TypedDict
# load_environment runs on first import, _not_ when we first call get_environment
# so the first module to import environment will run this, and throw if misconfigred
def _load_environment() -> dict:
    """Load and validate environment configuration"""
    config = {
        # RabbitMQ vars
        "rabbitmq_host": _get_required_env("RABBITMQ_HOST"),
        "rabbitmq_port": int(_get_required_env("RABBITMQ_PORT")),
        "rabbitmq_queue_name": _get_required_env("RABBITMQ_QUEUE_NAME"),
        "rabbitmq_user": _get_required_env("RABBITMQ_USER"),
        "rabbitmq_password": _get_required_env("RABBITMQ_PASSWORD"),
        # AWS vars (for S3 bucket)
        "aws_endpoint_url": _get_required_env("AWS_ENDPOINT_URL"),
        "aws_access_key_id": _get_required_env("AWS_ACCESS_KEY_ID"),
        "aws_secret_access_key": _get_required_env("AWS_SECRET_ACCESS_KEY"),
        "aws_region": _get_required_env("AWS_REGION"),
        "s3_bucket_name": _get_required_env("S3_BUCKET_NAME"),
        "web_app_host": _get_required_env("WEB_APP_HOST"),
        # --- Optional feature flags ---
        # TODO: (tjm) Most of these flags are from my vibe coded POC
        #   Go through them and determine what's still needed
        # Set ENABLE_STEM_SEPARATION=true to run Demucs stem separation.
        # Automatically enabled when chord_mode=no_vocals or debug_chord_diff=true.
        "enable_stem_separation": _get_env_as_boolean("ENABLE_STEM_SEPARATION", False),
        # Set ENABLE_MIDI_GENERATION=true to generate MIDI files from stems.
        # Automatically enabled when debug_midi_to_disk=true.
        # Requires stem separation to be enabled (will enable it implicitly).
        "enable_midi_generation": _get_env_as_boolean("ENABLE_MIDI_GENERATION", False),
        # Set CHORD_MODE=no_vocals to run harmony detection on the
        # accompaniment (drums+bass+other) instead of the full mix.
        # Set CHORD_MODE=full_mix to run harmony detection on full mix
        # TODO: (tjm) Code that used to read this expected empty string to equal full mix
        # Implicitly enables stem separation.
        "chord_mode": _get_env_with_default("CHORD_MODE", "full_mix"),
        # Set DEBUG_CHORD_DIFF=true to run harmony detection twice (full mix
        # AND no-vocals) and write diff-friendly text files to /app/output.
        # Implicitly enables stem separation.
        "debug_chord_diff": _get_env_as_boolean("DEBUG_CHORD_DIFF", False),
        # Set DEBUG_MIDI_TO_DISK=true to write .mid files to /app/output
        # instead of just logging.  Implicitly enables MIDI generation.
        "debug_midi_to_disk": _get_env_as_boolean("DEBUG_MIDI_TO_DISK", False),
        # Set MIDI_REPLAY_CHORDS_AT_BAR=false to disable re-triggering
        # sustained chords at bar boundaries in the chord MIDI.  Defaults
        # to "true" so piano / pad voicings don't decay to silence over
        # long held chords.
        "midi_replay_chords_at_bar": _get_env_as_boolean("MIDI_REPLAY_CHORDS_AT_BAR", True),
        # Set MIDI_QUANTIZE=false to disable snapping vocal and bass MIDI
        # note onsets and offsets to the nearest 16th-note grid position.
        # Defaults to "true" for a tighter, more notation-friendly result.
        "midi_quantize": _get_env_as_boolean("MIDI_QUANTIZE", True),
        # Set VOCAL_MIDI_BACKEND to choose the live vocal MIDI source.
        # Supported values: basic_pitch, omnizart.
        "vocal_midi_backend": _get_env_with_default("VOCAL_MIDI_BACKEND", "basic_pitch"),
        # Set VOCAL_MIDI_PROFILE to choose the vocal cleanup preset.
        # Supported values: default, balanced, high_quality.
        "vocal_midi_profile": _get_env_with_default("VOCAL_MIDI_PROFILE", "default"),
        # Optional vocal MIDI cleanup flags.
        # When set, discard transcribed vocal notes outside the provided inclusive MIDI pitch range.
        "vocal_midi_min_pitch": _get_env_with_default("VOCAL_MIDI_MIN_PITCH", "36"),
        "vocal_midi_max_pitch": _get_env_with_default("VOCAL_MIDI_MAX_PITCH", "84"),
        # TODO: (tjm) I think cleanup_boundary and cleanup_sustain_normalization should be
        #   cleanup_vocal_boundary and cleanup_vocal_sustain_normalization
        # When set, ... TODO: (tjm) Remind myself what this does
        "cleanup_boundary": _get_env_as_boolean("MIDI_CLEANUP_BOUNDARY", True),
        # When set, ... TODO: (tjm) Remind myself what this does
        "cleanup_sustain_normalization": _get_env_as_boolean(
            "MIDI_CLEANUP_SUSTAIN_NORMALIZATION",
            True,
        ),
        # When set, ... TODO: (tjm) Remind myself what this does
        "cleanup_bass_boundary": _get_env_as_boolean("MIDI_CLEANUP_BASS_BOUNDARY", True),
        # When set, ... TODO: (tjm) Remind myself what this does
        "cleanup_bass_sustain_normalization": _get_env_as_boolean(
            "MIDI_CLEANUP_BASS_SUSTAIN_NORMALIZATION",
            True,
        ),
        # When set, ... TODO: (tjm) Remind myself what this does
        "cleanup_bass_debris": _get_env_as_boolean("MIDI_CLEANUP_BASS_DEBRIS", True),
    }

    return config


# Load the environment at module level
_ENVIRONMENT = _load_environment()


def get_environment() -> dict:
    """Get the validated environment config

    Returns:
        dict: Dictionary containing environment configuration
    """
    return _ENVIRONMENT
