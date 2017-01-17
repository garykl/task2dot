#!/usr/bin/env python3
import os
import urllib.parse
from wsgiref.simple_server import make_server


def split_query(query):
    '''
    query: a string
    return: a tuple of two strings
    '''
    return query.split("=")


def extract_data_from_query(query):
    """
    query: a string.
    return: a dictionary.
    """
    result = {}
    if query is '':
        return result

    list_of_queries = query.split('&')
    for q in list_of_queries:
        splitted = q.split('=')
        result[splitted[0]] = splitted[1]

    return result



def generate_net(query):
    command = urllib.parse.unquote(query)
    command += ' | dot -Tsvg | '
    command += 'sed -E \'s/<svg width="[0-9]+pt" height="[0-9]+pt"/'
    command += '<svg width="500" height="500"/\' > test_raw.svg'
    os.system(command)


def app(environ, start_response):

    path = environ.get('PATH_INFO', '')

    if environ["REQUEST_METHOD"] in ["GET"]:

        query = environ['QUERY_STRING']
        request = extract_data_from_query(query)
        generate_net(request['query'])

        start_response("200 OK", [
            ("content-type", "image/svg"),
            ("Access-Control-Allow-Origin", "*")])
        return [open('test_raw.svg', 'r').read().encode('utf-8')]

    else:
        start_response("200 OK", [("content-type", "text/html")])
        return []



if __name__ == '__main__':

    import subprocess
    tags = subprocess.check_output(
        ['task', '_tags']).decode('utf-8').split('\n')[:-1]
    projects = subprocess.check_output(
        ['task', '_projects']).decode('utf-8').split('\n')[:-1]
    with open('config.js', 'w') as js_handle:
        js_handle.write('var tags = ')
        js_handle.write(repr(tags))
        js_handle.write(';')
        js_handle.write('\n')
        js_handle.write('var projects = ')
        js_handle.write(repr(projects))
        js_handle.write(';')

    port = 8000
    httpd = make_server("", port, app)
    httpd.serve_forever()
