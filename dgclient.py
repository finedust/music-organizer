#! /usr/bin/env python3.7

###
# File: dgclient.py
#
# Author: Francesco Tosello
###



import discogs_client as dgc
from utils import Song

from re import sub as substitute, search


APP_VERSION = 'Discogs Client/0.1'
TOKEN_FILE = "discogs_token.psw"

SANTIZE_TITLE_REGEX = r"(?:\s*[\(\[][^\(\[]*?[\)\]]\ *)"


def load_token():
	try:
		f = open(TOKEN_FILE, 'r')
		global TOKEN
		TOKEN = f.read().strip()
		f.close()
	except Exception:
		exit(-3)
	if not TOKEN: exit(-3)

def get_artist_releases(name, include_singles = False):
	"""
	Get the relases by an artist.
	The result is returned as a dictionary formatted like this: {title: release} where title is a string and release a Release object
	"""
	artist = DG_CLIENT.search(name, type = 'artist')[0]
	if artist.name.lower() != name.lower(): pass # print warning
	main_releases = {}
	try:
		for release in artist.releases:
			if release.title.strip().lower() in main_releases: continue # skip if already existing
			mainrel = None
			if type(release) == dgc.models.Master:
				mainrel = release.main_release # get master's main release
			elif type(release) == dgc.models.Release:
				mainrel = release
				# Get the master release (too much time expensive)
				# master = release.master
				# if master:
				# 	mainrel = master.main_release # if master exists get the main release
				# elif not include_singles: # skip singles
				# 	continue
				# if not mainrel: mainrel = release # otherwise pick this release
			if mainrel:
				if artist in mainrel.artists: 
					main_releases[mainrel.title] = mainrel
	except KeyboardInterrupt:
		print("\nKeyboard Interrupt caught, returning fetched results")
	return main_releases

def get_album_releases(name, artist = None):
	"""
	Get the releases associated with the provided name, filtered by artist if requested
	The return value is a list with the Release objects inside
	"""
	releases = DG_CLIENT.search(name, type = 'release')
	fetch_num = min(10, len(releases))
	if artist:
		artist = artist.strip().lower()
		for num in range(0, fetch_num):
			if artist == releases[num].artists[0].name.lower(): return [ releases[num] ]
		return None
	else:
		rels = []
		for num in range(0, fetch_num):
			rels.append( releases[num] )
		return releases

def get_songs(releases):
	"""
	Returns the songs contained in each release. The return value is a dictionary with this formatting:
		{release_name : {song1_name : song1, song2_name : song2}, release2_name : ...}
		where the names are strings and the songs are Song objects
	If only one release is provided the return value is a single dictionary containing the songs
	"""
	rels = {}

	# force a list object
	try:
		releases = list(releases)
	except TypeError:
		releases = [releases]

	for rel in releases:
		rel_tracks = {}
		for track in rel.tracklist:
			name = track.title
			while search(SANTIZE_TITLE_REGEX, name): # santize name
				name = substitute(SANTIZE_TITLE_REGEX, "", name)
			name = name.strip().title()
			if name and name not in rel_tracks:
				rel_tracks[name] = Song(name, artist = rel.artists[0].name.strip().title(), album = rel.title.strip().title())
		rels[rel.title.strip().title()] = rel_tracks

	if len(rels) == 1: return next( iter ( rels.values() ) )
	return rels



# Authentication and client connection
load_token()
DG_CLIENT = dgc.Client(APP_VERSION, user_token = TOKEN)


# Main body
if __name__ == '__main__':
	print(APP_VERSION)