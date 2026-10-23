"""Render timestamped real browser captures with narration and no subtitle overlays."""

import argparse
import json
import subprocess
from pathlib import Path


def run(*args):
    subprocess.run([str(a) for a in args], check=True, capture_output=True)


def duration(path):
    return float(
        subprocess.check_output(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=nw=1:nk=1",
                str(path),
            ]
        )
    )


def quoted(path):
    return str(path.resolve()).replace("'", "'\\''")


def render(plan_path, captures, output):
    plan = json.loads(plan_path.read_text())
    chapters = []
    receipts = []
    output.mkdir(parents=True, exist_ok=True)
    for chapter in plan:
        name = chapter["capture"]
        folder = captures / name
        capture = json.loads((folder / "capture.json").read_text())
        audio = output / name / "voice.mp3"
        if not audio.is_file():
            raise ValueError(f"Missing verified narration: {audio}")
        frames = capture["frames"]
        end = min(capture["duration_ms"], chapter.get("trim_seconds", 9999) * 1000)
        frames = [f for f in frames if f["at_ms"] < end]
        if not frames:
            raise ValueError(f"No captured UI frames for {name}")
        lines = ["ffconcat version 1.0"]
        for index, frame in enumerate(frames):
            next_at = frames[index + 1]["at_ms"] if index + 1 < len(frames) else end
            lines.extend(
                [
                    f"file '{quoted(folder / frame['file'])}'",
                    f"duration {max(0.001, (next_at - frame['at_ms']) / 1000):.6f}",
                ]
            )
        lines.append(f"file '{quoted(folder / frames[-1]['file'])}'")
        listing = output / name / "frames.ffconcat"
        listing.write_text("\n".join(lines) + "\n")
        seconds = max((end - frames[0]["at_ms"]) / 1000, duration(audio) + 0.4)
        target = output / name / "chapter.mp4"
        run(
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            listing,
            "-i",
            audio,
            "-vf",
            "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,tpad=stop_mode=clone:stop_duration=180,fps=30,format=yuv420p",
            "-af",
            "loudnorm=I=-16:TP=-1.5:LRA=11,apad",
            "-t",
            f"{seconds:.3f}",
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-crf",
            "19",
            "-c:a",
            "aac",
            "-ar",
            "48000",
            "-b:a",
            "192k",
            "-movflags",
            "+faststart",
            target,
        )
        chapters.append(target)
        receipts.append(
            {
                "chapter": name,
                "actual_frames": len(frames),
                "captured_at_utc": capture["started_at_utc"],
                "duration_seconds": duration(target),
            }
        )
    if sum(c["duration_seconds"] for c in receipts) >= 180:
        raise ValueError("Recording exceeds the hackathon's three-minute limit")
    listing = output / "chapters.ffconcat"
    listing.write_text(
        "ffconcat version 1.0\n" + "\n".join(f"file '{quoted(path)}'" for path in chapters) + "\n"
    )
    final = output / "OpsPilot-AI-Demo-Male-No-Subtitles.mp4"
    run(
        "ffmpeg",
        "-y",
        "-v",
        "error",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        listing,
        "-c",
        "copy",
        "-movflags",
        "+faststart",
        final,
    )
    probe = json.loads(
        subprocess.check_output(
            ["ffprobe", "-v", "error", "-show_streams", "-of", "json", str(final)]
        )
    )
    assert not any(s["codec_type"] == "subtitle" for s in probe["streams"])
    (output / "recording-manifest.json").write_text(
        json.dumps(
            {
                "chapters": receipts,
                "duration_seconds": duration(final),
                "subtitles": False,
                "overlays": False,
                "capture": "Actual timestamped browser frames; edited for time; final frame held for narration as needed.",
                "narration": "Male synthetic voice; provider and request receipts in narration-manifest.json",
            },
            indent=2,
        )
    )
    run("ffmpeg", "-v", "error", "-i", final, "-f", "null", "-")
    print(final)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--captures", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    render(args.plan, args.captures, args.output)
