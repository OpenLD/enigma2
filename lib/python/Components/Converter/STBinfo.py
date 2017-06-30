from Components.About import about
from Components.Converter.Converter import Converter
from Components.config import config
from Components.Element import cached
from Poll import Poll
from time import *
from types import *
from sys import modules
import sys, os, time, socket, fcntl, struct, subprocess, threading, traceback, commands, datetime
from os import path, system, remove as os_remove, rename as os_rename, popen, getcwd, chdir
import Screens.Standby

class STBinfo(Converter, object):

	def __init__(self, type):
		Converter.__init__(self, type)
		self.type = type

	@cached
	def getText(self):
		if Screens.Standby.inStandby:
			return ""
		elif self.type == "CPUload":
			return self.getCPUload()
		elif self.type == "RAMfree":
			return self.getRAMfree()
		elif self.type == "CPUtemp":
			return self.getCPUtemp()
		elif self.type == "SYStemp":
			return self.getSYStemp()
		elif self.type == "FLASHfree":
			return self.getFLASHfree()
		elif self.type == "CPUspeed":
			return self.getCPUspeed()
		return ""

	def getCPUload(self):
		info = ""
		if path.exists('/proc/loadavg'):
			f = open('/proc/loadavg', 'r')
			temp = f.readline(4)
			f.close()
			info = temp.replace('\n', '').replace(' ','')
			info = _("Load: %s") % info
		return info

	def getRAMfree(self):
		info = ""
		info = str(about.getRAMFreeString())
		info = _("RAM-Free: %s MB") % info
		return info

	def getCPUtemp(self):
		info = ""
		temp = ""
		if path.exists('/proc/stb/fp/temp_sensor_avs'):
			f = open('/proc/stb/fp/temp_sensor_avs', 'r')
			temp = f.readline()
			f.close()
		if temp and int(temp.replace('\n', '')) > 0:
			info = temp.replace('\n', '').replace(' ','') + str('\xc2\xb0') + "C"
			info = _("CPU-Temp: %s") % info
		return info

	def getSYStemp(self):
		info = ""
		temp = ""
		if path.exists('/proc/stb/sensors/temp0/value'):
			f = open('/proc/stb/sensors/temp0/value', 'r')
			temp = f.readline()
			f.close()
		elif path.exists('/proc/stb/fp/temp_sensor'):
			f = open('/proc/stb/fp/temp_sensor', 'r')
			temp = f.readline()
			f.close()
		elif path.exists('/proc/stb/sensors/temp/value'):
			f = open('/proc/stb/sensors/temp/value', 'r')
			temp = f.readline()
			f.close()
		if temp and int(temp.replace('\n', '')) > 0:
			info = temp.replace('\n', '').replace(' ','') + str('\xc2\xb0') + "C"
			info = _("SYS-Temp: %s") % info
		return info

	def getFLASHfree(self):
		info = ""
		cmd = 'df -m'
		try:
			temp = popen(cmd).readlines()
			for lines in temp:
				lisp = lines.split()
				if lisp[5] == "/":
					info = lisp[3].replace(' ','')
					info = _("Flash Memory free: %s MByte") % info
					break
		except:
			pass
		return info

	def getCPUspeed(self):
		info = ""
		if path.exists('/proc/cpuinfo'):
			f = open('/proc/cpuinfo', 'r')
			temp = f.readlines()
			f.close()
			try:
				for lines in temp:
					lisp = lines.split(': ')
					if lisp[0].startswith('cpu MHz'):
						info = str(int(float(lisp[1].replace('\n', ''))))
						info = _("CPU-Speed: %s MHz") % info
						break
			except:
				pass
		return info

	text = property(getText)
