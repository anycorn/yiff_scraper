import logging

from downloader import download

logger = logging.getLogger('catbox')
url_patterns = ['catbox.moe']


def get_link(link):
    download.download(link)


# Get all links on this page and try to download them.
def get_soup(soup):
    logger.debug('Getting ' + __file__ + ' links..')
    links = []
    for link in soup.findAll('a'):
        this_link = link.get('href')
        if any(pattern in str(this_link).lower() for pattern in url_patterns):
            links.append(this_link)
    links = list(dict.fromkeys(links))
    logger.debug('Found ' + __file__ + ' links: ' + str(links))
    for link in links:
        get_link(link)
