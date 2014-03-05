#!/usr/bin/python

import logging

import tempfile
from errno import ENOENT
from stat import S_IFDIR, S_IFLNK, S_IFREG
from sys import argv, exit
from time import time
from urllib import parse
import requests
from fuse import FUSE, FuseOSError, Operations, LoggingMixIn
from stashapi import client

if not hasattr(__builtins__, 'bytes'):
    bytes = str

class StashFS(LoggingMixIn, Operations):
    'Example memory filesystem. Supports only one level of files.'

    def __init__(self, stashapi):
        self.api = stashapi
        self.files = []
        self.enumerate_files()

    def enumerate_files(self):
        all_files_folders = api.list()
        self.files = list(filter(lambda a: not a.is_folder, all_files_folders))

    def getattr(self, path, fh=None):
        now = time()
        if path == '/':
            return dict(st_mode=(S_IFDIR | 0o755), st_ctime=now,
                    st_mtime=now, st_atime=now, st_nlink=2)
        else:
            return dict(st_mode=(S_IFREG | 0o755), st_size=4, st_ctime=now,
                    st_mtime=now, st_atime=now)

    def read(self, path, size, offset, fh):
        print(path)
        return b'test'

    def readdir(self, path, fh):
        return ['.', '..'] + [x.title for x in self.files]

    access = None
    flush = None
    getxattr = None
    listxattr = None
    open = None
    opendir = None
    release = None
    releasedir = None
    statfs = None

if __name__ == '__main__':
    if len(argv) != 4:
        print('usage: %s <mountpoint> <auth_code> <redirect_uri>' % argv[0])
        exit(1)

    client_id = '977'
    client_secret = '1eb3b5a5b401ac680d5b59ba972d56b2'
    api = client.StashAPI(client_id=client_id, client_secret=client_secret, redirect_uri=argv[3])
    token = api.exchange_code_for_access_token(argv[2])
    api = client.StashAPI(access_token=token, client_id=client_id, client_secret=client_secret, redirect_uri=argv[3])

    logging.getLogger().setLevel(logging.DEBUG)
    fuse = FUSE(StashFS(api), argv[1], foreground=True)
