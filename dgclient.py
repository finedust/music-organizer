#! /usr/bin/env python3.7

###
# File: dgclient.py
#
# Author: Francesco Tosello
###



import discogs_client as dgc

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
	artist = DG_CLIENT.search(name, type = 'artist')[0]
	if artist.name.lower() != name.lower(): pass # print warning
	main_releases = list()
	for release in artist.releases:
		existing_releases = [mrel.title.lower().strip() for mrel in main_releases]
		if release.title.lower().strip() in existing_releases: continue # skip if already existing
		mainrel = None
		if type(release) == dgc.models.Master:
			mainrel = release.main_release # get master's main release
		elif type(release) == dgc.models.Release:
			master = release.master
			if master:
				mainrel = master.main_release # if master exists get the main release
			elif not include_singles: # skip singles
				continue
			if not mainrel: mainrel = release # otherwise pick this release
		if mainrel:
			if artist in mainrel.artists: 
				main_releases.append(mainrel)
	return main_releases

def get_album_release(name, artist = None):
	pass

def get_songs(releases):
	tracks = list()
	if type(releases) != list: releases = [releases] # force a list object
	for rel in releases:
		for track in rel.tracklist:
			name = track.title
			while search(SANTIZE_TITLE_REGEX, name): # santize name
				name = substitute(SANTIZE_TITLE_REGEX, "", name)
			name = name.title().strip() 
			if name and name not in tracks: tracks.append(name)
	return tracks



# Authentication and client connection
load_token()
DG_CLIENT = dgc.Client(APP_VERSION, user_token = TOKEN)


# Main body
if __name__ == '__main__':
	print(APP_VERSION)