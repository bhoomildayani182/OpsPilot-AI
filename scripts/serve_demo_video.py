"""Local-only artifact preview with byte ranges for native video seeking."""

import io
import re
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "artifacts/video"


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def send_head(self):
        path = Path(self.translate_path(self.path))
        match = re.fullmatch(r"bytes=(\d+)-(\d*)", self.headers.get("Range", ""))
        if (
            match
            and path.suffix == ".mp4"
            and path.is_file()
            and path.resolve().is_relative_to(ROOT)
        ):
            size = path.stat().st_size
            start = int(match[1])
            end = min(int(match[2]) if match[2] else size - 1, size - 1)
            if start > end:
                self.send_error(416)
                return None
            self.send_response(206)
            self.send_header("Content-Type", "video/mp4")
            self.send_header("Accept-Ranges", "bytes")
            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
            self.send_header("Content-Length", str(end - start + 1))
            self.end_headers()
            with path.open("rb") as stream:
                stream.seek(start)
                return io.BytesIO(stream.read(end - start + 1))
        return super().send_head()


if __name__ == "__main__":
    ThreadingHTTPServer(("127.0.0.1", 8512), Handler).serve_forever()
