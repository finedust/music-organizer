#! /usr/bin/env python3.7



# Imports

from os.path import expanduser

from os.path import join as pjoin, isfile

from Crypto.Hash import SHA512

from re import compile as compile_regex


# Classes

class Song:

	def __init__(self, title, artist = None, album = None):
		if title:
			self.title = str(title).title()
		else: raise RuntimeError("You must specify a title for the song.")
		self.artist = str(artist).title() if artist else None
		self.album = str(album).title() if album else None

	def __str__(self):
		string = self.title
		if self.album: string += ", " + self.album
		if self.artist: string += " - " + self.artist
		return string

	def _filepath(self, fold = True): # return the preferred filename
		string = ""
		if fold:
			string = pjoin(string, self.artist if self.artist else "Unknown Artist")
			string = pjoin(string, self.album if self.album else "Unknown Album")
			string = pjoin(string, self.title)
		else:
			if self.artist: string += self.artist + " - "
			string += self.title
		return string + "." + OUTPUT_FORMAT


# Settings

MUSIC_DOWNLOAD_DIRECTORY = expanduser("~/Music/Downloaded/")
DOWNLOADED_VIDEOS_HASHES_FILEPATH = MUSIC_DOWNLOAD_DIRECTORY + ".hashes.lst"
IGNORE_VIDEOS_HASHES_FILEPATH = MUSIC_DOWNLOAD_DIRECTORY + ".ignore.lst"
OUTPUT_FORMAT = "mp3"

# Costants
VIDEO_URL = "https://www.youtube.com/watch?v=" # video's url first part

SONGS_REGEX = r"(?P<title>[\w\ \']+)\ \-\ (?P<artist>[\w\ \.\']+)" # this is the input format for the songs



# Functions


def add_hash(url, hashes_file):
	"""
	Add the hash to the downloaded files hash list
	"""
	vid = url.split(VIDEO_URL)[1]
	id_hash = SHA512.new( str(vid).encode() ).hexdigest().upper()
	f = open(hashes_file, 'a')
	f.write( f"{id_hash}\n" )
	f.close()

def match_hash(vid, hashes_file):
	"""
	Match the video id in the provided file
	"""
	id_hash = SHA512.new( str(vid).encode() ).hexdigest().upper()
	if not isfile(hashes_file):
		print( f"Hashes file {hashes_file} not found." )
		return False
	hf = open(hashes_file, 'r')
	for hline in hf.readlines():
		if hline.strip() == id_hash: return True
	return False

def load_songs_from_file(filename):
	"""
	Load a list of songs from a file
	"""
	sf = open(filename, 'r')
	lines = sf.readlines()
	sf.close()

	sgs = list()
	for s in lines:
		if not s.strip(): continue # skip empty lines
		matched_desc = compile_regex(SONGS_REGEX).match(s)
		if matched_desc:
			song = Song( *matched_desc.groups() )
			sgs.append(song)
		else:
			print( f"This line is not well formatted: {s}" )

	return sgs