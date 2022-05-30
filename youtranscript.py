#!/usr/bin/python3
"""website that displays the transcripts of a youtube videos."""
import http.server
import json
import os
import socketserver
import sys
from functools import cache
from urllib.error import URLError
from urllib.request import Request, urlopen

from get_transcript import get_transcript


INVIDIOUS_HOST = os.environ.get('YOUTRANSCRIPT_INVIDIOUS_HOST')
INVIDIOUS_API_URL = f'https://{INVIDIOUS_HOST}/api/v1'


@cache
def get_template(name: str) -> str:
    """Return the a given html template."""
    print('loading template:', name)
    with open(f'templates/{name}.html', encoding='utf-8') as template_file:
        template = template_file.read()
    return template


def fill_template(name: str, **kwargs) -> str:
    """
    Return a html template with the given values.

    Args:
        name: The name of the template.
        **kwargs: The values to fill the template with.
    Returns:
        A html template with the given values.
    """
    template = get_template(name)
    return template.format(**kwargs)


def get_youtube_search_results(search_term: str) -> list[dict]:
    """Return a list of youtube search results."""
    request = Request(
        f"{INVIDIOUS_API_URL}/search?q={search_term}&type=video"
    )

    with urlopen(request) as response:
        results = json.loads(response.read())
    return results


def get_table_with_search_results(results: list[dict]) -> str:
    """
    Return a html table with the search results.

    Args:
        results: A list of youtube search results.
    Returns:
        A html table with the search results.
    """
    table_parts = ['<table>']
    for video in results:
        youtube_id = video['videoId']
        link = f'/transcript?v={youtube_id}'
        title = video['title']
        thumbnail_url = get_matching_dictionary_from_list(
            video['videoThumbnails'], 'quality', 'medium'
        ).get('url')

        table_parts.append(fill_template(
            'search_result',
            link=link,
            title=title,
            thumbnail_url=thumbnail_url,
        ))
    table_parts.append('</table>')

    return ''.join(table_parts)


def get_matching_dictionary_from_list(
        list_of_dicts: list[dict],
        key: str,
        value: str) -> dict:
    """
    Return the element in a list of dictionaries that matches a key and value.

    Args:
        list_of_dicts: A list of dictionaries.
        key: The key to search for.
        value: The value to search for.
    Returns:
        The first element in a list of dictionaries that matches a key and
        value or {} if no match is found.
    """
    for element in list_of_dicts:
        if element[key] == value:
            return element
    return {}


def get_table_with_transcript(youtube_id: str) -> str:
    """
    Return a html table with the transcript of the video.

    Args:
        youtube_id: The youtube id of the video. For example: 'bXq4oQ-fXpE'
        add_punctuation: If True, adds punctuation to the transcript.
    Returns:
        A html table with the transcript of the video.
    """
    table_parts = ['<table>']
    transcript = get_transcript(youtube_id)

    for cue in transcript:
        table_parts.append(fill_template(
            'cue',
            start=cue.youtube_link_tag(youtube_id),
            text=cue.html_text()
        ))

    table_parts.append('</table>')

    return ''.join(table_parts)


class YouTranscriptHandler(http.server.BaseHTTPRequestHandler):
    """Serve website that shows youtube transcripts."""

    # pylint: disable=invalid-name
    def do_GET(self):
        """Route GET requests."""
        path = self.get_path_without_query_string()
        routes = {
            '/': self.render_homepage,
            '/search': self.render_search_results_page,
            '/style.css': lambda: self.render_file('style.css', 'text/css'),
            '/transcript': self.render_transcript_page,
            '/watch': self.render_watch_page,
        }

        if path not in routes:
            self.render_html_page_response(
                title='Not found',
                content='<h1>Not found</h1>',
                status_code=404
            )
            return

        routes[path]()

    def get_path_without_query_string(self) -> str:
        """Return the path without the query string."""
        path = self.path
        if '?' in path:
            path = path[:path.index('?')]
        return path

    def get_query_string_if_exists(self) -> str | None:
        """Return the query string if it exists."""
        if '?' in self.path:
            return self.path[self.path.index('?') + 1:]
        return None

    def get_query_param(self, param_name) -> str:
        """Return the value of a query param."""
        query_string = self.get_query_string_if_exists()
        if not query_string:
            return ''
        params = query_string.split('&')
        for param in params:
            if param.startswith(param_name):
                return param[param.index('=') + 1:]
        return ''

    def render_text(
                self,
                text: str,
                content_type: str = 'text/plain',
                status_code: int = 200,
            ) -> None:
        """Send an http response with the given text."""
        self.start_response(
            status_code, {
                'Content-type': content_type,
                'Content-length': str(len(text)),
            }
        )
        self.wfile.write(text.encode('utf-8'))

    def render_redirect(self, location: str) -> None:
        """Send a redirect response."""
        self.start_response(302, {'Location': location})

    def render_file(self, file_path: str, content_type) -> None:
        """Send a file response."""
        with open(file_path, 'rb') as file:
            self.start_response(200, {'Content-type': content_type})
            self.wfile.write(file.read())

    def start_response(self, status_code: int, headers: dict) -> None:
        """Send status code and headers for the response."""
        self.send_response(status_code)
        for k, v in headers.items():
            self.send_header(k, v)
        self.end_headers()

    def render_html_page_response(
        self,
        title: str,
        content: str,
        status_code: int = 200,
    ) -> None:
        """
        Send an html page response.

        Args:
            title: The title of the page.
            content: The content of the page.
            status_code: The status code to send.
        """
        html = fill_template('layout', content=content, title=title)
        self.render_text(html, 'text/html; charset=utf-8', status_code)

    def render_homepage(self) -> None:
        """
        Handle the homepage.

        Shows a simple search form.
        """
        self.render_html_page_response(
            title='youTranscript',
            content=fill_template(
                'homepage',
                search_box=get_template('search_box'),
            )
        )

    def render_search_results_page(self) -> None:
        """
        Handle the search results page.

        Shows a list of search results.
        """
        search_term = self.get_query_param('search_term')

        if len(search_term or '') == 0:
            self.render_redirect('/')
            return

        try:
            results = get_youtube_search_results(search_term)
        except URLError:
            self.render_html_page_response(
                title='External Site Error',
                content="""
                <h1>External Site Error</h1>
                <p>
                    An error occurred when trying to fetch search results.
                    Please try again later.
                </p>
                """
            )
            return

        if len(results) == 0:
            content = '<p>No results found</p>'
        else:
            content = get_table_with_search_results(results)

        self.render_html_page_response(
            title=f'Search results for "{search_term}"',
            content=content
        )

    def render_transcript_page(self) -> None:
        """
        Handle the transcript page.

        Shows a transcript for a youtube video.
        """
        youtube_id = self.get_query_param('v')
        try:
            table = get_table_with_transcript(youtube_id)
        except ValueError:
            self.render_html_page_response(
                title='Transcript Not Found',
                content="<p>No transcript found.</p>",
                status_code=404,
            )
            return
        self.render_html_page_response(
            title=f'Transcript for "{youtube_id}"',
            content=table
        )

    def render_watch_page(self) -> None:
        """Redirect to the transcript page."""
        youtube_id = self.get_query_param('v')
        self.render_redirect(f'/transcript?v={youtube_id}')


if __name__ == '__main__':
    if not INVIDIOUS_HOST:
        print(
            'You must set the environment variable'
            ' YOUTRANSCRIPT_INVIDIOUS_HOST'
        )
        sys.exit(1)

    PORT = 8008
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), YouTranscriptHandler) as httpd:
        print("serving at port", PORT)
        httpd.serve_forever()
