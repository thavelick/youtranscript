# youTranscript

A frontend for youtube that shows transcripts instead of videos.

## Installation and Usage

1. Clone
  ```
  git clone https://github.com/thavelick/youtranscript && cd youtranscript
  ```
2. Install dependencies
  ```
  pip install -r requirements.txt
  ```
3. Start the server
  ```bash
  # Make sure to use a real invidious host here
  YOUTRANSCRIPT_INVIDIOUS_HOST=your-favorite.invidious.host ./youtranscript.py
  ```
3. Open your browser to http://localhost:8008/

### Environment variables

* `YOUTRANSCRIPT_INVIDIOUS_HOST`: required -  the hostname of the invidious instance
to use to pull youtube transcripts and search results. For a list of available
instances check: https://api.invidious.io/. Make sure you pick one with a
checkmark for API.

## Urls

The urls should mostly correspond to youtube.com ones, so you can replace https://youtube.com with
http://localhost:8008/ and it will work.

## Dependencies
* Python 3.10
* youtube_transcript_api 0.4.4

# TODO
* choose a random invidious instance if one isn't specified
* Use a template engine instead of hard-coding html
* Clean up the design
  * The W3C's
    [Web Content Accessibility Guidelines](https://www.w3.org/TR/WCAG21/)
    seem like a good starting point, not just for users with disabilities
    but for everyone.
* Add accessibility features
* Add search box to the results and transcript pages
* Add title and other metadata to the transcript pages
* Commission or make a cool logo
* Add punctuation restoration to auto-generated transcripts
* Add some copy to the homepage about how cool this is
* Public hosting
* Figure out scale
  * Move transcript fetching to the invidious api
* Use a better algorithm for showing duration and consolidation of transcript chunks
* Add a way to show the transcripts in a different language
* Video Image alt text
* User testing with screen readers
* Responsive design

## Created By
* [Tristan Havelick](https:/tristanhavelick.com) - programming
* [@twizzay-code](https://github.com/twizzay-code) - idea
