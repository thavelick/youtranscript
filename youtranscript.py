#!/usr/bin/python3
import http.server
import socketserver
from youtube_transcript_api import YouTubeTranscriptApi
from fastpunct import FastPunct
from youtubesearchpython import VideosSearch

def get_youtube_search_results(search_term: str) -> list[dict]:
    """
    Returns a list of youtube search results.
    Args:
        search_term: The search term to search for.
    Retuns:
        youtube search results as a list of dictionaries.
    """
    videos_search = VideosSearch(search_term, limit=10)
    results = videos_search.result()
    return results.get('result', [])

def get_video_link(youtube_id):
    """
    Gets a link to the transcript page for the video.
    Args:
        youtube_id: The youtube id of the video. For example: 'bXq4oQ-fXpE'
    Returns:
        A relative link to the transcript page for the video.
    """
    return '/transcript?v={}'.format(youtube_id)

def get_table_with_search_results(results):
    """
    Returns a html table with the search results.
    Args:
        results: A list of youtube search results.
    Returns:
        A html table with the search results.
    """
    table_row_template = '<tr><td><img src="{thumbnail_url}"></td><td><a href="{link}">{title}</a></td></tr>'
    table_parts = ['<table>']
    for video in results:
        youtube_id = video['id']
        link = get_video_link(youtube_id)
        title = video['title']
        thumbnaiil_url = video['thumbnails'][0]['url']
        table_parts.append(table_row_template.format(
            link=link,
            title=title,
            thumbnail_url=thumbnaiil_url,
        ))
    table_parts.append('</table>')

    return ''.join(table_parts)

def get_transcript(youtube_id: str) -> list:
    """
    Pulls the transcript for a video from YouTube.
    Args:
        youtube_id: The youtube id of the video. For example: 'bXq4oQ-fXpE'
    Returns:
        A list of dictionaries with the start and text of each line.
    """

    transcript = YouTubeTranscriptApi.get_transcript(youtube_id)
    return transcript

def add_punctuation_to_transcript(transcript: list) -> list:
    """
    Adds punctuation to the transcript.
    Args:
        transcript: The transcript to add punctuation as a list of 
            dictionaries with the start and text of each line.
    Returns:
        The transcript with punctuation added.
    """
    punct = FastPunct()
    for i in range(len(transcript)):
        transcript[i]['text'] = punct.add_punctuation(transcript[i]['text'])
    return transcript 

def get_table_with_transcript(youtube_id: str, add_punctuation: bool = False) -> str:
    """
    Returns a html table with the transcript of the video.
    Args:
        youtube_id: The youtube id of the video. For example: 'bXq4oQ-fXpE'
        add_punctuation: If True, adds punctuation to the transcript.
    Returns:
        A html table with the transcript of the video.
    """
 
    table_row_template = '<tr><td>{start}</td><td>{text}</td></tr>'
    table_parts = ['<table>']
    transcript = get_transcript(youtube_id)
    if add_punctuation:
        transcript = add_punctuation_to_transcript(transcript)
    
    last_start = ''
    for line in transcript:
        start = human_readable_time_length(line['start'])
        # Don't repeat the times
        if start == last_start:
            start_cell = '&nbsp;'
        else:
            last_start = start
            start_cell = '<a href="https://www.youtube.com/watch?v={}&t={}">{}</a>'.format(
                youtube_id, 
                int(line['start']), 
                start
            )
      
        table_parts.append(table_row_template.format(
            start=start_cell,
            text=line['text']
        ))

    table_parts.append('</table>')

    return ''.join(table_parts)

def human_readable_time_length(seconds: int) -> str:
    """
    Converts seconds to a human readable time length.
    Args:
        seconds: The number of seconds to convert.
    Returns:
        A human readable time length.
    """

    if seconds < 60: 
        unit = 'second'
        # round to 15 second intervals
        amount = int(seconds / 15) * 15
    elif seconds < 3600:
        unit = 'minute'
        amount = int(seconds / 60)
    else:
        unit = 'hour'
        amount = int(seconds / (60 * 60))
    
    if int(amount) != 1:
        unit += 's'
    
    return '{} {}'.format(int(amount), unit)


class YouTranscriptHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        "Route GET requests."
        path = self.get_path_without_query_string()
        routes = {
            '/': self.do_homepage,
            '/search': self.do_search_results_page,
            '/transcript': self.do_transcript_page,
            '/watch': self.do_watch_page,
        }

        if path not in routes:
            self.do_html_page_response(
                title='Not found',
                content='<h1>Not found</h1>',
                status_code=404
            )
            return

        routes[path]()

    def get_path_without_query_string(self) -> str:
        "Returns the path without the query string."
        path = self.path
        if '?' in path:
            path = path[:path.index('?')]
        return path

    def get_query_string_if_exists(self) -> str|None:
        """Returns the query string if it exists.
        Returns:
            The query string if it exists, None otherwise.
        """

        if '?' in self.path:
            return self.path[self.path.index('?') + 1:]
        return None

    def get_query_param(self, param_name) -> str:
        """
        Returns the value of a query param.
        Args:
            param_name: The name of the query param.
        Returns:
            The value of the query param or an empty string.
        """
        query_string = self.get_query_string_if_exists()
        if not query_string:
            return ''
        params = query_string.split('&')
        for param in params:
            if param.startswith(param_name):
                return param[param.index('=') + 1:]
        return ''

    def do_permanent_redirect_response(self, location: str) -> None:
        """
        Sends a permanent redirect response.
        Args:
            location: The url to redirect to.
        """
        self.send_response(301)
        self.send_header('Location', location)
        self.end_headers()

    def do_html_response(self, html: str, status_code: int =200):
        """
        Sends an html response.
        Args:
            html: The html to send.
            status_code: The status code to send.
        """
        self.send_response(status_code)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(bytes(html, 'utf-8'))
        self.send_response(status_code)
        self.send_header('Content-type', 'text/html; charset=utf-8') 
        self.send_header('Content-length', str(len(html)))
        self.end_headers()
        self.wfile.write(html.encode())

    def do_html_page_response(self, title: str, content: str, status_code: int=200, css:str|None=None) -> None:
        """
        Sends an html page response.
        Args:
            title: The title of the page.
            content: The content of the page.
            status_code: The status code to send.
            css: The css to include in the page.

        """
        style_tag = ''
        if css:
            style_tag = '<style>{}</style>'.format(css)

        html = '''
        <!DOCTYPE html>
        <html>
            <head>
                <title>{title}</title>
                {style_tag}
            </head>
            <body>
                {content}
            </body>
        </html>
        '''.format(title=title, content=content, style_tag=style_tag)
        self.do_html_response(html, status_code)

    def do_homepage(self) -> None:
        """
        Handles the homepage.
        
        Shows a simple search form.
        """
        css_for_search_form = self.get_css_for_search_form()
        self.do_html_page_response(
            title='Homepage',
            content='''
            <form action="/search" method="get">
                <input type="text" name="search_term">
                <input type="submit" value="Search">
            </form>
            ''',
            css=css_for_search_form
        )

    def get_css_for_search_form(self) -> str:
        """
        Returns the css for the search form.
        """
        return '''
        body {
            font-family: sans-serif;
        }

        form {
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        input {
            margin: 10px;
        }

        input[type="text"] {
            width: 300px;
        }

        input[type="submit"] {
            width: 100px;
            height: 30px;
            font-size: 18px;
        }
        '''

    def do_search_results_page(self) -> None:
        """
        Handles the search results page.

        Shows a list of search results.
        """
        search_term = self.get_query_param('search_term')
        results = get_youtube_search_results(search_term)
        table = get_table_with_search_results(results)
        self.do_html_page_response(
            title='Search results for "{}"'.format(search_term),
            content=table
        )

    def do_transcript_page(self) -> None:
        """
        Handles the transcript page.

        Shows a transcript for a youtube video.
        """
        youtube_id = self.get_query_param('v')
        table = get_table_with_transcript(youtube_id)
        self.do_html_page_response(
            title='Transcript for "{}"'.format(youtube_id),
            content=table
        )

    def do_watch_page(self) -> None:
        "redirect to the transcript page."
        youtube_id = self.get_query_param('v')
        self.do_permanent_redirect_response('/transcript?v={}'.format(youtube_id))


if __name__ == '__main__':   
    PORT = 8008
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), YouTranscriptHandler) as httpd:
        print("serving at port", PORT)
        httpd.serve_forever()
