# the implementation here is a bit crappy.
import time
from Directories import resolveFilename, SCOPE_CONFIG
from boxbranding import getBoxType

PERCENTAGE_START = 0
PERCENTAGE_END = 100

profile_start = time.time()

profile_data = {}
total_time = 1
profile_file = None

try:
	f = open(resolveFilename(SCOPE_CONFIG, "profile"), "r")
	profile_old = f.readlines()
	f.close()

	t = None
	for line in profile_old:
		(t, id) = line[:-1].split('\t')
		t = float(t)
		total_time = t
		profile_data[id] = t
except:
	print "[Profile] no profile data available"

try:
	profile_file = open(resolveFilename(SCOPE_CONFIG, "profile"), "w")
except IOError:
	print "[Profile] WARNING: couldn't open profile file!"

def profile(id):
	now = time.time() - profile_start

	box_type = getBoxType()
	if box_type in ("classm", "axodin", "axodinc", "starsatlx", "evo", "genius", "galaxym6"):
		dev_fmt = ("/dev/dbox/oled0", "%d")
	elif box_type in ("marvel1", "enfinity"):
		dev_fmt = ("/dev/dbox/oled0", "  %d ")
	elif box_type in ("formuler1", "formuler3", "formuler4"):
		dev_fmt = ("/dev/dbox/oled0", "  %d ")
	elif box_type in ('gb800solo', 'gb800se', 'gb800seplus', 'gbultrase'):
		dev_fmt = ("/dev/mcu", "%d \n")
	elif box_type in ("mixosf5", "gi9196m", "osmini", "spycatmini", "osminiplus", "spycatminiplus"):
		dev_fmt = ("/proc/progress", "%d")
	elif box_type in ("xpeedlx3", "sezammarvel", "atemionemesis", "fegasusx3", "fegasusx5s", "fegasusx5t"):
		dev_fmt = ("/proc/vfd", "Loading %d %%")
	elif box_type in ("azboxhd", "azboxme", "azboxminime"):
		dev_fmt = ("/proc/vfd", "Loading %d%%")
	elif box_type in ('amikomini', 'amiko8900', 'sognorevolution', 'arguspingulux', 'arguspinguluxmini', 'sparkreloaded', 'sabsolo', 'sparklx', 'gis8120'):
		dev_fmt = ("/proc/vfd", "%d \n")
	else:
		dev_fmt = ("/proc/progress", "%d \n")
	(dev, fmt) = dev_fmt

	if profile_file:
		profile_file.write("%7.3f\t%s\n" % (now, id))

		if id in profile_data:
			t = profile_data[id]
			if total_time:
				perc = t * (PERCENTAGE_END - PERCENTAGE_START) / total_time + PERCENTAGE_START
			else:
				perc = PERCENTAGE_START
			try:
				f = open(dev, "w")
				f.write(fmt % perc)
				f.close()
			except IOError:
				pass

def profile_final():
	global profile_file
	if profile_file is not None:
		profile_file.close()
		profile_file = None
