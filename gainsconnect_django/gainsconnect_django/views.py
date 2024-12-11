from django.http import HttpResponse
from django.conf import settings
from urllib.parse import urlparse
import os

def parseURL(url: str) -> list:
    '''
    returns a the ID found in the url, assumes id is the last element in the path
    '''
    parsed_url = urlparse(url)
    paths = parsed_url.path.split('/')
    id = paths.pop()
    return id

def index(_):
    index_path = os.path.join(settings.BASE_DIR, 'static', 'index.html')
    with open(index_path, 'r') as f:
        return HttpResponse(f.read())