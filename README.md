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
  ```
  ./youtranscript.py
  ```
3. Open your browser to http://localhost:8008/

## Urls

The urls should mostly correspond to youtube.com ones, so you can replace https://youtube.com with
http://localhost:8008/ and it will work.

## Dependencies
* Python 3.10
* youtube-search-python 1.6.5
* youtube_transcript_api 0.4.4

# TODO
* Use a template engine instead of hard-coding html
* Clean up the design
* Add accessibility features
* Add search to the results and transcript pages
* Add title and other metadata to the transcript pages
* Commission or make a cool logo
* Add punctuation restoration to auto-generated transcripts
* Add some copy to the homepage about how cool this is
* Public hosting
* Figure out scale
  * Maybe move to official youtube api?
  * Rate limiting?
  * User accounts? (looser rate limiting for signed in users)
* Use a better algorithm for showing duration and consolidation of transcript chunks
* Add a way to show the transcripts in a different language
* Video Image alt text
* User testing with screen readers
* Responsive design

## Created By

* [Tristan Havelick](https:/tristanhavelick.com) - programming
* An anonymous fediverse user - idea
