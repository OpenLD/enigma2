# -*- coding: utf-8 -*-
from Screens.Screen import Screen
from Screens.Standby import TryQuitMainloop
from Screens.MessageBox import MessageBox
from Components.ActionMap import NumberActionMap
from Components.Pixmap import Pixmap
from Components.Sources.StaticText import StaticText
from Components.MenuList import MenuList
from Components.config import config, configfile
from Tools.Directories import resolveFilename, SCOPE_ACTIVE_SKIN
from enigma import eEnv, ePicLoad
import os

class SkinSelectorBase:
	def __init__(self, session, args = None):
		self.skinlist = []
		self.previewPath = ""
		if self.SKINXML and os.path.exists(os.path.join(self.root, self.SKINXML)):
			self.skinlist.append(self.DEFAULTSKIN)
		if self.PICONSKINXML and os.path.exists(os.path.join(self.root, self.PICONSKINXML)):
			self.skinlist.append(self.PICONDEFAULTSKIN)
		if self.PICON1SKINXML and os.path.exists(os.path.join(self.root, self.PICON1SKINXML)):
			self.skinlist.append(self.PICON1DEFAULTSKIN)
		if self.PICON2SKINXML and os.path.exists(os.path.join(self.root, self.PICON2SKINXML)):
			self.skinlist.append(self.PICON2DEFAULTSKIN)
		if self.PICON3SKINXML and os.path.exists(os.path.join(self.root, self.PICON3SKINXML)):
			self.skinlist.append(self.PICON3DEFAULTSKIN)
		if self.PICON4SKINXML and os.path.exists(os.path.join(self.root, self.PICON4SKINXML)):
			self.skinlist.append(self.PICON4DEFAULTSKIN)
		if self.PICON5SKINXML and os.path.exists(os.path.join(self.root, self.PICON5SKINXML)):
			self.skinlist.append(self.PICON5DEFAULTSKIN)
		if self.PICON6SKINXML and os.path.exists(os.path.join(self.root, self.PICON6SKINXML)):
			self.skinlist.append(self.PICON6DEFAULTSKIN)
		if self.PICON7SKINXML and os.path.exists(os.path.join(self.root, self.PICON7SKINXML)):
			self.skinlist.append(self.PICON7DEFAULTSKIN)
		if self.PICON8SKINXML and os.path.exists(os.path.join(self.root, self.PICON8SKINXML)):
			self.skinlist.append(self.PICON8DEFAULTSKIN)
		for root, dirs, files in os.walk(self.root, followlinks=True):
			for subdir in dirs:
				dir = os.path.join(root,subdir)
				if os.path.exists(os.path.join(dir,self.SKINXML)):
					self.skinlist.append(subdir)
			dirs = []

		self["key_red"] = StaticText(_("Close"))
		self["key_green"] = StaticText(_("Save"))
		self["introduction"] = StaticText(_("Press OK to activate the selected skin."))
		self["SkinList"] = MenuList(self.skinlist)
		self["Preview"] = Pixmap()
		self.skinlist.sort()

		self["actions"] = NumberActionMap(["SetupActions", "DirectionActions", "TimerEditActions", "ColorActions"],
		{
			"ok": self.ok,
			"cancel": self.close,
			"red": self.close,
			"green": self.ok,
			"up": self.up,
			"down": self.down,
			"left": self.left,
			"right": self.right,
			"log": self.info,
		}, -1)

		self.picload = ePicLoad()
		self.picload.PictureData.get().append(self.showPic)

		self.onLayoutFinish.append(self.layoutFinished)

	def showPic(self, picInfo=""):
		ptr = self.picload.getData()
		if ptr is not None:
			self["Preview"].instance.setPixmap(ptr.__deref__())
			self["Preview"].show()

	def layoutFinished(self):
		self.picload.setPara((self["Preview"].instance.size().width(), self["Preview"].instance.size().height(), 0, 0, 1, 1, "#00000000"))
		tmp = self.config.value.find("/"+self.SKINXML)
		if tmp != -1:
			tmp = self.config.value[:tmp]
			idx = 0
			for skin in self.skinlist:
				if skin == tmp:
					break
				idx += 1
			if idx < len(self.skinlist):
				self["SkinList"].moveToIndex(idx)
		self.loadPreview()

	def ok(self):
		if self["SkinList"].getCurrent() == self.DEFAULTSKIN:
			skinfile = ""
			skinfile = os.path.join(skinfile, self.SKINXML)
		elif self["SkinList"].getCurrent() == self.PICONDEFAULTSKIN:
			skinfile = ""
			skinfile = os.path.join(skinfile, self.PICONSKINXML)
		elif self["SkinList"].getCurrent() == self.PICON1DEFAULTSKIN:
			skinfile = ""
			skinfile = os.path.join(skinfile, self.PICON1SKINXML)
		elif self["SkinList"].getCurrent() == self.PICON2DEFAULTSKIN:
			skinfile = ""
			skinfile = os.path.join(skinfile, self.PICON2SKINXML)
		elif self["SkinList"].getCurrent() == self.PICON3DEFAULTSKIN:
			skinfile = ""
			skinfile = os.path.join(skinfile, self.PICON3SKINXML)
		elif self["SkinList"].getCurrent() == self.PICON4DEFAULTSKIN:
			skinfile = ""
			skinfile = os.path.join(skinfile, self.PICON4SKINXML)
		elif self["SkinList"].getCurrent() == self.PICON5DEFAULTSKIN:
			skinfile = ""
			skinfile = os.path.join(skinfile, self.PICON5SKINXML)
		elif self["SkinList"].getCurrent() == self.PICON6DEFAULTSKIN:
			skinfile = ""
			skinfile = os.path.join(skinfile, self.PICON6SKINXML)
		elif self["SkinList"].getCurrent() == self.PICON7DEFAULTSKIN:
			skinfile = ""
			skinfile = os.path.join(skinfile, self.PICON7SKINXML)
		elif self["SkinList"].getCurrent() == self.PICON8DEFAULTSKIN:
			skinfile = ""
			skinfile = os.path.join(skinfile, self.PICON8SKINXML)
		else:
			skinfile = self["SkinList"].getCurrent()
			skinfile = os.path.join(skinfile, self.SKINXML)

		print "Skinselector: Selected Skin: "+self.root+skinfile
		self.config.value = skinfile
		self.config.save()
		configfile.save()
		restartbox = self.session.openWithCallback(self.restartGUI,MessageBox,_("GUI needs a restart to apply a new skin\nDo you want to restart the GUI now?"), MessageBox.TYPE_YESNO)
		restartbox.setTitle(_("Restart GUI now?"))

	def up(self):
		self["SkinList"].up()
		self.loadPreview()

	def down(self):
		self["SkinList"].down()
		self.loadPreview()

	def left(self):
		self["SkinList"].pageUp()
		self.loadPreview()

	def right(self):
		self["SkinList"].pageDown()
		self.loadPreview()

	def info(self):
		aboutbox = self.session.open(MessageBox,_("Enigma2 skin selector"), MessageBox.TYPE_INFO)
		aboutbox.setTitle(_("About..."))

	def loadPreview(self):
		if self["SkinList"].getCurrent() == self.DEFAULTSKIN:
			pngpath = "."
			pngpath = os.path.join(os.path.join(self.root, pngpath), "prev.png")
		elif self["SkinList"].getCurrent() == self.PICONDEFAULTSKIN:
			pngpath = "."
			pngpath = os.path.join(os.path.join(self.root, pngpath), "piconprev.png")
		elif self["SkinList"].getCurrent() == self.PICON1DEFAULTSKIN:
			pngpath = "."
			pngpath = os.path.join(os.path.join(self.root, pngpath), "picon1prev.png")
		elif self["SkinList"].getCurrent() == self.PICON2DEFAULTSKIN:
			pngpath = "."
			pngpath = os.path.join(os.path.join(self.root, pngpath), "picon2prev.png")
		elif self["SkinList"].getCurrent() == self.PICON3DEFAULTSKIN:
			pngpath = "."
			pngpath = os.path.join(os.path.join(self.root, pngpath), "picon3prev.png")
		elif self["SkinList"].getCurrent() == self.PICON4DEFAULTSKIN:
			pngpath = "."
			pngpath = os.path.join(os.path.join(self.root, pngpath), "picon4prev.png")
		elif self["SkinList"].getCurrent() == self.PICON5DEFAULTSKIN:
			pngpath = "."
			pngpath = os.path.join(os.path.join(self.root, pngpath), "picon5prev.png")
		elif self["SkinList"].getCurrent() == self.PICON6DEFAULTSKIN:
			pngpath = "."
			pngpath = os.path.join(os.path.join(self.root, pngpath), "picon6prev.png")
		elif self["SkinList"].getCurrent() == self.PICON7DEFAULTSKIN:
			pngpath = "."
			pngpath = os.path.join(os.path.join(self.root, pngpath), "picon7prev.png")
		elif self["SkinList"].getCurrent() == self.PICON8DEFAULTSKIN:
			pngpath = "."
			pngpath = os.path.join(os.path.join(self.root, pngpath), "picon8prev.png")
		else:
			pngpath = self["SkinList"].getCurrent()
			pngpath = os.path.join(os.path.join(self.root, pngpath), "prev.png")

		if not os.path.exists(pngpath):
			pngpath = resolveFilename(SCOPE_ACTIVE_SKIN, "noprev.png")

		if self.previewPath != pngpath:
			self.previewPath = pngpath

		self.picload.startDecode(self.previewPath)

	def restartGUI(self, answer):
		if answer is True:
			self.session.open(TryQuitMainloop, 3)

class SkinSelector(Screen, SkinSelectorBase):
	SKINXML = "skin.xml"
	DEFAULTSKIN = "< Default >"
	PICONSKINXML = None
	PICONDEFAULTSKIN = None
	PICON1SKINXML = None
	PICON1DEFAULTSKIN = None
	PICON2SKINXML = None
	PICON2DEFAULTSKIN = None
	PICON3SKINXML = None
	PICON3DEFAULTSKIN = None
	PICON4SKINXML = None
	PICON4DEFAULTSKIN = None
	PICON5SKINXML = None
	PICON5DEFAULTSKIN = None
	PICON6SKINXML = None
	PICON6DEFAULTSKIN = None
	PICON7SKINXML = None
	PICON7DEFAULTSKIN = None
	PICON8SKINXML = None
	PICON8DEFAULTSKIN = None

	skinlist = []
	root = os.path.join(eEnv.resolve("${datadir}"),"enigma2")

	def __init__(self, session, args = None):
		Screen.__init__(self, session)
		SkinSelectorBase.__init__(self, args)
		Screen.setTitle(self, _("Skin setup"))
		self.skinName = "SkinSelector"
		self.config = config.skin.primary_skin

class LcdSkinSelector(Screen, SkinSelectorBase):
	SKINXML = "skin_display.xml"
	DEFAULTSKIN = "< Default >"
	PICONSKINXML = "skin_display_picon.xml"
	PICONDEFAULTSKIN = "< Default with Picon >"
	PICON1SKINXML = "skin_display_picon1.xml"
	PICON1DEFAULTSKIN = "< Skin picon A >"
	PICON2SKINXML = "skin_display_picon2.xml"
	PICON2DEFAULTSKIN = "< Skin picon B >"
	PICON3SKINXML = "skin_display_picon3.xml"
	PICON3DEFAULTSKIN = "< Skin picon C >"
	PICON4SKINXML = "skin_display_picon4.xml"
	PICON4DEFAULTSKIN = "< Skin picon D >"
	PICON5SKINXML = "skin_display5.xml"
	PICON5DEFAULTSKIN = "< Skin modelo E >"
	PICON6SKINXML = "skin_display6.xml"
	PICON6DEFAULTSKIN = "< Skin modelo F >"
	PICON7SKINXML = "skin_display7.xml"
	PICON7DEFAULTSKIN = "< Skin modelo H >"
	PICON8SKINXML = "skin_display8.xml"
	PICON8DEFAULTSKIN = "< Skin modelo I >"

	skinlist = []
	root = os.path.join(eEnv.resolve("${datadir}"),"enigma2/display/")

	def __init__(self, session, args = None):
		Screen.__init__(self, session)
		SkinSelectorBase.__init__(self, args)
		Screen.setTitle(self, _("Skin setup"))
		self.skinName = "SkinSelector"
		self.config = config.skin.display_skin
