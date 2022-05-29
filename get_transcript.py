"""
Get transcripts from youtube.

Portions of code here taken from:
* https://github.com/AKGV1/ytseach (MIT) and
* https://github.com/NoahCardoza/noter (unlicensed)

Once Invidious is updated to use the innertube api, for transcripts
much of the code here can be removed.
"""

from dataclasses import dataclass
import json
from urllib.request import Request, urlopen
from pprint import pprint


@dataclass
class TranscriptCue:
    """A transcript cue."""

    start: int # Time into the video when the cue starts in seconds.
    text: str # Spoken text

    def start_time_text(self) -> str:
        """Return the start time of the cue in the form minutes:ss."""
        minute_part = self.start // 60
        second_part = self.start % 60
        return f'{minute_part}12:{second_part:02d}'

    def youtube_link_tag(self, youtube_id: str) -> str:
        """Return a html link to the youtube video at the cue start time."""
        return (
            '<a href="https://www.youtube.com/watch'
            f'?v={youtube_id}&t={self.start}">{self.start_time_text()}</a>'
        )


def _get_youtube_page(url: str) -> str:
    """Get the page for a youtube url."""
    video_page_request = Request(url)
    with urlopen(video_page_request) as response:
        text = response.read().decode('utf-8')

    return text


def _parse_value_from_page_text(text: str, key: str) -> str:
    """Get the value for a key from a page text."""
    return text.split(f'"{key}":"')[1].split('"')[0]


def _get_transcript_from_innertube_api(
        serialized_share_entity: str,
        inner_tube_api_key: str
    ) -> dict:
    """
    Get a transcript from the innertube api.

    Args:
        serialized_share_entity: (whatever that is).
            It is just a string of random encoded data parsed from the youtube
            page.
        inner_tube_api_key: The innertube api key. A random string of
            characters that is parsed out of the youtube page.
    """
    user_agent = (
        # Probably doesn't matter that much. Just make it look like a browser.
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/97.0.4692.99 Safari/537.36 OPR/83.0.4254.70,gzip(gfe)'
    )
    payload = {
        "context": {
                "client": {
                    "userAgent": user_agent,
                    "clientName": "WEB",
                    "clientVersion": "2.20220309.01.00",
                }
        },
        "params": serialized_share_entity
    }

    transcript_request = Request(
        f'https://www.youtube.com/youtubei/v1/get_transcript?key={inner_tube_api_key}',
        json.dumps(payload).encode('utf-8'),
        {'Content-Type': 'application/json'},
    )

    with urlopen(transcript_request) as response:
        transcript_data = json.loads(response.read())

    return transcript_data

def get_transcript(youtube_id: str) -> list[TranscriptCue]:
    """
    Get a transcript for a youtube url using the innertube api.

    Args:
        youtube_id: The youtube id of the video.
    Returns:
        A list of TranscriptCues.
    """
    transcript_log = []

    text = _get_youtube_page(f"https://www.youtube.com/watch?v={youtube_id}")

    innertube_api_key = _parse_value_from_page_text(text, 'INNERTUBE_API_KEY')
    serialized_share_entity = _parse_value_from_page_text(
        text,
        'serializedShareEntity'
    )
    transcript_data = _get_transcript_from_innertube_api(
        serialized_share_entity,
        innertube_api_key
    )

    for action in transcript_data['actions']:
        for group in (
                action['updateEngagementPanelAction']['content']
                ['transcriptRenderer']['body']['transcriptBodyRenderer'
                ]['cueGroups']
            ):
            for cue in group['transcriptCueGroupRenderer']['cues']:
                renderer = cue['transcriptCueRenderer']
                time = int(float(renderer['startOffsetMs']) / 1000)
                text = renderer['cue']['simpleText']
                transcript_log.append(
                    TranscriptCue(time, text)
                )

    return transcript_log


if __name__ == '__main__':
    pprint(
        get_transcript('yg9HwXI6Ha0')
    )
