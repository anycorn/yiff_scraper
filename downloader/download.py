import os

from send2trash import send2trash

import logging

import requests
import urllib
import re

from downloader import catbox, discord, dropbox, gfycat, googledrive, mega, onedrive, smugsmug, uploaddir, yandisk
from zipfile import ZipFile
import patoolib

logger = logging.getLogger('file_handling')


def get_os_cmd(cmd):
    if os.name == 'nt':
        process_cmd = ['wsl']
    else:
        process_cmd = []
    return process_cmd + cmd


def get_soups(soup):
    mega.get_soup(soup)
    catbox.get_soup(soup)
    discord.get_soup(soup)
    dropbox.get_soup(soup)
    gfycat.get_soup(soup)
    googledrive.get_soup(soup)
    onedrive.get_soup(soup)
    smugsmug.get_soup(soup)
    uploaddir.get_soup(soup)
    yandisk.get_soup(soup)


def _append_num(filename, num):
    fname, ext = os.path.splitext(filename)
    return fname + "_" + str(num) + ext


# Number the filename if it exists already.
def rotate_name(filename):
    n = 1
    fname = filename
    while os.path.exists(fname):
        fname = _append_num(filename, n)
        n += 1
    folder = os.path.dirname(os.path.join(".", filename))
    if not os.path.isdir(folder):
        os.makedirs(folder)
    return fname


# unzip/unrar files
def unpack(filename, remove_file=False):
    fname, ext = os.path.splitext(filename)
    ext = ext.lower()
    extract_dir = rotate_name(fname)
    extracted = False
    if ext == ".zip":
        try:
            with ZipFile(filename, 'r') as zf:
                zf.extractall(path=extract_dir)
                zf.close()
            extracted = True
        except Exception as e:
            logger.error(e)
    elif ext in [".rar", ".7z"]:  # requires to have 7zip installed
        try:
            if not os.path.isdir(extract_dir):
                os.makedirs(extract_dir)
            patoolib.extract_archive(filename, outdir=extract_dir)
            extracted = True
        except Exception as e:
            logger.error(e)
    if remove_file and extracted:
        # os.remove(filename)
        send2trash(filename)


def get_filename(response, fname=None):
    if not fname:
        try:
            fname = urllib.parse.unquote(
                re.findall("filename\\*=UTF-8''(.+)", response.headers['content-disposition'])[0]
            )
        except:
            fname = None
    if not fname:
        try:
            fname = re.findall("filename=(.+)", response.headers['content-disposition'])[0].replace('"', '')
        except:
            fname = None
    if not fname:
        try:
            fname = response.url.rsplit("/", 1)[1]
        except:
            fname = None
    if not fname:
        logger.warning("Could not get filename from html headers. Using fallback..")
        fname = "file.ext"
    fname = rotate_name(fname)
    logger.debug('Using filename ' + fname)
    return fname


# Download a file with automatic naming.
def download(url, fname=None):
    try:
        url = str(url).replace('http://https://', 'https://', 1)  # http://https:// sometimes seems to happen?
        url = str(url).replace('http://https//', 'https://', 1)  # http://https// sometimes seems to happen?
        response = requests.get(url, allow_redirects=True)
    except Exception as e:
        logger.error(e)
        log_failed_download(url)
        return False
    fname = get_filename(response, fname=fname)
    logger.info('Downloading ' + url + ' to ' + fname)
    with open(fname, 'wb') as f:
        f.write(response.content)
        f.close()
    unpack(filename=fname, remove_file=True)


def log_failed_download(link):
    if any(pattern in link for pattern in dropbox.url_patterns):
        filename = "dropbox.txt"
    elif any(pattern in link for pattern in googledrive.url_patterns):
        filename = "gdrive.txt"
    elif any(pattern in link for pattern in mega.url_patterns):
        filename = "mega.nz.txt"
    elif any(pattern in link for pattern in onedrive.url_patterns):
        filename = "onedrive.txt"
    elif any(pattern in link for pattern in yandisk.url_patterns):
        filename = "yadi.sk.txt"
    else:
        filename = "download.txt"
    logger.error('Failed to download ' + str(link) + '. Saving to link to ' + filename + ' instead')
    with open(filename, 'a+') as file:
        file.write(str(link) + '\n')
        file.close()
