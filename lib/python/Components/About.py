# -*- coding: utf-8 -*-
from boxbranding import getBoxType, getMachineBuild, getImageVersion
from time import *
from types import *
from sys import modules
import sys, os, time, socket, fcntl, struct, subprocess, threading, traceback, commands, datetime
from os import path, system, remove as os_remove, rename as os_rename, popen, getcwd, chdir

def getVersionString():
	return getImageVersion()

def getImageVersionString():
	try:
		if os.path.isfile('/var/lib/opkg/status'):
			st = os.stat('/var/lib/opkg/status')
		else:
			st = os.stat('/usr/lib/ipkg/status')
		tm = time.localtime(st.st_mtime)
		if tm.tm_year >= 2011:
			return time.strftime("%Y-%m-%d %H:%M:%S", tm)
	except:
		pass
	return _("unavailable")

def getFlashDateString():
	try:
		if path.exists("/boot/STARTUP"):
			return _("Multiboot active")
		else:
			return time.strftime(_("%Y-%m-%d"), time.localtime(os.stat("/boot").st_ctime))
	except:
		return _("unknown")

def getEnigmaVersionString():
	return getImageVersion()

def getGStreamerVersionString():
	import enigma
	return enigma.getGStreamerVersionString()

def getKernelVersionString():
	try:
		f = open("/proc/version","r")
		kernelversion = f.read().split(' ', 4)[2].split('-',2)[0]
		f.close()
		return kernelversion
	except:
		return _("unknown")

def getModelString():
	try:
		file = open("/proc/stb/info/boxtype", "r")
		model = file.readline().strip()
		file.close()
		return model
	except IOError:
		return _("unknown")

def getIsBroadcom():
	try:
		file = open('/proc/cpuinfo', 'r')
		lines = file.readlines()
		for x in lines:
			splitted = x.split(': ')
			if len(splitted) > 1:
				splitted[1] = splitted[1].replace('\n','')
				if splitted[0].startswith("Hardware"):
					system = splitted[1].split(' ')[0]
				elif splitted[0].startswith("system type"):
					if splitted[1].split(' ')[0].startswith('BCM'):
						system = 'Broadcom'
		file.close()
		if 'Broadcom' in system:
			return True
		else:
			return False
	except:
		return False

def getChipSetString():
	if getMachineBuild() in ('dm7080', 'dm820'):
		return "7435"
	elif getMachineBuild() in ('dm520'):
		return "73625"
	elif getMachineBuild() in ('dm900'):
		return "7252S"
	elif getMachineBuild() in ('hd51'):
		return "7251S"
	else:
		try:
			f = open('/proc/stb/info/chipset', 'r')
			chipset = f.read()
			f.close()
			return str(chipset.lower().replace('\n','').replace('bcm','').replace('brcm','').replace('sti',''))
		except IOError:
			return _("unavailable")

def getCPUSpeedString():
	if getMachineBuild() in ('vusolo4k', 'vuultimo4k'):
		return "1,5 GHz"
	elif getMachineBuild() in ('formuler1tc', 'formuler1', 'triplex'):
		return "1,3 GHz"
	elif getMachineBuild() in ('vuuno4k', 'dm900', 'gbquad4k'):
		return "1,7 GHz"
	elif getMachineBuild() in ('hd51', 'hd52', 'sf4008'):
		try:
			import binascii
			f = open('/sys/firmware/devicetree/base/cpus/cpu@0/clock-frequency', 'rb')
			clockfrequency = f.read()
			f.close()
			return "%s MHz" % str(round(int(binascii.hexlify(clockfrequency), 16)/1000000,1))
		except:
			return "1,7 GHz"
	else:
		try:
			file = open('/proc/cpuinfo', 'r')
			lines = file.readlines()
			for x in lines:
				splitted = x.split(': ')
				if len(splitted) > 1:
					splitted[1] = splitted[1].replace('\n','')
					if splitted[0].startswith("cpu MHz"):
						mhz = float(splitted[1].split(' ')[0])
						if mhz and mhz >= 1000:
							mhz = "%s GHz" % str(round(mhz/1000,1))
						else:
							mhz = "%s MHz" % str(round(mhz,1))
			file.close()
			return mhz
		except IOError:
			return _("unavailable")

def getCPUArch():
	import os
	if os.uname()[4].startswith("arm"):
		return _("ARM")
	elif os.uname()[4].startswith("sh4"):
		return _("SH4")
	elif os.uname()[4].startswith("mips"):
		return _("Mipsel")
	else:
		return _("unknown")

def getCPUString():
	if getMachineBuild() in ('vuuno4k', 'vuultimo4k', 'vusolo4k', 'hd51', 'hd52', 'sf4008', 'dm900', 'gbquad4k'):
		return "Broadcom"
	else:
		try:
			system="unknown"
			file = open('/proc/cpuinfo', 'r')
			lines = file.readlines()
			for x in lines:
				splitted = x.split(': ')
				if len(splitted) > 1:
					splitted[1] = splitted[1].replace('\n','')
					if splitted[0].startswith("system type"):
						system = splitted[1].split(' ')[0]
					elif splitted[0].startswith("model name"):
						system = splitted[1].split(' ')[0]
					elif splitted[0].startswith("Processor"):
						system = splitted[1].split(' ')[0]
			file.close()
			return system
		except IOError:
			return _("unavailable")

def getCpuCoresString2():
	MachinesCores = {
					1 : 'Single core',
					2 : 'Dual core',
					4 : 'Quad core',
					8 : 'Octa core'
					}
	try:
		cores = 1
		file = open('/proc/cpuinfo', 'r')
		lines = file.readlines()
		file.close()
		for x in lines:
			splitted = x.split(': ')
			if len(splitted) > 1:
				splitted[1] = splitted[1].replace('\n','')
				if splitted[0].startswith("processor"):
					cores = int(splitted[1]) + 1
		return MachinesCores[cores]
	except IOError:
		return _("unavailable")

def getCpuCoresString():
	try:
		file = open('/proc/cpuinfo', 'r')
		lines = file.readlines()
		for x in lines:
			splitted = x.split(': ')
			if len(splitted) > 1:
				splitted[1] = splitted[1].replace('\n','')
				if splitted[0].startswith("processor"):
					if int(splitted[1]) > 0:
						cores = 2
					else:
						cores = 1
		file.close()
		return cores
	except IOError:
		return _("unavailable")

def _ifinfo(sock, addr, ifname):
	iface = struct.pack('256s', ifname[:15])
	info  = fcntl.ioctl(sock.fileno(), addr, iface)
	if addr == 0x8927:
		return ''.join(['%02x:' % ord(char) for char in info[18:24]])[:-1].upper()
	else:
		return socket.inet_ntoa(info[20:24])

def getIfConfig(ifname):
	ifreq = {'ifname': ifname}
	infos = {}
	sock  = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	# offsets defined in /usr/include/linux/sockios.h on linux 2.6
	infos['addr']    = 0x8915 # SIOCGIFADDR
	infos['brdaddr'] = 0x8919 # SIOCGIFBRDADDR
	infos['hwaddr']  = 0x8927 # SIOCSIFHWADDR
	infos['netmask'] = 0x891b # SIOCGIFNETMASK
	try:
		for k,v in infos.items():
			ifreq[k] = _ifinfo(sock, v, ifname)
	except:
		pass
	sock.close()
	return ifreq

def getIfTransferredData(ifname):
	f = open('/proc/net/dev', 'r')
	for line in f:
		if ifname in line:
			data = line.split('%s:' % ifname)[1].split()
			rx_bytes, tx_bytes = (data[0], data[8])
			f.close()
			return rx_bytes, tx_bytes

def getDriverInstalledDate():
	try:
		from glob import glob
		driver = [x.split("-")[-2:-1][0][-8:] for x in open(glob("/var/lib/opkg/info/*-dvb-modules-*.control")[0], "r") if x.startswith("Version:")][0]
		return  "%s-%s-%s" % (driver[:4], driver[4:6], driver[6:])
	except:
		return _("unknown")

def getPythonVersionString():
	import sys
	return "%s.%s.%s" % (sys.version_info.major,sys.version_info.minor,sys.version_info.micro)

def getFFmpegVersionString():
	import commands
	try:
		ffmpegV = commands.getoutput("ffmpeg -version | awk 'NR==1{print $3}'")
		output = ffmpegV
		return output.split(' ')[0]
	except:
		return _("unknown")

def getCPUTempString():
	try:
		if os.path.isfile('/proc/stb/fp/temp_sensor_avs'):
			temperature = open("/proc/stb/fp/temp_sensor_avs").readline().replace('\n','')
			return _("%s°C") % temperature
	except:
		pass
	return ""

def getLoadCPUString():
	import commands
	try:
		output = commands.getoutput("top -bn1 | grep load | awk '{printf \"%.2f\", $(NF-2)}'")
		return output.split(' ')[0]
	except:
		return _("unknown")

def getRAMusageString():
	import commands
	try:
		output = commands.getoutput("free -m | awk 'NR==2{printf \"%s/%sMB %.2f%%\", $3,$2,$3*100/$2 }'")
		return output.split(' ')[1]
	except:
		return _("unknown")

def getRAMFreePorcString():
	import commands
	try:
		output = commands.getoutput("free -m | awk 'NR==2{printf \"%s/%sMB %.2f%%\", $4,$2,$4*100/$2 }'")
		return output.split(' ')[1]
	except:
		return _("unknown")

def getRAMTotalString():
	import commands
	try:
		output = commands.getoutput("free -m | awk 'NR==2{print $2}'")
		return output.split(' ')[0]
	except:
		return _("unknown")

def getRAMUsedString():
	import commands
	try:
		output = commands.getoutput("free -m | awk 'NR==2{print $3}'")
		return output.split(' ')[0]
	except:
		return _("unknown")

def getRAMUsedKBString():
	import commands
	try:
		output = commands.getoutput("free | grep Mem: | awk '{print $3}'")
		return output.split(' ')[0]
	except:
		return _("unknown")

def getRAMFreeString():
	import commands
	try:
		output = commands.getoutput("free -m | awk 'NR==2{print $4}'")
		return output.split(' ')[0]
	except:
		return _("unknown")

def getRAMSharingString():
	import commands
	try:
		output = commands.getoutput("free -m | awk 'NR==2{print $5}'")
		return output.split(' ')[0]
	except:
		return _("unknown")

def getRAMStoredString():
	import commands
	try:
		output = commands.getoutput("free -m | awk 'NR==2{print $6}'")
		return output.split(' ')[0]
	except:
		return _("unknown")

def getRAMCachedString():
	import commands
	try:
		output = commands.getoutput("free -m | awk 'NR==2{print $7}'")
		return output.split(' ')[0]
	except:
		return _("unknown")

def getRAMSwapTotalString():
	import commands
	try:
		output = commands.getoutput("free -m | awk 'NR==3{print $2}'")
		return output.split(' ')[0]
	except:
		return _("unknown")

def getRAMSwapUsedString():
	import commands
	try:
		output = commands.getoutput("free -m | awk 'NR==3{print $3}'")
		return output.split(' ')[0]
	except:
		return _("unknown")

def getRAMSwapFreeString():
	import commands
	try:
		output = commands.getoutput("free -m | awk 'NR==3{print $4}'")
		return output.split(' ')[0]
	except:
		return _("unknown")

def getRAMTotalGlobalString():
	import commands
	try:
		output = commands.getoutput("free -h -t | sed '1 d' | grep Total: | awk '{print $2}'")
		return output.split(' ')[0]
	except:
		return _("unknown")

def getRAMUsedGlobalString():
	import commands
	try:
		output = commands.getoutput("free -h -t | sed '1 d' | grep Total: | awk '{print $3}'")
		return output.split(' ')[0]
	except:
		return _("unknown")

def getRAMFreeGlobalString():
	import commands
	try:
		output = commands.getoutput("free -h -t | sed '1 d' | grep Total: | awk '{print $4}'")
		return output.split(' ')[0]
	except:
		return _("unknown")

# For modules that do "from About import about"
about = modules[__name__]
