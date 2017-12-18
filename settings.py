#! /usr/bin/env python3.7



# Imports

from os.path import expanduser


# Settings

MUSIC_DOWNLOAD_DIRECTORY = expanduser("~/Music/Downloaded/")
DOWNLOADED_FILES_HASHES_FILEPATH = MUSIC_DOWNLOAD_DIRECTORY + ".hashes.lst"