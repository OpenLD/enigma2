from enigma import *
from Screens.Screen import Screen
from Components.Button import Button
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.ScrollLabel import ScrollLabel
from Components.MenuList import MenuList
from Components.Sources.List import List
from Components.About import about
from Tools.Directories import fileExists
from ServiceReference import ServiceReference
from os import system, listdir, remove as os_remove
from enigma import iServiceInformation, eTimer

			
class LdsysInfo(Screen):
	skin = """
	<screen position="center,center" size="800,560" title="OpenLD - Info">
	<ePixmap position="460,10" size="310,165" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/LDteam/images/menu/ld.png" alphatest="blend" transparent="1" />
	<widget name="lab1" position="50,25" halign="left" size="700,550" zPosition="1" font="Regular;20" valign="top" transparent="1" />
	</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		self["lab1"] =  Label()

		self.onShow.append(self.updateInfo)
		
		self["myactions"] = ActionMap(["OkCancelActions"],
		{
			"ok": self.close,
			"cancel": self.close,
		}, -1)
		
	def updateInfo(self):
		rc = system("df -h > /tmp/syinfo.tmp")
		text = "BOX\n"
		f = open("/proc/stb/info/model",'r')
 		text += "Marca:\t" + f.readline()
 		f.close()
		f = open("/proc/stb/info/gbmodel",'r')
 		text += "Model:\t" + f.readline()
 		f.close()
		f = open("/proc/stb/info/chipset",'r')
 		text += "Chipset:\t" + f.readline() +"\n"
 		f.close()		
		text += "MEMORY\n"
		memTotal = memFree = swapTotal = swapFree = 0
		for line in open("/proc/meminfo",'r'):
			parts = line.split(':')
			key = parts[0].strip()
			if key == "MemTotal":
				memTotal = parts[1].strip()
			elif key in ("MemFree", "Buffers", "Cached"):
				memFree += int(parts[1].strip().split(' ',1)[0])
			elif key == "SwapTotal":
				swapTotal = parts[1].strip()
			elif key == "SwapFree":
				swapFree = parts[1].strip()
		text += "Total memory:\t%s\n" % memTotal
		text += "Free memory:\t%s kB\n"  % memFree
		text += "Swap total:\t%s \n"  % swapTotal
		text += "Swap free:\t%s \n"  % swapFree
		text += "\nSTORAGE\n"
		f = open("/tmp/syinfo.tmp",'r')
		line = f.readline()
		parts = line.split()
		text += parts[0] + "\t" + parts[1].strip() + "      " + parts[2].strip() + "    " + parts[3].strip() + "    " + parts[4] + "\n"
		line = f.readline()
		parts = line.split()
		text += "Flash" + "\t" + parts[1].strip() + "  " + parts[2].strip()  + "  " +  parts[3].strip()  + "  " +  parts[4] + "\n"
 		for line in f.readlines():
			if line.find('/media/') != -1:
				line = line.replace('/media/', '   ')
				parts = line.split()
				if len(parts) == 6:
					text += parts[5] + "\t" + parts[1].strip() + "  " + parts[2].strip() + "  " + parts[3].strip() + "  " + parts[4] + "\n"
		f.close()
		os_remove("/tmp/syinfo.tmp")
		
		text += "\nSOFTWARE\n"
		f = open("/etc/ldversion",'r')
		text += "Firmware: \t" + f.readline() + "\n"
		f.close()
		text += "Enigma2: \t" +  about.getEnigmaVersionString() + "\n"
		text += "Kernel: \t" +  about.getKernelVersionString() + "\n"
		
		self["lab1"].setText(text)
		
