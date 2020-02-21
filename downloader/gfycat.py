import logging
import requests
from bs4 import BeautifulSoup

from downloader import download

logger = logging.getLogger(__file__)
url_patterns = ['gfycat.com', 'redgifs.com']


def _dl_redgifs(link):
    logger.debug("Downloading from redgifs.")
    response = requests.get(link)
    soup = BeautifulSoup(response.content, "html.parser")
    _get_redgifs_soup(soup)


def _get_redgifs_soup(soup):
    links = []
    for video in soup.findAll('source'):
        this_link = video.get('src')
        if any(pattern in str(this_link).lower() for pattern in url_patterns):
            links.append(this_link)
    links = list(dict.fromkeys(links))
    logger.debug('Found ' + __file__ + ' links: ' + str(links))
    for link in links:
        get_link(link)


def get_link(link):
    logger.debug('Getting ' + __file__ + ' link..')
    if "redgifs.com" in link:
        _dl_redgifs(link)
    else:
        download.download(link)


# Get all links on this page and try to download them.
def get_soup(soup):
    links = []
    for link in soup.findAll('a'):
        this_link = link.get('href')
        if any(pattern in str(this_link).lower() for pattern in url_patterns):
            links.append(this_link)
    links = list(dict.fromkeys(links))
    logger.debug('Found ' + __file__ + ' links: ' + str(links))
    for link in links:
        get_link(link)
