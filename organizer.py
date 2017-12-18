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
from mp3downloader import download_song, edit_tags, Song


def interactive():
	raise NotImplementedError("Interactive mode has not been coded yet, sorry.")

def download():
	if args.url:
		outputfile, title = download_song( args.url )
		if outputfile:
			print( f"Downloaded: {args.url} to {outputfile}" )
		if args.title: title = args.title
		song = Song(title, args.artist, args.album)
		edit_tags(outputfile, song)
		return outputfile
	else:
		if args.title:
			song = Song(args.title, args.artist, args.album)
			link = search_song_url(song)
			filepath, title = download_song(link, song)
			edit_tags(filepath, song)
			return filepath
		


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
	args = parser.parse_args()

	# parse general arguments
	pass

	try:
		if not args.subparser: interactive()
		else:
			if args.subparser not in locals(): raise NotImplementedError(f"Function {args.subparser} has not been coded yet.")
			locals()[args.subparser]()	
	except NotImplementedError as nie:
		print(nie)