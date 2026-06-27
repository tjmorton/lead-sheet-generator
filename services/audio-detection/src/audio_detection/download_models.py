import os
import sys


def _check_demucs():
    from demucs.pretrained import get_model

    cache = os.path.expanduser("~/.cache/torch/hub/checkpoints")
    print("host: pretrained_models/torch_hub/checkpoints/")
    print(f"container: {cache}")

    existing = os.listdir(cache) if os.path.isdir(cache) else []
    th_files = [f for f in existing if f.endswith(".th")]
    if th_files:
        print(f"  status: cached ({len(th_files)} .th files)")
        for f in sorted(th_files):
            print(f"    {f}")
    else:
        print("  status: downloading htdemucs (~80 MB)...")
        get_model("htdemucs")
        new = [f for f in os.listdir(cache) if f.endswith(".th")]
        print(f"  status: downloaded ({len(new)} .th files)")
        for f in sorted(new):
            print(f"    {f}")


def _check_basic_pitch():
    from pathlib import Path

    import basic_pitch

    model_dir = str(Path(basic_pitch.__file__).parent / "saved_models" / "icassp_2022")
    print("host: pretrained_models/basic_pitch/")
    print(f"container: {model_dir}")

    n_files = sum(1 for _r, _d, fs in os.walk(model_dir) for _ in fs)
    print(f"  status: {n_files} files")


def _check_crema():
    from pathlib import Path

    import pkg_resources

    model_path = Path(pkg_resources.resource_filename("crema.models.chord", "model.h5"))
    model_dir = str(model_path.parent)
    print("host: pretrained_models/crema/")
    print(f"container: {model_dir}")

    expected = ["model.h5", "model_spec.pkl", "pump.pkl", "version.txt"]
    found = [f for f in expected if (model_path.parent / f).exists()]
    print(f"  status: {len(found)}/{len(expected)} expected files")


def _check_madmom():
    from pathlib import Path

    import madmom.models

    models_dir = str(Path(madmom.models.__file__).parent)
    print("host: pretrained_models/madmom/")
    print(f"container: {models_dir}")

    pkl_count = 0
    for _root, _dirs, files in os.walk(models_dir):
        pkl_count += sum(1 for f in files if f.endswith(".pkl"))
    print(f"  status: {pkl_count} .pkl files")


def main():
    print("=== ML Model Status ===\n")

    checks = [
        ("demucs (stem separation) — downloads at runtime", _check_demucs),
        ("basic-pitch (MIDI transcription) — bundled in pip", _check_basic_pitch),
        ("crema (chord detection) — bundled in pip", _check_crema),
        ("madmom (beat/downbeat/key) — bundled in pip", _check_madmom),
    ]

    failed = False
    for label, fn in checks:
        print(f"--- {label} ---")
        try:
            fn()
        except Exception as e:
            print(f"  error: {e}")
            failed = True
        print()

    if failed:
        sys.exit(1)

    print("All models ready.")


if __name__ == "__main__":
    main()
