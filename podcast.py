#!/usr/bin/env python3

import uuid
import os, sys
import argparse
import subprocess, string
from glob import glob
from pathlib import Path
from urllib.parse import quote
from datetime import datetime
from xml.sax.saxutils import escape

parser = argparse.ArgumentParser(prog='mnml-podcast-generator', description='Generate a podcast RSS feed xml file based on a collection of MP3/M4A files')
parser.add_argument('-u', '--urlbase', help='Internet-accessible URL base where MP3/M4A files for this podcast are hosted', default='https://example.com/podcast')
parser.add_argument('-n', '--name', help='Podcast name', default='My podcast')
parser.add_argument('-l', '--link', help='Podcast link', default='https://example.com/podcast')
parser.add_argument('-d', '--description', help='Podcast description', default='Welcome to my podcast')
parser.add_argument('-o', '--owner', help='Podcast owner email address', default='podcast@example.com')
parser.add_argument('-a', '--author', help='Podcast author', default='Anonymous')
parser.add_argument('-i', '--image', help='Cover image', default='https://example.com/podcast/cover.jpg')
parser.add_argument('-p', '--print', help='Print episode order only', action='store_true')
parser.add_argument('-s', '--special', help='Apply special episode ordering', action='store_true')
args = parser.parse_args()

if args.urlbase[-1] != '/':
    args.urlbase += '/'

pubDate = datetime.now().astimezone().strftime("%A, %d %b %Y %H:%M:%S %z") #pubDate for all episodes is the time you run this script
files = sorted(glob('*.m4a')+glob('*.mp3'))
i = 1

if args.special:
   files = files[52:108]+files[0:52]
if args.print:
  for f in files:
     print(f'{i}. {f}')
     i+=1
  sys.exit(0)

items = ''
for filename in files:
    filetype = 'audio/mpeg'
    if filename[-3:].lower() == 'm4a':
        filetype = 'audio/mp4'
    duration_in_seconds = int(float(subprocess.check_output(['ffprobe', '-i', filename, '-show_entries', 'format=duration', '-v', 'quiet', '-of', 'csv=p=0']).strip().decode()))
    bitrate = round(int(subprocess.check_output(['ffprobe', '-v', '0', '-select_streams', 'a:0', '-show_entries', 'stream=bit_rate' ,'-of', 'compact=p=0:nk=1', filename]).decode().replace('\n','').replace('|',''))/1000)
    items += f'''
    <item>
        <pubDate>{pubDate}</pubDate>
        <title>{escape(Path(filename).stem.replace('_',' '))}</title>
        <description/>
        <guid isPermaLink="true">{args.urlbase+quote(filename)}</guid>
        <enclosure url="{args.urlbase+quote(filename)}" type="{filetype}" length="{os.path.getsize(filename)}"/>
        <itunes:explicit>no</itunes:explicit>
        <itunes:duration>{duration_in_seconds}</itunes:duration>
        <itunes:episode>{i}</itunes:episode>
        <itunes:season>1</itunes:season>
        <itunes:episodeType>full</itunes:episodeType>
        <itunes:subtitle>{bitrate} kbps {filename[-3:].upper()}</itunes:subtitle>
    </item>'''
    i+=1

print(f'''<?xml version="1.0" encoding="UTF-8"?>
<rss xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:podcast="https://podcastindex.org/namespace/1.0" version="2.0">
  <channel>
    <title>{args.name}</title>
    <description>{args.description}</description>
    <language>en-us</language>
    <link>{args.link}</link>
    <atom:link href="{args.urlbase}index.rss" rel="self" type="application/rss+xml"/>
    <itunes:explicit>no</itunes:explicit>
    <itunes:owner>
      <itunes:email>{args.owner}</itunes:email>
    </itunes:owner>
    <itunes:author>{args.author}</itunes:author>
    <itunes:summary>{args.description}</itunes:summary>      
    <itunes:category text="Music"/>
    <itunes:image href="{args.image}"/>
    <podcast:locked owner="{args.owner}">no</podcast:locked>
    <podcast:guid>{uuid.uuid4()}</podcast:guid>
    <image>
        <url>{args.image}</url>
        <title>{args.name}</title>
        <link>{args.urlbase}></link>
    </image>{items}
  </channel>
</rss>''')
