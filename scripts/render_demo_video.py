"""Render real browser captures with local narration and captions; no fake UI frames."""

import argparse
import json
import subprocess
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAPTURE = ROOT / "artifacts/private/video-final"
OUTPUT = ROOT / "artifacts/video"


def run(*args):
    subprocess.run(
        [str(a) for a in args], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE
    )


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


def stamp(seconds):
    cs = round(seconds * 100)
    return f"{cs // 360000}:{cs // 6000 % 60:02}:{cs // 100 % 60:02}.{cs % 100:02}"


def encode_captured_frames(folder, frames, length, speech, narration, heading, audio, target):
    """Paint video captions outside the real UI, preserving source-frame timestamps."""
    import bisect
    import math

    from PIL import Image, ImageDraw, ImageFont

    body_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 34)
    header_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 23)
    command = [
        "ffmpeg",
        "-y",
        "-v",
        "error",
        "-f",
        "rawvideo",
        "-pix_fmt",
        "rgb24",
        "-s",
        "1920x1080",
        "-r",
        "6",
        "-i",
        "pipe:0",
        "-i",
        str(audio),
        "-vf",
        "fps=30",
        "-af",
        "apad",
        "-t",
        f"{length:.3f}",
        "-c:v",
        "libx264",
        "-preset",
        "fast",
        "-crf",
        "20",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-b:a",
        "160k",
        "-ar",
        "48000",
        "-movflags",
        "+faststart",
        str(target),
    ]
    log_path = target.with_suffix(".encoder.log")
    times = [f["at_ms"] / 1000 for f in frames]
    words = narration.split()
    cached_index = None
    cached_image = None
    with log_path.open("wb") as error_log:
        process = subprocess.Popen(
            command, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=error_log
        )
        try:
            for index in range(math.ceil(length * 6)):
                at = index / 6
                source_index = max(0, bisect.bisect_right(times, at) - 1)
                if source_index != cached_index:
                    with Image.open(folder / frames[source_index]["file"]) as source:
                        cached_image = source.convert("RGB").resize(
                            (1728, 972), Image.Resampling.LANCZOS
                        )
                    cached_index = source_index
                canvas = Image.new("RGB", (1920, 1080), "black")
                canvas.paste(cached_image, (96, 0))
                draw = ImageDraw.Draw(canvas)
                header = heading + " | Real UI capture - edited for time | AWS: bhoomil"
                box = draw.textbbox((110, 10), header, font=header_font)
                draw.rectangle((102, 4, min(box[2] + 8, 1816), 43), fill=(8, 15, 28))
                draw.text((110, 10), header, font=header_font, fill=(225, 245, 240))
                if at < speech:
                    word_index = min(len(words) - 1, int(at / speech * len(words)))
                    chunk = word_index // 10 * 10
                    phrase = " ".join(words[chunk : chunk + 10])
                    lines = textwrap.wrap(phrase, width=87)
                    top = 990 if len(lines) > 1 else 1010
                    for line_no, line in enumerate(lines):
                        width = draw.textlength(line, font=body_font)
                        draw.text(
                            ((1920 - width) / 2, top + line_no * 39),
                            line,
                            font=body_font,
                            fill="white",
                            stroke_width=1,
                            stroke_fill="black",
                        )
                process.stdin.write(canvas.tobytes())
        finally:
            process.stdin.close()
            code = process.wait()
        if code:
            raise RuntimeError(log_path.read_text()[-2500:])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--audio-only", action="store_true")
    args = parser.parse_args()
    plan = json.loads((OUTPUT / "edit-plan.json").read_text())
    OUTPUT.mkdir(parents=True, exist_ok=True)
    rendered = []
    manifest = []
    all_subtitles = []
    offset = 0
    for chapter in plan:
        name = chapter["capture"]
        work = OUTPUT / name
        work.mkdir(exist_ok=True)
        script = work / "narration.txt"
        script.write_text(chapter["narration"])
        audio = work / "voice.aiff"
        run("say", "-v", "Samantha", "-r", "145", "-f", script, "-o", audio)
        speech = duration(audio)
        if args.audio_only:
            print(name, round(speech, 2), "seconds of narration", flush=True)
            continue
        capture = json.loads((CAPTURE / name / "capture.json").read_text())
        capture_ms = (
            min(capture["duration_ms"], int(chapter["trim_seconds"] * 1000))
            if chapter.get("trim_seconds")
            else capture["duration_ms"]
        )
        frames = [f for f in capture["frames"] if f["at_ms"] < capture_ms]
        if not frames:
            raise RuntimeError(f"No actual captured frames for {name}")
        length = max(capture_ms / 1000, speech + 0.5)
        concat = work / "frames.ffconcat"
        lines = ["ffconcat version 1.0"]
        for index, frame in enumerate(frames):
            next_ms = frames[index + 1]["at_ms"] if index + 1 < len(frames) else capture_ms
            interval = max(0.001, (next_ms - frame["at_ms"]) / 1000)
            lines += [f"file '{CAPTURE / name / frame['file']}'", f"duration {interval:.6f}"]
        lines += [f"file '{CAPTURE / name / frames[-1]['file']}'"]
        concat.write_text("\n".join(lines) + "\n")
        ass = work / "captions.ass"
        header = """[Script Info]\nScriptType: v4.00+\nPlayResX: 1920\nPlayResY: 1080\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\nStyle: Default,Arial,34,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,1,0,2,110,110,14,1\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"""
        words = chapter["narration"].split()
        events = []
        for index in range(0, len(words), 10):
            phrase = " ".join(words[index : index + 10])
            begin = speech * index / len(words)
            end = speech * min(index + 10, len(words)) / len(words)
            label = "\\N".join(textwrap.wrap(phrase, width=87))
            events.append(f"Dialogue: 0,{stamp(begin)},{stamp(end)},Default,,0,0,0,,{label}")
            all_subtitles.append({"start": offset + begin, "end": offset + end, "text": phrase})
        ass.write_text(header + "\n".join(events) + "\n")
        title = work / "chapter-title.txt"
        title.write_text(chapter["title"] + "  |  Actual browser capture - edited for time")
        mp4 = work / "chapter.mp4"
        encode_captured_frames(
            CAPTURE / name,
            frames,
            length,
            speech,
            chapter["narration"],
            chapter["title"],
            audio,
            mp4,
        )
        rendered.append(mp4)
        manifest.append(
            {
                "chapter": name,
                "actual_frames": len(frames),
                "captured_at_utc": capture["started_at_utc"],
                "video_seconds": round(length, 3),
                "narration_seconds": round(speech, 3),
            }
        )
        offset += length
        print(name, len(frames), "real frames rendered;", round(length, 2), "seconds", flush=True)
    if args.audio_only:
        return
    if offset >= 180:
        raise RuntimeError(f"Demo is too long: {offset:.2f} seconds")
    listing = OUTPUT / "chapters.ffconcat"
    listing.write_text("ffconcat version 1.0\n" + "\n".join(f"file '{p}'" for p in rendered) + "\n")
    final = OUTPUT / "OpsPilot-AI-Hackathon-Demo.mp4"
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

    def srt_time(seconds):
        ms = round(seconds * 1000)
        return f"{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02},{ms % 1000:03}"

    (OUTPUT / "OpsPilot-AI-Hackathon-Demo.srt").write_text(
        "\n\n".join(
            f"{i}\n{srt_time(s['start'])} --> {srt_time(s['end'])}\n{s['text']}"
            for i, s in enumerate(all_subtitles, 1)
        )
        + "\n"
    )
    (OUTPUT / "recording-manifest.json").write_text(
        json.dumps(
            {
                "chapters": manifest,
                "rendered_duration_seconds": duration(final),
                "narration": "Local synthesized English voice: Samantha",
                "capture": "Actual dashboard browser frames sampled continuously; edited chapters, no mock UI.",
            },
            indent=2,
        )
    )
    print("FINAL:", final, duration(final), "seconds", flush=True)


if __name__ == "__main__":
    main()
