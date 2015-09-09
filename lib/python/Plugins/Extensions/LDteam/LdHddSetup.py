# for localized messages

from enigma import *
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.Sources.List import List
from Tools.Directories import resolveFilename, SCOPE_CURRENT_PLUGIN
from Tools.LoadPixmap import LoadPixmap
from Components.Button import Button
from Components.Label import Label
from Screens.MessageBox import MessageBox
from Screens.Standby import TryQuitMainloop
from Plugins.Extensions.LDteam.LdHddPartitions import HddPartitions
from Plugins.Extensions.LDteam.LdHddInfo import HddInfo

from Plugins.Extensions.LDteam.LdDisks import Disks
from Plugins.Extensions.LDteam.ExtraMessageBox import ExtraMessageBox
from Plugins.Extensions.LDteam.ExtraActionBox import ExtraActionBox
from Plugins.Extensions.LDteam.LdMountPoints import MountPoints
from boxbranding import getMachineBrand, getMachineName

import os
import sys

def DiskEntry(model, size, removable):
	if removable:
		picture = LoadPixmap(cached = True, path = resolveFilename(SCOPE_CURRENT_PLUGIN, "/usr/lib/enigma2/python/Plugins/Extensions/LDteam/images/icons/diskusb.png"));
	else:
		picture = LoadPixmap(cached = True, path = resolveFilename(SCOPE_CURRENT_PLUGIN, "/usr/lib/enigma2/python/Plugins/Extensions/LDteam/images/icons/disk.png"));

	return (picture, model, size)

class HddSetup(Screen):
	skin = """
				<screen name="HddSetup" position="center,center" size="800,560" title="OpenLD - Hard Drive Setup">
			<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/LDteam/images/buttons/red150x30.png" position="55,510" size="150,30" alphatest="on"/>
<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/LDteam/images/buttons/green150x30.png" position="235,510" size="150,30" alphatest="on"/>
<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/LDteam/images/buttons/yellow150x30.png" position="415,510" size="150,30" alphatest="on"/>
<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/LDteam/images/buttons/blue150x30.png" position="595,510" size="150,30" alphatest="on"/>
<widget name="key_red" position="55,512" zPosition="1" size="150,25" font="Regular;20" halign="center" backgroundColor="transpBlack" transparent="1"/>
<widget name="key_green" position="235,512" zPosition="1" size="150,25" font="Regular;20" halign="center" backgroundColor="transpBlack" transparent="1"/>
<widget name="key_yellow" position="415,512" zPosition="1" size="150,25" font="Regular;20" halign="center" backgroundColor="transpBlack" transparent="1"/>
<widget name="key_blue" position="595,512" zPosition="1" size="150,25" font="Regular;20" halign="center" backgroundColor="transpBlack" transparent="1"/>
			<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/LDteam/images/menu/div-h.png" position="10,0" size="780,2" alphatest="on" />
			<widget source="menu" render="Listbox" position="10,10" size="780,510" scrollbarMode="showOnDemand" backgroundColor="transpBlack" transparent="1">
			<convert type="TemplatedMultiContent">
				{"template": [
					MultiContentEntryPixmapAlphaTest(pos = (5, 0), size = (48, 48), png = 0),
					MultiContentEntryText(pos = (65, 10), size = (330, 38), font=0, flags = RT_HALIGN_LEFT|RT_VALIGN_TOP, text = 1),
					MultiContentEntryText(pos = (405, 10), size = (125, 38), font=0, flags = RT_HALIGN_LEFT|RT_VALIGN_TOP, text = 2),
					],
					"fonts": [gFont("Regular", 22)],
					"itemHeight": 50
				}
			</convert>
		</widget>
	</screen>"""

	def __init__(self, session, args = 0):
		self.session = session

		Screen.__init__(self, session)
		self.disks = list ()

		self.mdisks = Disks()
		for disk in self.mdisks.disks:
			capacity = "%d MB" % (disk[1] / (1024 * 1024))
			self.disks.append(DiskEntry(disk[3], capacity, disk[2]))

		self["menu"] = List(self.disks)
		self["key_red"] = Button(_("Mounts"))
		self["key_green"] = Button(_("Info"))
		self["key_yellow"] = Button(_("Initialize"))
		self["key_blue"] = Button(_("Exit"))
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
		{
			"blue": self.quit,
			"yellow": self.yellow,
			"green": self.green,
			"red": self.red,
			"cancel": self.quit,
		}, -2)

		self.onShown.append(self.setWindowTitle)

	def setWindowTitle(self):
		self.setTitle(_("OpenLD - Format/Mount HDD"))

	def isExt4Supported(self):
		return "ext4" in open("/proc/filesystems").read()

	def mkfs(self):
		self.formatted += 1
		return self.mdisks.mkfs(self.mdisks.disks[self.sindex][0], self.formatted, self.fsresult)

	def refresh(self):
		self.disks = list ()

		self.mdisks = Disks()
		for disk in self.mdisks.disks:
			capacity = "%d MB" % (disk[1] / (1024 * 1024))
			self.disks.append(DiskEntry(disk[3], capacity, disk[2]))

		self["menu"].setList(self.disks)

	def checkDefault(self):
		mp = MountPoints()
		mp.read()
		if not mp.exist("/media/hdd"):
			mp.add(self.mdisks.disks[self.sindex][0], 1, "/media/hdd")
			mp.write()
			mp.mount(self.mdisks.disks[self.sindex][0], 1, "/media/hdd")
			os.system("/bin/mkdir -p /media/hdd/movie")

			message = _("Fixed mounted first initialized Storage Device to /media/hdd. It needs a system restart in order to take effect.\nRestart your %s %s now?") % (getMachineBrand(), getMachineName())
			mbox = self.session.openWithCallback(self.restartBox, MessageBox, message, MessageBox.TYPE_YESNO)
			mbox.setTitle(_("Restart %s %s") % (getMachineBrand(), getMachineName()))

	def restartBox(self, answer):
		if answer is True:
			self.session.open(TryQuitMainloop, 2)

	def format(self, result):
		if result != 0:
			self.session.open(MessageBox, _("Cannot format partition %d") % (self.formatted), MessageBox.TYPE_ERROR)
		if self.result == 0:
			if self.formatted > 0:
				self.checkDefault()
				self.refresh()
				return
		elif self.result > 0 and self.result < 3:
			if self.formatted > 1:
				self.checkDefault()
				self.refresh()
				return
		elif self.result == 3:
			if self.formatted > 2:
				self.checkDefault()
				self.refresh()
				return
		elif self.result == 4:
			if self.formatted > 3:
				self.checkDefault()
				self.refresh()
				return

		self.session.openWithCallback(self.format, ExtraActionBox, _("Formatting partition %d") % (self.formatted + 1), _("Initialize disk"), self.mkfs)

	def fdiskEnded(self, result):
		if result == 0:
			self.format(0)
		elif result == -1:
			self.session.open(MessageBox, _("Cannot umount current device.\nA record in progress, timeshift or some external tools (like samba, swapfile and nfsd) may cause this problem.\nPlease stop this actions/applications and try again"), MessageBox.TYPE_ERROR)
		else:
			self.session.open(MessageBox, _("Partitioning failed!"), MessageBox.TYPE_ERROR)

	def fdisk(self):
		return self.mdisks.fdisk(self.mdisks.disks[self.sindex][0], self.mdisks.disks[self.sindex][1], self.result, self.fsresult)

	def initialaze(self, result):
		if not self.isExt4Supported():
			result += 1

		if result != 4:
			self.fsresult = result
			self.formatted = 0
			mp = MountPoints()
			mp.read()
			mp.deleteDisk(self.mdisks.disks[self.sindex][0])
			mp.write()
			self.session.openWithCallback(self.fdiskEnded, ExtraActionBox, _("Partitioning..."), _("Initialize disk"), self.fdisk)

	def chooseFSType(self, result):
		if result != 5:
			self.result = result
			if self.isExt4Supported():
				self.session.openWithCallback(self.initialaze, ExtraMessageBox, _("Format as"), _("Partitioner"),
											[ [ "Ext4", "partitionmanager.png" ],
											[ "Ext3", "partitionmanager.png" ],
											[ "NTFS", "partitionmanager.png" ],
											[ "Fat32", "partitionmanager.png" ],
											[ _("Cancel"), "cancel.png" ],
											], 1, 4)
			else:
				self.session.openWithCallback(self.initialaze, ExtraMessageBox, _("Format as"), _("Partitioner"),
											[ [ "Ext3", "partitionmanager.png" ],
											[ "NTFS", "partitionmanager.png" ],
											[ "Fat32", "partitionmanager.png" ],
											[ _("Cancel"), "cancel.png" ],
											], 1, 3)

	def yellow(self):
		if len(self.mdisks.disks) > 0:
			self.sindex = self['menu'].getIndex()
			self.session.openWithCallback(self.chooseFSType, ExtraMessageBox, _("Please select your preferred configuration."), _("Partitioner"),
										[ [ _("One partition"), "partitionmanager.png" ],
										[ _("Two partitions (50% - 50%)"), "partitionmanager.png" ],
										[ _("Two partitions (75% - 25%)"), "partitionmanager.png" ],
										[ _("Three partitions (33% - 33% - 33%)"), "partitionmanager.png" ],
										[ _("Four partitions (25% - 25% - 25% - 25%)"), "partitionmanager.png" ],
										[ _("Cancel"), "cancel.png" ],
										], 1, 5)

	def green(self):
		if len(self.mdisks.disks) > 0:
			self.sindex = self['menu'].getIndex()
			self.session.open(HddInfo, self.mdisks.disks[self.sindex][0])

	def red(self):
		if len(self.mdisks.disks) > 0:
			self.sindex = self['menu'].getIndex()
			if len(self.mdisks.disks[self.sindex][5]) == 0:
				self.session.open(MessageBox, _("You need to initialize your storage device first"), MessageBox.TYPE_ERROR)
			else:
				self.session.open(HddPartitions, self.mdisks.disks[self.sindex])

	def quit(self):
		self.close()
