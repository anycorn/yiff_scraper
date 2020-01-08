import logging

import os
import subprocess
import binascii
import re

from downloader import download, url_patterns

logger = logging.getLogger('mega')


def _get_rng_str(length=16):
    return binascii.b2a_hex(os.urandom(length)).decode("utf-8")


def _clean_ansi_characters(string, regex=r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])'):
    ansi_escape = re.compile(regex)
    return ansi_escape.sub('', string)


def _get_megadl_files(path, link):
    raw_output = subprocess.run(
        args=download.get_os_cmd(['megadl', "--print-names", "--path", path.replace("\\", "/"), link]),
        check=True,
        stdout=subprocess.PIPE).stdout
    contents = []
    for line in raw_output.splitlines():
        contents.append(_clean_ansi_characters(line.decode("utf8")))
    for i, content in enumerate(contents):
        if content.startswith("Downloaded "):
            logger.debug("Got MEGA files: " + str(contents[i+1:]))
            return contents[i+1:]
    return False


def get_link(link):
    link = link.replace('http://https://', 'https://', 1)
    if link.startswith("!#"):
        link = "https://mega.nz/" + link
    try:
        megadl_dir = "."
        while os.path.isdir(megadl_dir):
            megadl_dir = os.path.join(".", "megadl", _get_rng_str())
        os.makedirs(megadl_dir)
        for output_file in _get_megadl_files(megadl_dir, link):
            new_output_file = download.rotate_name(output_file)
            os.rename(os.path.join(".", megadl_dir, output_file), new_output_file)
            download.unpack(new_output_file, remove_file=True)
    except Exception as e:
        logger.error(e)
        download.log_failed_download(link)


def _clean_link(link):
    link = link.replace('http://https://', 'https://', 1)
    if link.startswith("#!"):
        link = "https://mega.nz/" + link
    return link


# Get all links to MEGA and save them to a file.
def get_soup(soup):
    logger.debug('Getting MEGA links..')
    links = []
    for element in soup.strings:
        if any(pattern in str(element).lower() for pattern in url_patterns.mega):
            links.append(_clean_link(element))
    for link in soup.findAll('a'):
        this_link = link.get('href')
        if any(pattern in str(this_link).lower() for pattern in url_patterns.mega):
            links.append(_clean_link(this_link))
    links = list(dict.fromkeys(links))  # remove duplicates
    logger.debug('Found MEGA links: ' + str(links))
    for link in links:
        get_link(link)
