# youTranscript

[![](https://tokei.rs/b1/github/thavelick/youtranscript)](https://tokei.rs/b1/github/thavelick/youtranscript)
[![Maintainability](https://api.codeclimate.com/v1/badges/e14cb3a0b59f1db8f3f5/maintainability)](https://codeclimate.com/github/thavelick/youtranscript/maintainability)


A frontend for youtube that shows transcripts instead of videos.

## Installation and Usage

1. Clone
  ```
  git clone https://github.com/thavelick/youtranscript && cd youtranscript
  ```
2. Start the server
  ```bash
  # Make sure to use a real invidious host here
  YOUTRANSCRIPT_INVIDIOUS_HOST=your-favorite.invidious.host ./youtranscript.py
  ```
3. Open your browser to http://localhost:8008/

### Environment variables

* `YOUTRANSCRIPT_INVIDIOUS_HOST`: optional -  the hostname of the invidious instance
to use to pull youtube transcripts and search results. For a list of available
instances check: https://api.invidious.io/. Make sure you pick one with a
checkmark for API. If not set a random server listed at https://api.invidious.io/
will be used

## Urls

The urls should mostly correspond to youtube.com ones, so you can replace https://youtube.com with
http://localhost:8008/ and it will work.

## Dependencies
* Python 3.10

# TODO
* Add accessibility features
* Add punctuation restoration to auto-generated transcripts
* Add some copy to the homepage about how cool this is
* Public hosting
* Add a way to show the transcripts in a different language
* Responsive design
* Add channel page
* Add RSS feeds
* More info on search results page
* Rename the search results page to match youtube:
  * Use `search_query` instead of `search_term`
  * Rename to `/results`
* Highlight current cue in transcript during audio playback, Also:
  * Pause the audio when the user clicks on the currently playing cue
  * Play the audio when the user clicks on a cue
  * Scroll the page to the currently playing cue as the audio plays
* search result paging
* optimize for text based-browsers and screen readers
  * don't use the `<details>` tag even though it's awesome
  * move the Description to the bottom of the page so the transcript is more
    prominent (maybe add a link to the description towards the top)
  * don't rely on css to hide javascript-only elements. This doesn't work in all
    browsers
  * add alt text to search result thumbnails, even if it's just "thumbnail for
    {video_title}"

## Created By
* [Tristan Havelick](https:/tristanhavelick.com) - programming
* [@twizzay-code](https://github.com/twizzay-code) - idea
