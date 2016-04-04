from Components.MenuList import MenuList
from Components.Label import Label
from Components.ActionMap import NumberActionMap
from Components.Pixmap import Pixmap
from Components.FileList import FileList
from Components.ActionMap import ActionMap
from Components.config import config
from Screens.Screen import Screen
from Screens.ChoiceBox import ChoiceBox
from Screens.MessageBox import MessageBox
from Screens.Standby import TryQuitMainloop
from Screens.Console import Console
from os import system


class Ipkuninstall(Screen):
	skin = """
		<screen name="Ipkuninstall" position="center,center" size="900,600" title="IPK Uninstall Tool" >
			<widget name="list" position="50,50" size="800,500" scrollbarMode="showOnDemand" />
			<widget name="info" position="150,10" zPosition="4" size="500,20" font="Regular;22" foregroundColor="#ffffff" transparent="1" halign="left" valign="center" />
		</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		self.skin = Ipkuninstall.skin
		title = "IPK Uninstall Tool"
		self.setTitle(title)
		self["list"] = MenuList([])
		self["info"] = Label()
		self["actions"] = ActionMap(["OkCancelActions"], {"ok": self.okClicked, "cancel": self.close}, -1)
		txt = _("Please select ipk to uninstall.")
		self["info"].setText(txt)
		self.onShown.append(self.startSession)

	def startSession(self):
		self.ipklist = []
		cmd = 'opkg list_installed > /tmp/ipkdb'
		system(cmd)
		out_lines = []
		out_lines = open('/tmp/ipkdb').readlines()
		for filename in out_lines:
			self.ipklist.append(filename[:-1])

		self['list'].setList(self.ipklist)

	def okClicked(self):
		ires = self["list"].getSelectionIndex()
		if ires != None:
			self.ipk = self.ipklist[ires]
			n1 = self.ipk.find("_", 0)
			self.ipk = self.ipk[:n1]
			self.session.openWithCallback(self.test, ChoiceBox, title="Select method?", list=[(_("Remove"), "rem"), (_("Force Remove"), "force")])
		else:
			return

	def test(self, answer):
		cmd = " "
		title = " "
		if answer[1] == "rem":
			cmd = "opkg remove " + self.ipk
			title = _("Removing ipk %s" %(self.ipk))
		elif answer[1] == "force":
			cmd = "opkg remove --force-depends " + self.ipk
			title = _("Force Removing ipk %s" %(self.ipk))
		self.session.open(Console,_(title),[cmd])
		self.close()
