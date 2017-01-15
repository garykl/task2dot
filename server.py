#!/usr/bin/env python3
import os
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



def generate_net(kind, label):

    command = None

    if kind == 'tags':
        command = 'task +' + label + ' status:pending export |'
        command += ' python3 t2n.py -todo -' + label
        command += ' | dot -Tsvg > test_raw.svg'

    if kind == 'project':
        command = 'task project:' + label + ' status:pending export |'
        command += ' python3 t2n.py -todo -' + label
        command += ' | dot -Tsvg > test_raw.svg'

    if command is not None:
        os.system(command)


def app(environ, start_response):

    path = environ.get('PATH_INFO', '')

    if environ["REQUEST_METHOD"] in ["GET"]:

        query = environ['QUERY_STRING']
        request = extract_data_from_query(query)
        generate_net(request['kind'], request['label'])

        start_response("200 OK", [
            ("content-type", "image/svg"),
            ("Access-Control-Allow-Origin", "*")])
        return [open('test_raw.svg', 'r').read().encode('utf-8')]

    else:
        start_response("200 OK", [("content-type", "text/html")])
        return []



if __name__ == '__main__':
    port = 8000
    httpd = make_server("", port, app)
    httpd.serve_forever()
