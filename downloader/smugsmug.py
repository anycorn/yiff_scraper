import logging

from downloader import download

logger = logging.getLogger(__file__)
url_patterns = ['photos.smugmug.com']


def get_link(link):
    logger.debug('Getting ' + __file__ + ' link..')
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
