#! /usr/bin/env python3.7

###
# File: organizer.py
#
# Author: Francesco Tosello
###


##
# TODO
#
# - ...
##



from re import compile as compile_regex, match

from os import makedirs
from os.path import join as pjoin, dirname, isdir
from shutil import move

from mp3downloader import download_song, edit_tags, search_song_url
from utils import Song
from dgclient import get_artist_releases, get_songs, get_album_releases

from datetime import datetime, timedelta


def interactive():
	raise NotImplementedError("Interactive mode has not been coded yet, sorry.")

def download():
	if args.url:
		# TODO: check if has already been donwloaded.
		outputfile, title = download_song( args.url, fold = args.fold, overwrite = args.overwrite )
		if outputfile:
			print( f"Downloaded: {args.url} to {outputfile}" )
		else: return False
		if args.title: title = args.title
		song = Song(title, args.artist, args.album)
		newpath = pjoin( dirname(dirname(dirname(outputfile))), song._filepath() )
		if not isdir(dirname(newpath)): makedirs(dirname(newpath))
		if newpath != outputfile:
			move(outputfile, newpath)
			print( f"Song moved to {newpath}" )
			outputfile = newpath
		edit_tags(outputfile, song)
		print( f"Added tags to {song.title}" )
		return outputfile
	else:
		if args.title:
			song = Song(args.title, args.artist, args.album)
			link = search_song_url(song, download_another = args.download_another)
			filepath, title = download_song(link, song, fold = args.fold, overwrite = args.overwrite )
			print( f"Downloaded: {song} to {filepath}" )
			edit_tags(filepath, song)
			return filepath
		elif args.artist:
			if args.album:
				album_release = get_album_releases(args.album, args.artist)[0]
				if album_release:
					songs = get_songs( album_release )
					print( "I found {} songs".format(len(songs)) )
					for song_name in songs:
						print( f"I'll download {song_name}, press Ctrl+C to skip this song" )
						try:
							count = 0
							while count < 3:
								link = search_song_url( songs[song_name], download_another = True )
								count += 1
								if link:
									outputfile, title = download_song( link, song = songs[song_name], fold = args.fold, overwrite = args.overwrite )
									if outputfile:
										edit_tags( outputfile, songs[song_name] )
										print( f"Downloaded {title} to {outputfile}" )
										break
									else: continue
								else:
									print( f"Skipping {song_name}." )
									break
						except KeyboardInterrupt:
							print( f"Skipping {song_name}." )
				else:
					print( f"{args.album} by {args.artist} not found." )
			else:
				print( f"Fetching releases by {args.artist}..." )
				releases = get_artist_releases(args.artist)
				print( f"I found these releases by {args.artist}: " + ", ".join( [r.title().strip() for r in releases] ))
		elif args.album:
			album_rels = get_album_release(args.album, args.artist)
			for x in album_rels:
				print( "I found {args.album} by these artist: " + ", ".join( [r.artists[0].name for r in album_rels] ) )



# Main program
if __name__ == '__main__':
	
	from argparse import ArgumentParser, SUPPRESS

	parser = ArgumentParser("Music organizer", argument_default = SUPPRESS)
	sub_parsers = parser.add_subparsers(dest = 'subparser', required = False)
	download_parser = sub_parsers.add_parser('download')
	download_parser.add_argument('-u', '--url', help = "Download directly by URL")
	download_parser.add_argument('-t', '--title', '--song-title', help = "Search the song with this title")
	download_parser.add_argument('--artist', help = "Specify the artist (if title is not present top songs of this artist will be downloaded)")
	download_parser.add_argument('--album', help = "Specify the album (if title is absent the whole album will be downloaded)")
	download_parser.add_argument('-da', '--download-another', action = 'store_true', help = "Download another version if a video has already been downloaded")
	download_parser.add_argument('--overwrite', '--overwrite-existing', action = 'store_true', help = "Overwrite existing files")
	download_parser.add_argument('-nf', '--do-not-fold', dest = 'fold', action = 'store_false', help = "Don't create artist and album directories")
	args = parser.parse_args()
	try:
		if args.download_another: args.overwrite = True
	except AttributeError: pass

	# parse general arguments
	pass

	try:
		start_time = datetime.now()

		if not args.subparser: interactive()
		else:
			if args.subparser not in locals(): raise NotImplementedError(f"Function {args.subparser} has not been coded yet.")
			locals()[args.subparser]()

		end_time = datetime.now()
		print( "Elapsed time: {}".format(end_time - start_time) )
	except NotImplementedError as nie:
		print(nie)
	except KeyboardInterrupt:
		print("\nInterrupted, exiting.")
		exit(1)