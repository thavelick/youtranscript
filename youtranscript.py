#!/usr/bin/python3
import http.server
import socketserver
from youtube_transcript_api import YouTubeTranscriptApi
from fastpunct import FastPunct
from youtubesearchpython import VideosSearch

def get_youtube_search_results(search_term):
    videos_search = VideosSearch(search_term, limit=2)
    results = videos_search.result()
    return results.get('result', [])

def get_video_link(youtube_id):
    return '/transcript?v={}'.format(youtube_id)

def get_table_with_search_results(results):
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

def get_transcript(youtube_id):
    transcript = YouTubeTranscriptApi.get_transcript(youtube_id)
    return transcript

def add_punctuation_to_transcript(transcript):
    punct = FastPunct()
    for i in range(len(transcript)):
        transcript[i]['text'] = punct.add_punctuation(transcript[i]['text'])
    return transcript 

def get_table_with_transcript(youtube_id, add_punctuation=False):
    table_row_template = '<tr><td>{start}</td><td>{text}</td></tr>'
    table_parts = ['<table>']
    transcript = get_transcript(youtube_id)
    if add_punctuation:
        transcript = add_punctuation_to_transcript(transcript)
    for line in transcript:
        table_parts.append(table_row_template.format(
            start=line['start'],
            text=line['text']
        ))
    table_parts.append('</table>')

    return ''.join(table_parts)

class YouTranscriptHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        # safely seperate the path and query string: 
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

    def get_path_without_query_string(self):
        path = self.path
        if '?' in path:
            path = path[:path.index('?')]
        return path

    def get_query_string_if_exists(self):
        if '?' in self.path:
            return self.path[self.path.index('?') + 1:]
        return None

    def get_query_param(self, param_name):
        query_string = self.get_query_string_if_exists()
        if not query_string:
            return None
        params = query_string.split('&')
        for param in params:
            if param.startswith(param_name):
                return param[param.index('=') + 1:]
        return None

    def do_permanent_redirect_response(self, location):
        self.send_response(301)
        self.send_header('Location', location)
        self.end_headers()

    def do_html_response(self, html, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-type', 'text/html')
        self.send_header('Content-length', len(html))
        self.end_headers()
        self.wfile.write(html.encode())

    def do_html_page_response(self, title, content, status_code=200, css=None):
        style_tag = ''
        if css:
            style_tag = '<style>{}</style>'.format(css)

        html = '''
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

    def do_homepage(self):
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

    def get_css_for_search_form(self):
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

    def do_search_results_page(self):
        search_term = self.get_query_param('search_term')
        results = get_youtube_search_results(search_term)
        table = get_table_with_search_results(results)
        self.do_html_page_response(
            title='Search results for "{}"'.format(search_term),
            content=table
        )

    def do_transcript_page(self):
        youtube_id = self.get_query_param('v')
        table = get_table_with_transcript(youtube_id)
        self.do_html_page_response(
            title='Transcript for "{}"'.format(youtube_id),
            content=table
        )

    def do_watch_page(self):
        "redirect to the transcript page"
        youtube_id = self.get_query_param('v')
        self.do_permanent_redirect_response('/transcript?youtube_id={}'.format(youtube_id))


PORT = 8008
with socketserver.TCPServer(("", PORT), YouTranscriptHandler) as httpd:
    print("serving at port", PORT)
    httpd.serve_forever()
