import re
from dataclasses import dataclass
from urllib.parse import urlparse, parse_qs
from youtube_transcript_api import YouTubeTranscriptApi

@dataclass
class TranscriptResult:
    video_id: str
    text: str
    language: str
    is_generated: bool

class TranscriptFetcher:
    VIDEO_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{11}$")

    def extract_video_id(self, url):
        if not url or not url.strip():
            raise ValueError("Please enter a YouTube URL.")
        value = url.strip()
        if self.VIDEO_ID_PATTERN.fullmatch(value):
            return value
        parsed = urlparse(value if "://" in value else f"https://{value}")
        host = (parsed.hostname or "").lower()
        video_id = None
        if host in {"youtu.be", "www.youtu.be"}:
            video_id = parsed.path.strip("/").split("/")[0]
        elif host.endswith("youtube.com") or host.endswith("youtube-nocookie.com"):
            if parsed.path == "/watch":
                video_id = parse_qs(parsed.query).get("v", [None])[0]
            else:
                parts = [p for p in parsed.path.split("/") if p]
                if len(parts) >= 2 and parts[0] in {"embed", "shorts", "live", "v"}:
                    video_id = parts[1]
        if not video_id or not self.VIDEO_ID_PATTERN.fullmatch(video_id):
            raise ValueError("That doesn't look like a valid YouTube video URL.")
        return video_id

    def fetch(self, video_id, languages=None):
        transcript = YouTubeTranscriptApi().fetch(video_id, languages=languages or ["en"])
        text = " ".join(s.text.replace("\\n", " ").strip()
                        for s in transcript.snippets if s.text.strip())
        if not text:
            raise RuntimeError("The transcript is empty.")
        return TranscriptResult(video_id, text,
            getattr(transcript, "language", "unknown"),
            bool(getattr(transcript, "is_generated", False)))
