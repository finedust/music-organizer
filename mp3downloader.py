#! /usr/bin/env python3.7

###
# File: mp3downloader.py
#
# Author: Francesco Tosello
###


##
# TODO
#
# - ...
##



from argparse import ArgumentParser

from re import compile as compile_regex, match, escape, IGNORECASE

from os import remove, makedirs, listdir
from os.path import isdir, join as pjoin, isfile, expanduser, dirname
from shutil import rmtree

from urllib.request import Request, urlopen
from urllib.parse import quote
from urllib.error import URLError

from Crypto.Hash import SHA512

from pytube import YouTube
from ffmpy import FFmpeg as Converter
from mutagen.easyid3 import EasyID3


SONGS_REGEX = r"(?P<title>[\w\ \']+)\ \-\ (?P<artist>[\w\ ]+)" # this is the input format for the songs
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11" # do not change this user-agent
YOUTUBE_SEARCH_QUERY = "https://www.youtube.com/results?search_query={}" # search videos using this query
VIDEO_URL = "https://www.youtube.com/watch?v=" # videos first url part
VIDEO_ID_REGEX = r"data\-context\-item\-id\=\"(?P<id>\w+)\"" # search for videos ids
HASHES_FILEPATH = expanduser("~/Music/Downloaded/.hashes.lst")
TEMP_DIR = ".tmp" # temporary working directory
OUTPUT_FORMAT = "mp3"
SAVE_DIR = expanduser("~/Music/Downloaded/")


class Song:

	def __init__(self, title, artist = None, album = None):
		self.title = str(title).title() if title else title
		self.artist = str(artist).title() if artist else artist
		self.album = str(album).title() if album else album

	def __str__(self):
		string = ""
		if self.artist: string += self.artist + " - "
		string += self.title
		if self.album: string += ", " + self.album
		return string

	def _filepath(self, fold = True): # return the preferred filename
		string = ""
		if fold:
			if self.artist: string = pjoin(string, self.artist)
			if self.album: string = pjoin(string, self.album)
			string = pjoin(string, self.title)
		else:
			if self.artist: string += self.artist + " - "
			string += self.title
		return string


def load_from_file(filename):
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

def load_from_stdin():
	songs = list()
	line = 1
	while line:
		line = input("Provide a song in this format: title - artist. Or leave blank to continue.  ").strip()
		matched_desc = compile_regex(SONGS_REGEX).match(line)
		if matched_desc:
			songs.append( Song(*matched_desc.groups()) )
		elif line:
			print( f"The input is not well formatted." )

	return songs

def already_downloaded(vid):
	id_hash = SHA512.new( str(vid).encode() ).hexdigest().upper()
	if not isfile(args.hashes_file):
		print( f"Hashes file {args.hashes_file} not found." )
		return False
	hf = open(args.hashes_file, 'r')
	for hline in hf.readlines():
		if hline.strip() == id_hash: return True
	return False

def search_song_url(song):
	# Make the query using the provided information
	if song.artist:
		query = f"{song.artist} - {song.title}"
	elif song.album:
		query = f"{song.title} - {song.album}"
	else:
		query = f"{song.title}"

	print( f"Searching for: {query}" )
	req = Request(YOUTUBE_SEARCH_QUERY.format( quote(query) ), None, {'User-Agent': USER_AGENT})
	try:
		content = str( urlopen(req).read() )
	except URLError:
		print("Connection error, quitting.")
		exit(-3)
	
	for video_match in compile_regex(VIDEO_ID_REGEX).finditer(content): # find video links
		if video_match:
			video_id = video_match.group('id')
			if already_downloaded(video_id):
				print( f"Video with id {video_id} already downloaded." )
				if args.download_another:
					print( "Searching for another link." )
					continue
				else: return None
			link = VIDEO_URL + video_id
			print( f"Found video match at {link}" )
			return link
	print( "No video ids found, skipping.")
	return None

def download_song(url, song):
	if not url: return False

	yt = YouTube(url)

	if not compile_regex( escape(song.title), IGNORECASE ).search( yt.title ) and not args.auto:
		if input( f"Are you sure you want to download this song: {yt.title} ({url})? " ).lower() not in ['s', 'si', 'y', 'yes']:
			print("Download canceled.")
			return None

	if not isdir(TEMP_DIR): makedirs(TEMP_DIR) # create a temporary directory
	streams = yt.streams.filter( only_audio = True ).all() + yt.streams.filter( progressive = True ).all() # select both only audio and mixed streams
	if not len(streams):
		print( f"No stream found for song: {song}" )
		return None
	else:
		print( "Found {} streams associated with this url: {}".format(len(streams), url) )
	streams[0].download( TEMP_DIR ) # download the first

	if not isdir(SAVE_DIR): makedirs(SAVE_DIR)
	filepath = pjoin(SAVE_DIR, "{}.{}".format( song._filepath(args.fold), OUTPUT_FORMAT ))
	if isfile(filepath):
		if args.overwrite:
			print( f"Overwriting {filepath}." )
			remove(filepath)
		else:
			print( f"{filepath} already existing, skipping." )
			return None
	if not isdir( dirname(filepath) ): makedirs( dirname(filepath) )
	Converter(
		global_options = '-loglevel quiet', # suppress output
		inputs = {pjoin(TEMP_DIR, f"{streams[0].default_filename}") : None},
		outputs = {filepath : None}
	).run()

	# Add the hash to the downloaded files hash list
	vid = url.split(VIDEO_URL)[1]
	id_hash = SHA512.new( str(vid).encode() ).hexdigest().upper()
	f = open(args.hashes_file, 'a')
	f.write( f"{id_hash}\n" )
	f.close()

	return filepath

def edit_tags(filepath, song):
	audio_file = EasyID3(filepath)
	audio_file["title"] = song.title
	audio_file["artist"] = song.artist
	if song.album: audio_file["album"] = song.album
	audio_file.save()


# Argument parsing
parser = ArgumentParser(description = "Download songs from YouTube")
parser.add_argument('-f', '--from-file', metavar = 'FILENAME', dest = 'file', help = "Load a list of songs from a file")
parser.add_argument('--hashes-file', default = HASHES_FILEPATH, help = "Custom path for the file that contains the video hashes")
parser.add_argument('-da', '--download-another', action = 'store_true', help = "Download another version is a video has already been downloaded")
parser.add_argument('-oe', '--overwrite', '--overwrite-existing', action = 'store_true', help = "Overwrite existing files")
parser.add_argument('-nf', '--do-not-fold', dest = 'fold', action = 'store_false', help = "Create artist and album directories")
parser.add_argument('--auto', action = 'store_true', help = "Do not prompt anything, go straight.")
args = parser.parse_args()
if args.download_another: args.overwrite = True

# Program start
print("Script loaded correctly, started.")
try:

	songs = list()
	if args.file: songs = load_from_file(args.file)
	if not songs and not args.auto: songs = load_from_stdin()
	num_songs = len(songs)
	if num_songs:
		print( "{} songs loaded successfully.".format(num_songs) )
	else:
		print( "No songs provided, quitting." )
		exit(-2)

	for index,s in enumerate(songs):
		print( f"Processing song {index+1} of {num_songs}: {s}" )
		outputfile = download_song( search_song_url(s), s )
		if outputfile:
			print( f"Downloaded: {s} to {outputfile}" )
		edit_tags(outputfile, s)
	print( f"Done. Downloaded {num_songs}" )

except KeyboardInterrupt:
	print("\nInterrupted, exiting.")
finally:
	if isdir(TEMP_DIR): rmtree(TEMP_DIR)
	if not listdir(SAVE_DIR): remove(SAVE_DIR)
	print("All cleaned.")