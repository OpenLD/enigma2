from Screens.Console import Console
from Screens.Screen import Screen
from Screens.ChoiceBox import ChoiceBox
from Screens.MessageBox import MessageBox
from Components.FileList import FileEntryComponent, FileList
from Components.ActionMap import ActionMap, NumberActionMap, HelpableActionMap
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from Components.Button import Button
from Components.Label import Label
from Components.config import config, ConfigElement, ConfigSubsection, ConfigSelection, ConfigSubList, getConfigListEntry, KEY_LEFT, KEY_RIGHT, KEY_OK
from Components.ConfigList import ConfigList
from Components.ScrollLabel import ScrollLabel
from Components.MenuList import MenuList
from Components.Sources.StaticText import StaticText
from Components.Sources.List import List
from Components.Pixmap import MultiPixmap
from Components.Sources.Progress import Progress
from Components.About import about
from Tools.BoundFunction import boundFunction
from Tools.LoadPixmap import LoadPixmap
from Tools.Directories import fileExists, resolveFilename, SCOPE_CURRENT_SKIN, SCOPE_PLUGINS
from ServiceReference import ServiceReference
from Components.PluginList import *
from Plugins.Plugin import PluginDescriptor
from Components.PluginComponent import plugins
from Components.Console import Console
from os import popen, system, listdir, remove as os_remove
from enigma import iServiceInformation, eTimer, eDVBDB, eDVBCI_UI, eListboxPythonStringContent, eListboxPythonConfigContent, gFont, loadPNG, eListboxPythonMultiContent, iServiceInformation

import os
import sys
import re
import socket
import time
import datetime


class LDBluePanel(Screen):
	skin = """
<screen name="LDBluePanel" position="center,center" size="1150,650">
<ePixmap position="700,10" zPosition="1" size="450,700" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/LDteam/images/menu/fondo.png" alphatest="blend" transparent="1" />
<widget source="global.CurrentTime" render="Label" position="35,10" size="500,24" font="Regular;22" foregroundColor="#FFFFFF" halign="left" transparent="1" zPosition="5">
		<convert type="ClockToText">>Format%H:%M:%S</convert>
	</widget>
<ePixmap position="380,10" size="310,155" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/LDteam/images/menu/ld.png" alphatest="blend" transparent="1" />
<ePixmap position="25,55" size="510,255" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/LDteam/images/menu/bp_deko.png" zPosition="1" alphatest="on" />
<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/LDteam/images/buttons/red150x30.png" position="30,590" size="150,30" alphatest="on"/>
<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/LDteam/images/buttons/green150x30.png" position="200,590" size="150,30" alphatest="on"/>
<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/LDteam/images/buttons/yellow150x30.png" position="370,590" size="150,30" alphatest="on"/>
<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/LDteam/images/buttons/blue150x30.png" position="543,590" size="150,30" alphatest="on"/>
<eLabel text="Servicios" position="30,592" zPosition="1" size="150,25" font="Regular;20" halign="center" backgroundColor="transpBlack" transparent="1"/>
<eLabel text="Plugins" position="200,592" zPosition="1" size="150,25" font="Regular;20" halign="center" backgroundColor="transpBlack" transparent="1"/>
<eLabel text="Info" position="370,592" zPosition="1" size="150,25" font="Regular;20" halign="center" backgroundColor="transpBlack" transparent="1"/>
<eLabel text="Settings" position="543,592" zPosition="1" size="150,25" font="Regular;20" halign="center" backgroundColor="transpBlack" transparent="1"/>
<widget name="lab1" position="195,43" size="230,25" font="Regular;20" zPosition="2" backgroundColor="transpBlack" transparent="1" />
<widget name="lab2" position="195,73" size="190,25" font="Regular;20" zPosition="2" backgroundColor="transpBlack" transparent="1" />
<widget name="list" position="35,116" size="320,25" zPosition="2" scrollbarMode="showOnDemand" foregroundColor="#BDBDBD" backgroundColor="transpBlack" transparent="1"/>
<widget name="lab3" position="35,149" size="120,25" font="Regular;20" halign="left" zPosition="2" backgroundColor="transpBlack" transparent="1" />
<eLabel text="CAM Activa:" position="35,149" size="245,25" font="Regular;20" halign="left" zPosition="2" foregroundColor="white" backgroundColor="transpBlack" transparent="1"/>
<widget name="activecam" position="166,149" size="245,25" font="Regular;20" halign="left" zPosition="2" backgroundColor="transpBlack" transparent="1" />
<widget name="Ilab1" position="35,183" size="340,25" font="Regular;20" zPosition="2" backgroundColor="transpBlack" transparent="1" />
<widget name="Ilab2" position="35,208" size="340,25" font="Regular;20" zPosition="2" backgroundColor="transpBlack" transparent="1" />
<widget name="Ilab3" position="35,233" size="340,25" font="Regular;20" zPosition="2" backgroundColor="transpBlack" transparent="1" />
<widget name="Ilab4" position="35,258" size="340,25" font="Regular;20" zPosition="2" backgroundColor="transpBlack" transparent="1" />
<widget name="Ecmtext" position="40,293" size="505,380" font="Regular;18" halign="left" zPosition="2" backgroundColor="transpBlack" transparent="1" />

 </screen>"""
	def __init__(self, session):
		Screen.__init__(self, session)

		self["lab1"] = Label()
		self["lab2"] = Label(_("Set Default CAM"))
		self["lab3"] = Label()
		self["Ilab1"] = Label()
		self["Ilab2"] = Label()
		self["Ilab3"] = Label()
		self["Ilab4"] = Label()
		self["activecam"] = Label()
		self["Ecmtext"] = ScrollLabel()

		self["actions"] = ActionMap(["ColorActions", "OkCancelActions", "DirectionActions"],
		{
			"ok": self.keyOk,
			"cancel": self.close,
			"green": self.keyGreen,
			"red": self.keyRed,
			"yellow": self.keyYellow,
			"blue": self.keyBlue,
			"up": self["Ecmtext"].pageUp,
			"down": self["Ecmtext"].pageDown
		}, -1)

		self.emlist = []
		self.populate_List()
		self["list"] = MenuList(self.emlist)
		self["lab1"].setText("%d  CAMs Instalada" % (len(self.emlist)))
		self.onShow.append(self.updateBP)

	def populate_List(self):
		self.camnames = {}
		cams = listdir("/usr/camscript")
		for fil in cams:
			if fil.find('Ncam_') != -1:
				f = open("/usr/camscript/" + fil,'r')
				for line in f.readlines():
					line = line.strip()
					if line.find('CAMNAME=') != -1:
						name = line[9:-1]
						self.emlist.append(name)
						self.camnames[name] = "/usr/camscript/" + fil
				f.close()

	def updateBP(self):
		try:
			name = ServiceReference(self.session.nav.getCurrentlyPlayingServiceReference()).getServiceName()
			sinfo = self.session.nav.getCurrentService().info()
			provider = self.getServiceInfoValue(iServiceInformation.sProvider, sinfo)
			wide = self.getServiceInfoValue(iServiceInformation.sAspect, sinfo)
			width = sinfo and sinfo.getInfo(iServiceInformation.sVideoWidth) or -1
			height = sinfo and sinfo.getInfo(iServiceInformation.sVideoHeight) or -1
			videosize = "%dx%d" %(width, height)
			aspect = "16:9"
			if aspect in ( 1, 2, 5, 6, 9, 0xA, 0xD, 0xE ):
				aspect = "4:3"
		except:
			name = "N/A"; provider = "N/A"; aspect = "N/A"; videosize  = "N/A"

		self["Ilab1"].setText(_("Name: ") + name)
		self["Ilab2"].setText(_("Provider: ") + provider)
		self["Ilab3"].setText(_("Aspect Ratio: ") + aspect)
		self["Ilab4"].setText(_("Videosize: ") + videosize)

		self.defaultcam = "/usr/camscript/Ncam_Ci.sh"
		if fileExists("/etc/LdCamConf"):
			f = open("/etc/LdCamConf",'r')
			for line in f.readlines():
   				parts = line.strip().split("|")
				if parts[0] == "deldefault":
					self.defaultcam = parts[1]
			f.close()

		self.defCamname =  "Common Interface"
		for c in self.camnames.keys():
			if self.camnames[c] == self.defaultcam:
				self.defCamname = c
		pos = 0
		for x in self.emlist:
			if x == self.defCamname:
				self["list"].moveToIndex(pos)
				break
			pos += 1

		mytext = "";
		if fileExists("/tmp/ecm.info"):
			f = open("/tmp/ecm.info",'r')
 			for line in f.readlines():
				mytext = mytext + line.strip() + "\n"
 			f.close()
		if len(mytext) < 5:
			mytext = "\n\n    " + _("Ecm info not available.")

		self["activecam"].setText(self.defCamname)
		self["Ecmtext"].setText(mytext)


	def getServiceInfoValue(self, what, myserviceinfo):
		v = myserviceinfo.getInfo(what)
		if v == -2:
			v = myserviceinfo.getInfoString(what)
		elif v == -1:
			v = "N/A"
		return v


	def keyOk(self):
		self.sel = self["list"].getCurrent()
		self.newcam = self.camnames[self.sel]

		out = open("/etc/LdCamConf",'w')
		out.write("deldefault|" + self.newcam + "\n")
		out.close()

		out = open("/etc/CurrentLdCamName", "w")
		out.write(self.sel)
		out.close()
		cmd = "cp -f " + self.newcam + " /usr/bin/StartLdCam"
		system (cmd)
		cmd = "STOP_CAMD," + self.defaultcam
		self.sendtoLd_sock(cmd)
		self.session.openWithCallback(self.keyOk2, startstopCam, self.defCamname, _("Stopping"))

	def keyOk2(self):
		os.system("/usr/bin/StartLdCam stop")
		cmd = "NEW_CAMD," + self.newcam
		self.sendtoLd_sock(cmd)
		oldcam = self.camnames[self.sel]
		self.session.openWithCallback(self.myclose, startstopCam, self.sel, _("Starting"))


	def sendtoLd_sock(self, data):
		client_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
		client_socket.connect("/tmp/OpenLD.socket")
		client_socket.send(data)
		client_socket.close()

	def keyBlue(self):
		from LdSet import LDSettings
		self.session.open(LDSettings)

	def keyGreen(self):
		from Plugins.Extensions.LDteam.LdPlugin import LDPluginPanel
		self.session.open(LDPluginPanel)

	def keyRed(self):
		from LdServ import LDServices
		self.session.open(LDServices)

	def keyYellow(self):
		from LdAbout import LdsysInfo
		self.session.open(LdsysInfo)

	def myclose(self):
		self.close()


class startstopCam(Screen):
	skin = """
	<screen position="center,center" size="360,200">
		<widget name="lab1" position="10,10" halign="center" size="340,180" zPosition="1" font="Regular;20" valign="center" backgroundColor="transpBlack" transparent="1"/>
	</screen>"""

	def __init__(self, session, name, what):
		Screen.__init__(self, session)

		msg = _("Please wait ") + "%s\n %s ..." % (what, name)
		self["connect"] = MultiPixmap()
		self["lab1"] = Label(msg)
		self.delay = 800
		if what == _("Starting"):
			self.delay= 3000

		self.activityTimer = eTimer()
		self.activityTimer.timeout.get().append(self.end)
		self.onShow.append(self.startShow)

	def startShow(self):
		self.activityTimer.start(self.delay)

	def end(self):
		self.activityTimer.stop()
		del self.activityTimer
		self.close()


class LDBp:
	def __init__(self):
		self["LDBp"] = ActionMap( [ "InfobarExtensions" ],
			{
				"LDBpshow": (self.showLDBp),
			})

	def showLDBp(self):
		self.session.openWithCallback(self.callNabAction, LDBluePanel)

	def callNabAction(self, *args):
		if len(args):
			(actionmap, context, action) = args
			actionmap.action(context, action)
