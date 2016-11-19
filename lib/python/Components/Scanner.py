from Plugins.Plugin import PluginDescriptor
from Components.PluginComponent import plugins

import os
from mimetypes import guess_type, add_type

# Matroska Multimedia Container (MKV/MKA/MKS) multimedia container
add_type("video/x-matroska", ".mkv")
add_type("video/x-matroska", ".mks")
add_type("video/mkv", ".mkv")
add_type("audio/x-matroska", ".mka")
# Winamp playlist (M3U/PLS) playlist
add_type("audio/x-mpegurl", ".m3u")
add_type("application/vnd.apple.mpegurl", ".m3u8")
add_type("video/vnd.mpegurl", ".mxu")
add_type("video/vnd.mpegurl", ".m4u")
add_type("application/pls+xml", ".pls")
add_type("audio/x-scpls", ".pls")
# Foobar2000 playlist (FPL) playlist
add_type("application/octet-stream", ".fpl")
# Microsoft Windows Media Player Playlist (WPL) playlist
add_type("application/vnd.ms-wpl", ".wpl")
# Microsoft Advanced Stream Redirector (ASX/LSX) playlist
add_type("video/x-ms-asf", ".asx")
add_type("video/x-la-asf", ".lsx")
# Microsoft Windows Media Video Redirector (WVX) shortcut
add_type("video/x-ms-wmx", ".wmx")
add_type("audio/x-ms-wax", ".wax")
add_type("video/x-ms-wvx", ".wvx")
# MPEG (M3A) playlist
add_type("audio/mpeg", ".m3a")
# WebM, VP8/Vorbis (WEBM) multimedia container
add_type("video/webm", ".webm")
add_type("audio/webm", ".webm")
# Xiph.org Vorbis (OGX/OGG) multimedia container
add_type("application/ogg", ".ogx")
add_type("application/ogg", ".ogg")
add_type("audio/ogg", ".ogg")
add_type("video/ogg", ".ogg")
# Nullsoft Streaming Video (NSV) audio/video container
add_type("application/x-winamp", ".nsv")
add_type("application/x-winamp", ".nsa")
# RealMedia Variable Bitrate (RMVB) audio/video container
add_type("application/vnd.rn-realmedia-vbr", ".rmvb")
# RealMedia (RM) audio/video container
add_type("application/vnd.rn-realmedia", ".rm")
add_type("audio/x-pn-realaudio-plugin", ".rmp")
# Adobe Flash Video (FLV) audio/video container
add_type("audio/x-f4a", ".f4a")
add_type("audio/x-f4a", ".f4b")
add_type("audio/mp4", ".f4a")
add_type("audio/mp4", ".f4b")
add_type("video/x-f4v", ".f4v")
add_type("video/x-f4v", ".f4p")
add_type("video/mp4", ".f4v")
add_type("video/mp4", ".f4p")
add_type("video/x-fli", ".fli")
add_type("video/x-flv", ".flv")
add_type("video/x-m4v", ".m4v")
# Third Generation Partnership Project (3GPP) multimedia container
add_type("audio/3gpp", ".3gp")
add_type("audio/3gpp", ".3ggp")
add_type("audio/3gpp2", ".3g2")
add_type("audio/3gpp2", ".3gp2")
add_type("video/3gpp", ".3gp")
add_type("video/3gpp", ".3ggp")
add_type("video/3gpp2", ".3g2")
add_type("video/3gpp2", ".3gp2")
# MPEG-4 Part 14, MP4 file format, MPEG-4 file format version 2 (MP4) multimedia container
add_type("application/mp4", ".mp4")
add_type("application/mp4", ".mpg4")
add_type("application/mp4", ".mp4s")
add_type("audio/mp4", ".mp4")
add_type("audio/mp4", ".mpg4")
add_type("video/mp4", ".mp4")
add_type("video/mp4", ".mpg4")
# Microsoft Advanced Systems Format (ASF) audio/video container
add_type("application/vnd.ms-asf", ".asf")
add_type("video/x-ms-asf", ".asf")
add_type("video/x-la-asf", ".lsf")
# Microsoft Audio Video Interleave (AVI) audio/video container
add_type("video/vnd.avi", ".avi")
add_type("video/avi", ".avi")
add_type("video/msvideo", ".avi")
add_type("video/x-msvideo", ".avi")
# Musical Instrument Digital Interface (MIDI) synthetized music
add_type("audio/midi", ".mid")
add_type("audio/midi", ".midi")
add_type("audio/midi", ".kar")
add_type("audio/midi", ".rmi")
# Xiph.org Speex (OGA/OGG) lossy speech
add_type("audio/speex", ".spx")
add_type("audio/ogg", ".spx")
# Adaptive Multi-Rate Wideband (AMR-WB) lossy speech
add_type("audio/amr-wb", ".awb")
# Adaptive Multi-Rate (AMR/AMR-NB) lossy speech
add_type("audio/amr", ".amr")
# Xiph.org Free Lossless Audio Codec (FLAC) lossless audio
add_type("audio/x-flac", ".flac")
# WavPack (WV) lossless audio
add_type("audio/x-wavpack", ".wv")
# True Audio (TTA) lossless audio
add_type("audio/x-tta", ".tta")
# Monkey's Audio (APE) lossless audio
add_type("audio/x-ape", ".ape")
add_type("audio/x-ape", ".apl")
# Apple Lossless Audio Codec (ALAC) lossless audio
add_type("audio/x-alac", ".m4a")
# Microsoft Windows Media Audio Lossless (WMA) lossless audio
add_type("audio/x-ms-wma", ".wma")
# Sony Adaptive Transform Acoustic Coding (ATRAC) Advanced Lossless (AA3) lossless audio
add_type("audio/atrac-advanced-lossless", ".aa3")
add_type("audio/atrac-advanced-lossless", ".at3")
# Shorten (SHN) lossless audio
add_type("audio/x-shorten", ".shn")
# Apple Audio Interchange File Format (AIFF) lossless audio
add_type("audio/x-aiff", ".aif")
add_type("audio/x-aiff", ".aiff")
add_type("audio/x-aiff", ".aifc")
add_type("audio/aiff", ".aif")
add_type("audio/aiff", ".aiff")
add_type("audio/aiff", ".aifc")
# Adaptive Differential Pulse Code Modulation (ADPCM) lossless audio
add_type("audio/adpcm", ".adp")
add_type("audio/adpcm", ".adpcm")
# Linear Pulse Code Modulation (LPCM) lossless audio
add_type("audio/l16", ".pcm")
add_type("audio/l16", ".l16")
add_type("audio/l8", ".pcm")
add_type("audio/l20", ".pcm")
add_type("audio/l24", ".pcm")
# Microsoft Waveform Audio File Format (WAVE) lossless audio
add_type("audio/vnd.wave", ".wav")
add_type("audio/vnd.wave", ".wave")
add_type("audio/wav", ".wav")
add_type("audio/wav", ".wave")
add_type("audio/wave", ".wav")
add_type("audio/wave", ".wave")
add_type("audio/x-wav", ".wav")
add_type("audio/x-wav", ".wave")
# Xiph.org Vorbis (OGA/OGG) lossy audio
add_type("audio/ogg", ".oga")
add_type("audio/vorbis", ".oga")
add_type("audio/vorbis-config", ".oga")
# MusePack (MPC) lossy audio
add_type("audio/x-musepack", ".mpc")
add_type("audio/x-musepack", ".mp+")
add_type("audio/x-musepack", ".mpp")
add_type("audio/musepack", ".mpc")
add_type("audio/musepack", ".mp+")
add_type("audio/musepack", ".mpp")
# RealAudio (RA) lossy audio
add_type("audio/x-pn-realaudio", ".ra")
add_type("audio/x-pn-realaudio", ".ram")
# Microsoft Windows Media Audio (WMA) lossy audio
add_type("audio/x-ms-wma", ".wma")
# Sony Adaptive Transform Acoustic Coding (ATRAC) (AA3) lossy audio
add_type("audio/atrac-x", ".aa3")
add_type("audio/atrac-x", ".at3")
add_type("audio/atrac3", ".aa3")
add_type("audio/atrac3", ".at3")
add_type("audio/x-oma", ".oma")
# DTS Theater System (DTS) lossy audio
add_type("audio/vnd.dts", ".dts")
add_type("audio/vnd.dts.hd", ".dtshd")
# Dolby Digital (AC3) lossy audio
add_type("audio/ac3", ".ac3")
# MPEG-4 Part 3, Audio, High-Efficiency Advanced Audio Coding (HE-AAC) (AAC) lossy audio
add_type("audio/aacp", ".aac")
# MPEG-4 Part 3, Audio, Advanced Audio Coding (AAC) lossy audio
add_type("audio/x-aac", ".aac")
add_type("audio/aac", ".aac")
add_type("audio/mp4", ".aac")
# MPEG-4 Part 3, Audio, various formats (M4A) lossy audio
add_type("audio/mp4", ".m4a")
add_type("audio/mp4", ".mp4a")
add_type("audio/mp4", ".m4p")
add_type("audio/mp4", ".m4b")
add_type("audio/mp4", ".m4r")
add_type("audio/mp4a-latm", ".m4a")
add_type("audio/mpeg4-generic", ".m4a")
# MPEG-2 Part 3, Audio, Layer I/II/II (M2A) lossy audio
add_type("audio/mpeg", ".m2a")
add_type("audio/mpeg", ".mp2a")
# MPEG-1 Part 3, Audio, Layer III (MP3) lossy audio
add_type("audio/mpeg", ".mp3")
add_type("audio/mpa", ".mp3")
add_type("audio/mpa-robust", ".mp3")
# MPEG-1 Part 3, Audio, Layer II (MP2) lossy audio
add_type("audio/mpeg", ".mp2")
add_type("audio/mpeg", ".mpa")
add_type("audio/mpeg", ".mpga")
add_type("audio/mpeg", ".mpega")
add_type("audio/mpa", ".mp2")
add_type("audio/mpa", ".mpa")
add_type("audio/mpa", ".mpga")
add_type("audio/mpa", ".mpega")
# MPEG-1 Part 3, Audio, Layer I (MP1) lossy audio
add_type("audio/mpeg", ".mp1")
add_type("audio/mpeg", ".m1a")
add_type("audio/mpeg", ".mpa")
add_type("audio/mpeg", ".mpga")
add_type("audio/mpeg", ".mpega")
add_type("audio/mpa", ".mp1")
add_type("audio/mpa", ".m1a")
add_type("audio/mpa", ".mpa")
add_type("audio/mpa", ".mpga")
add_type("audio/mpa", ".mpega")
# Sun Au file format (AU/SND) lossy audio
add_type("audio/basic", ".au")
add_type("audio/basic", ".snd")
# Xiph.org Theora, VP3 (OGV/OGG) lossy video
add_type("video/ogg", ".ogv")
# RealVideo (RV) lossy video
add_type("video/x-pn-realvideo", ".rv")
add_type("video/x-rn-realvideo", ".rv")
# Apple QuickTime File Format (QTFF) (QT/MOV) lossy video
add_type("video/quicktime", ".mov")
add_type("video/quicktime", ".qt")
add_type("video/x-sgi-movie", ".movie")
add_type("video/x-sgi-movie", ".mv")
# Microsoft Windows Media Video, VC-1 (WMV) lossy video
add_type("video/x-ms-wm", ".wm")
add_type("video/x-ms-wmv", ".wmv")
add_type("video/x-ms-wmx", ".wmx")
add_type("video/x-ms-wvx", ".wvx")
# 4k H.265
add_type("video/h265", ".h265")
# MPEG-4 Part 10, Advanced Video Coding (AVC), H.264 lossy video
add_type("video/h264", ".h264")
# VCEG H.261/H.263 lossy video
add_type("video/h261", ".h261")
add_type("video/h263", ".h263")
# MPEG-4 Part 2, Visual, Advanced Simple Profile (ASP), Xvid/DivX lossy video
add_type("video/x-divx", ".xvid|.divx")
add_type("video/x-divx", ".divx")
# MPEG-4 Part 2/10/14, Video, various formats (M4V) video
add_type("video/mp4", ".m4v")
add_type("video/mp4", ".mp4v")
add_type("video/mp4", ".3gp")
add_type("video/mp4", ".3g2")
add_type("video/mpeg4-generic", ".m4v")
# Various formats
add_type("video/mpeg", ".mts")
add_type("video/mpeg", ".mpe")
add_type("video/mpeg", ".mpeg")
add_type("video/mpeg", ".mpg")
add_type("video/x-rad-screenplay", ".vx")
add_type("video/MP2T", ".ts")
add_type("video/x-dvd-iso", ".iso")
# Debian (DEB) archives
add_type("application/x-debian-package", ".deb")
add_type("application/x-debian-package", ".udeb")
add_type("application/x-debian-package", ".ipk")
# DreamBox archives
add_type("application/x-dream-package", ".dmpkg")
add_type("application/x-dream-image", ".nfi")

def getType(file):
	(type, _) = guess_type(file)
	if type is None:
		# Detect some unknown types
		if file[-12:].lower() == "video_ts.ifo":
			return "video/x-dvd"
		if file == "/media/audiocd/cdplaylist.cdpls":
			return "audio/x-cda"

		p = file.rfind('.')
		if p == -1:
			return None
		ext = file[p+1:].lower()

		if ext == "dat" and file[-11:-6].lower() == "avseq":
			return "video/x-vcd"
	return type

class Scanner:
	def __init__(self, name, mimetypes= [], paths_to_scan = [], description = "", openfnc = None):
		self.mimetypes = mimetypes
		self.name = name
		self.paths_to_scan = paths_to_scan
		self.description = description
		self.openfnc = openfnc

	def checkFile(self, file):
		return True

	def handleFile(self, res, file):
		if (self.mimetypes is None or file.mimetype in self.mimetypes) and self.checkFile(file):
			res.setdefault(self, []).append(file)

	def __repr__(self):
		return "<Scanner " + self.name + ">"

	def open(self, list, *args, **kwargs):
		if self.openfnc is not None:
			self.openfnc(list, *args, **kwargs)

class ScanPath:
	def __init__(self, path, with_subdirs = False):
		self.path = path
		self.with_subdirs = with_subdirs

	def __repr__(self):
		return self.path + "(" + str(self.with_subdirs) + ")"

	# we will use this in a set(), so we need to implement __hash__ and __cmp__
	def __hash__(self):
		return self.path.__hash__() ^ self.with_subdirs.__hash__()

	def __cmp__(self, other):
		if self.path < other.path:
			return -1
		elif self.path > other.path:
			return +1
		else:
			return self.with_subdirs.__cmp__(other.with_subdirs)

class ScanFile:
	def __init__(self, path, mimetype = None, size = None, autodetect = True):
		self.path = path
		if mimetype is None and autodetect:
			self.mimetype = getType(path)
		else:
			self.mimetype = mimetype
		self.size = size

	def __repr__(self):
		return "<ScanFile " + self.path + " (" + str(self.mimetype) + ", " + str(self.size) + " MB)>"

def execute(option):
	print "execute", option
	if option is None:
		return

	(_, scanner, files, session) = option
	scanner.open(files, session)

def scanDevice(mountpoint):
	scanner = [ ]

	for p in plugins.getPlugins(PluginDescriptor.WHERE_FILESCAN):
		l = p()
		if not isinstance(l, list):
			l = [l]
		scanner += l

	print "scanner:", scanner

	res = { }

	# merge all to-be-scanned paths, with priority to
	# with_subdirs.

	paths_to_scan = set()

	# first merge them all...
	for s in scanner:
		paths_to_scan.update(set(s.paths_to_scan))

	# ...then remove with_subdir=False when same path exists
	# with with_subdirs=True
	for p in paths_to_scan:
		if p.with_subdirs == True and ScanPath(path=p.path) in paths_to_scan:
			paths_to_scan.remove(ScanPath(path=p.path))

	from Components.Harddisk import harddiskmanager
	blockdev = mountpoint.rstrip("/").rsplit('/',1)[-1]
	error, blacklisted, removable, is_cdrom, partitions, medium_found = harddiskmanager.getBlockDevInfo(blockdev)

	# now scan the paths
	for p in paths_to_scan:
		path = os.path.join(mountpoint, p.path)

		for root, dirs, files in os.walk(path):
			for f in files:
				path = os.path.join(root, f)
				if (is_cdrom and f.endswith(".wav") and f.startswith("track")) or f == "cdplaylist.cdpls":
					sfile = ScanFile(path,"audio/x-cda")
				else:
					sfile = ScanFile(path)
				for s in scanner:
					s.handleFile(res, sfile)

			# if we really don't want to scan subdirs, stop here.
			if not p.with_subdirs:
				del dirs[:]

	# res is a dict with scanner -> [ScanFiles]
	return res

def openList(session, files):
	if not isinstance(files, list):
		files = [ files ]

	scanner = [ ]

	for p in plugins.getPlugins(PluginDescriptor.WHERE_FILESCAN):
		l = p()
		if not isinstance(l, list):
			scanner.append(l)
		else:
			scanner += l

	print "scanner:", scanner

	res = { }

	for file in files:
		for s in scanner:
			s.handleFile(res, file)

	choices = [ (r.description, r, res[r], session) for r in res ]
	Len = len(choices)
	if Len > 1:
		from Screens.ChoiceBox import ChoiceBox

		session.openWithCallback(
			execute,
			ChoiceBox,
			title = "The following viewers were found...",
			list = choices
		)
		return True
	elif Len:
		execute(choices[0])
		return True

	return False

def openFile(session, mimetype, file):
	return openList(session, [ScanFile(file, mimetype)])
