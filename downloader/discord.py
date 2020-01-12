import logging

from downloader import download

logger = logging.getLogger('discord')
url_patterns = ['cdn.discordapp.com', 'media.discordapp.net']


def _get_fname(link):
    try:
        url_split = link.split("/")
        fname = url_split[-1]
        uid = url_split[-2]
        cid = url_split[-3]
        return cid + "_" + uid + "_" + fname
    except:
        return None


def get_link(link):
    download.download(link, fname=_get_fname(link))


# Get all links to Discord on this page and try to download them.
def get_soup(soup):
    logger.debug('Getting discord links..')
    links = []
    for link in soup.findAll('a'):
        this_link = link.get('href') or link.get('src')
        if any(pattern in str(this_link).lower() for pattern in url_patterns):
            links.append(this_link)
    links = list(dict.fromkeys(links))  # remove duplicates
    logger.debug('Found discord links: ' + str(links))
    for link in links:
        get_link(link)
