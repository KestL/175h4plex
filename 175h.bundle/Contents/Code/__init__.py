# -*- coding: utf-8 -*-

VERSION = 0.1
PREFIX = "/video/175h"
TITLE = '175h.net'
ART = 'art.png'
ICON = 'icon.png'
BASE_URL = 'http://175h.net/'
movies = []

def Start():
	ObjectContainer.art = R(ART)
	ObjectContainer.title1 = TITLE
	DirectoryObject.thumb = R(ICON)

	HTTP.CacheTime = CACHE_1HOUR
	HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; en-US; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5'


@handler(PREFIX, TITLE, thumb=ICON, art=ART, allow_sync=True)
def MainMenu():

	oc = ObjectContainer()
	r = HTTP.Request(BASE_URL + 'id.js', immediate=True, cacheTime=1).content
	r = '[%s]' % (r.split('[', 1)[1].rsplit(']', 1)[0],)
	mlist = JSON.ObjectFromString(r)

	global movies
	for mlink in mlist:
		r = HTTP.Request(BASE_URL + mlink + '/a.js').content
		r = "{%s}" % (r.split('{', 1)[1].rsplit('}', 1)[0])
		movies.append(JSON.ObjectFromString(r))

	for mid,m in enumerate(movies):
		thumb=Resource.ContentsOfURLWithFallback(url=BASE_URL+m['id']+'/p.jpg')
		oc.add(MovieObject(
			key=Callback(Movie, mid=mid),
			rating_key=m['id'],
			title=m['title'] + (' (%s)' % m['title_original'] if m['title_original'] else ''),
			summary=m['storyline'],
			thumb=thumb,
			items=[
				MediaObject(video_resolution = 1080, parts=[PartObject(key=BASE_URL+m['id']+'/1080.mp4')]),
				MediaObject(video_resolution = 720, parts=[PartObject(key=BASE_URL+m['id']+'/720.mp4')])
			]
		))

	return oc


@route(PREFIX+'/{mid}', mid=int, allow_sync=True)
def Movie(mid, includeExtras=0, includeRelated=0, includeRelatedCount=0):
	global movies
	m = movies[mid]
	oc = ObjectContainer()
	art = Resource.ContentsOfURLWithFallback(url=BASE_URL+m['id']+'/1.jpg')
	thumb = Resource.ContentsOfURLWithFallback(url=BASE_URL+m['id']+'/p.jpg')
	kinopoisk = float(XML.ElementFromURL(BASE_URL+'kinopoisk/'+str(m['kinopoisk'])+'.xml').xpath('/rating/kp_rating')[0].text)
	oc.add(MovieObject(
		key=Callback(Movie, mid=mid),
		rating_key=m['id'],
		title=m['title'],
		original_title=m['title_original'],
		summary=m['storyline'],
		year=m['year'],
		tagline=m['motto'],
		rating=kinopoisk,
		genres=[s for s in m['genre'].split(',')],
		directors=[s for s in m['director'].split(',')],
		producers=[s for s in m['producer'].split(',')],
		writers=[s for s in m['writer'].split(',')],
		countries=[s for s in m['country'].split(',')],
		content_rating_age=m['age'],
		duration=int(m['time'])*60000,
		art=art,
		thumb=thumb,
		items=[MediaObject(
			video_resolution=1080,
			video_codec=VideoCodec.H264,
			audio_codec=AudioCodec.AAC,
			container=Container.MP4,
			optimized_for_streaming=True,
			audio_channels=2,
			duration=int(m['time'])*60000,
			parts=[PartObject(key=BASE_URL+m['id']+'/1080.mp4')]
		), MediaObject(
			video_resolution=720,
			video_codec=VideoCodec.H264,
			audio_codec=AudioCodec.AAC,
			container=Container.MP4,
			optimized_for_streaming=True,
			audio_channels=2,
			duration=int(m['time'])*60000,
			parts=[PartObject(key=BASE_URL+m['id']+'/720.mp4')]
		)]
	))
	return oc
