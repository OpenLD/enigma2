#!/usr/bin/env python
# -*- coding: UTF-8 -*-
##
##
## Copyright (c) 2012-2017 OpenLD
##        Javier Sayago <admin@lonasdigital.com>
## Contact: javilonas@esp-desarrolladores.com
##
## Licensed under the Apache License, Version 2.0 (the "License");
## you may not use this file except in compliance with the License.
## You may obtain a copy of the License at
##
## http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.
##
##########################################################################

from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.ChoiceBox import ChoiceBox
from Components.config import config, configfile, ConfigYesNo, ConfigSubsection
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.Harddisk import harddiskmanager, getProcMounts
from Components.Console import Console
from Components.Sources.StaticText import StaticText
from Tools.Directories import fileExists, resolveFilename, SCOPE_PLUGINS, SCOPE_ACTIVE_SKIN
import sys, commands, gettext, subprocess, threading, sys, traceback, time, datetime
from os import system, stat as mystat, path, remove, rename
from glob import glob
import stat

from enigma import eTimer

config.plugins.ldteam = ConfigSubsection()
config.plugins.ldteam.swapautostart = ConfigYesNo(default=False)

startswap = None


def SwapAutostart(reason, session=None, **kwargs):
	global startswap
	if reason == 0:
		if config.plugins.ldteam.swapautostart.value:
			print "[SwapManager] autostart"
			startswap = StartSwap()
			startswap.start()


class StartSwap:
	def __init__(self):
		self.Console = Console()

	def start(self):
		self.Console.ePopen("sfdisk -l | grep swap", self.startSwap2)

	def startSwap2(self, result=None, retval=None, extra_args=None):
		swap_place = ""
		if result and result.find('sd') != -1 or result.find('mmcblk') != -1:
			for line in result.split('\n'):
				if line.find('sd') != -1 or line.find('mmcblk') != -1:
					parts = line.strip().split()
					swap_place = parts[0]
					tmpfile = file('/etc/fstab.tmp', 'w')
					fstabfile = file('/etc/fstab')
					tmpfile.writelines([l for l in fstabfile.readlines() if swap_place not in l])
					rename('/etc/fstab.tmp', '/etc/fstab')
					tmpfile.close()
					fstabfile.close()
					print "[SwapManager] Found a swap partition:", swap_place
		else:
			devicelist = []
			for p in harddiskmanager.getMountedPartitions():
				d = path.normpath(p.mountpoint)
				if path.exists(p.mountpoint) and p.mountpoint != "/" and not p.mountpoint.startswith('/media/net'):
					devicelist.append((p.description, d))
			if len(devicelist):
				for device in devicelist:
					for filename in glob(device[1] + '/swap*'):
						if path.exists(filename):
							swap_place = filename
							print "[SwapManager] Found a swapfile on ", swap_place

		f = file('/proc/swaps')
		swapfile = f.read()
		if swapfile.find(swap_place) == -1:
			print "[SwapManager] Starting swapfile on ", swap_place
			system('swapon ' + swap_place)
		else:
			print "[SwapManager] Swapfile is already active on ", swap_place
		f.close()

class Swap(Screen):
	skin = """
	<screen name="Swap" position="center,center" size="560,450" title="Swap File Manager" flags="wfBorder" >
		<ePixmap pixmap="skin_default/buttons/red.png" position="0,0" size="140,40" alphatest="on" />
		<ePixmap pixmap="skin_default/buttons/green.png" position="140,0" size="140,40" alphatest="on" />
		<ePixmap pixmap="skin_default/buttons/yellow.png" position="280,0" size="140,40" alphatest="on" />
		<ePixmap pixmap="skin_default/buttons/blue.png" position="420,0" size="140,40" alphatest="on" />
		<widget name="key_red" position="0,0" zPosition="1" size="140,40" font="Regular;18" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
		<widget name="key_green" position="140,0" zPosition="1" size="140,40" font="Regular;18" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />
		<widget name="key_yellow" position="280,0" zPosition="1" size="140,40" font="Regular;18" halign="center" valign="center" backgroundColor="#a08500" transparent="1" />
		<widget name="autostart_off" position="10,50" zPosition="1" pixmap="skin_default/icons/lock_off.png" size="32,32" alphatest="on" />
		<widget name="autostart_on" position="10,50" zPosition="2" pixmap="skin_default/icons/lock_on.png" size="32,32" alphatest="on" />
		<widget name="lab1" position="50,50" size="360,30" font="Regular;18" valign="center" transparent="1"/>
		<widget name="lab2" position="10,100" size="150,30" font="Regular;18" valign="center" transparent="1"/>
		<widget name="lab3" position="10,150" size="150,30" font="Regular;18" valign="center" transparent="1"/>
		<widget name="lab4" position="10,200" size="150,30" font="Regular;18" valign="center" transparent="1"/>
		<widget name="lab5" position="10,290" size="400,150" font="Regular;18" valign="center" transparent="1"/>
		<widget name="labplace" position="160,100" size="220,30" font="Regular;18" valign="center" backgroundColor="#4D5375"/>
		<widget name="labsize" position="160,150" size="220,30" font="Regular;18" valign="center" backgroundColor="#4D5375"/>
		<widget name="inactive" position="160,200" size="100,30" font="Regular;18" valign="center" halign="center" backgroundColor="red"/>
		<widget name="active" position="160,200" size="100,30" font="Regular;18" valign="center" halign="center" backgroundColor="green"/>
	</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		Screen.setTitle(self, _("Swap Manager"))

		self['lab1'] = Label()
		self['autostart_on'] = Pixmap()
		self['autostart_off'] = Pixmap()
		self['lab2'] = Label(_("Swap Place:"))
		self['labplace'] = Label()
		self['lab3'] = Label(_("Swap Size:"))
		self['labsize'] = Label()
		self['lab4'] = Label(_("Status:"))
		self['lab5'] = Label(_('Swap status: disabled'))
		self['inactive'] = Label(_("Inactive"))
		self['active'] = Label(_("Active"))
		self['key_red'] = Label(_("Create"))
		self['key_green'] = Label(_("Activate"))
		self['key_blue'] = Label()
		self['key_yellow'] = Label(_("Autostart"))
		self['swapname_summary'] = StaticText()
		self['swapactive_summary'] = StaticText()
		self.Console = Console()
		self.swap_place = ''
		self.new_place = ''
		self.creatingswap = False
		self.swap_active = False
		self['actions'] = ActionMap(['WizardActions', 'ColorActions', "MenuActions"], {'back': self.close, 'green': self.actDeact, 'yellow': self.autoSsWap, 'red': self.createDel, "menu": self.close})
		self.activityTimer = eTimer()
		self.activityTimer.timeout.get().append(self.getSwapDevice)
		self.onLayoutFinish.append(self.updateSwap)

	def updateSwap(self, result=None, retval=None, extra_args=None):
		self["actions"].setEnabled(False)
		self.swap_active = False
		self.swap_place = None
		self['autostart_on'].hide()
		self['autostart_off'].show()
		self['active'].hide()
		self['inactive'].show()
		self['labplace'].hide()
		self['labsize'].hide()
		self['swapactive_summary'].setText(_("Current Status:"))
		scanning = _("Wait please while scanning...")
		self['lab1'].setText(scanning)
		rc = system('cat /proc/swaps > /tmp/swapdevices.tmp')
		self.swap_place = ''
		swapinfo = _('Swap status: disabled')
		f = open('/proc/swaps', 'r')
		for line in f.readlines():
			if line.find('swapfile') != -1:
				parts = line.split()
				self.swap_place = parts[0].strip()
				self.swapsize = int(parts[2].strip())
				swapinfo = _('Swap status: active\nSwap file: %s \nSwap size: %d Kb \nSwap used: %s Kb') % (self.swap_place, self.swapsize, parts[3].strip())

		f.close()
		self['lab5'].setText(swapinfo)
		self.activityTimer.start(10)

	def getSwapDevice(self):
		self.activityTimer.stop()
		if path.exists('/etc/rcS.d/S98SwapManager'):
			remove('/etc/rcS.d/S98SwapManager')
			config.plugins.ldteam.swapautostart.value = True
			config.plugins.ldteam.swapautostart.save()
		if path.exists('/tmp/swapdevices.tmp'):
			remove('/tmp/swapdevices.tmp')
		self.Console.ePopen("sfdisk -l | grep swap", self.updateSwap2)

	def updateSwap2(self, result=None, retval=None, extra_args=None):
		self.swapsize = 0
		self.swap_place = ''
		self.swap_active = False
		self.device = False

		if result.find('sd') > 0 or result.find('mmcblk') > 0:
			self['key_red'].setText("")
			for line in result.split('\n'):
				if line.find('sd') > 0 or line.find('mmcblk') > 0:
					parts = line.strip().split()
					self.swap_place = parts[0]
					if self.swap_place == 'sfdisk:':
						self.swap_place = ''
					self.device = True
				f = open('/proc/swaps', 'r')
				for line2 in f.readlines():
					parts = line.strip().split()
					if line2.find('partition') != -1:
						self.swap_active = True
						self.swapsize = parts[2]
						continue
				f.close()
		else:
			self['key_red'].setText(_("Create"))
			devicelist = []
			for p in harddiskmanager.getMountedPartitions():
				d = path.normpath(p.mountpoint)
				if path.exists(p.mountpoint) and p.mountpoint != "/" and not p.mountpoint.startswith('/media/net'):
					devicelist.append((p.description, d))
			if len(devicelist):
				for device in devicelist:
					for filename in glob(device[1] + '/swap*'):
						self.swap_place = filename
						self['key_red'].setText(_("Delete"))
						info = mystat(self.swap_place)
						self.swapsize = info[stat.ST_SIZE]
						continue

		if config.plugins.ldteam.swapautostart.value and self.swap_place:
			self['autostart_off'].hide()
			self['autostart_on'].show()
		else:
			config.plugins.ldteam.swapautostart.setValue(False)
			config.plugins.ldteam.swapautostart.save()
			configfile.save()
			self['autostart_on'].hide()
			self['autostart_off'].show()
		self['labplace'].setText(self.swap_place)
		self['labplace'].show()

		f = open('/proc/swaps', 'r')
		for line in f.readlines():
			parts = line.strip().split()
			if line.find('partition') != -1:
				self.swap_active = True
				continue
			elif line.find('file') != -1:
				self.swap_active = True
				continue
		f.close()

		if self.swapsize > 0:
			if self.swapsize >= 1024:
				self.swapsize = int(self.swapsize) / 1024
				if self.swapsize >= 1024:
					self.swapsize = int(self.swapsize) / 1024
				self.swapsize = str(self.swapsize) + ' ' + 'MB'
			else:
				self.swapsize = str(self.swapsize) + ' ' + 'KB'
		else:
			self.swapsize = ''

		self['labsize'].setText(self.swapsize)
		self['labsize'].show()

		if self.swap_active:
			self['inactive'].hide()
			self['active'].show()
			self['key_green'].setText(_("Deactivate"))
			self['swapactive_summary'].setText(_("Current Status:") + ' ' + _("Active"))
		else:
			self['inactive'].show()
			self['active'].hide()
			self['key_green'].setText(_("Activate"))
			self['swapactive_summary'].setText(_("Current Status:") + ' ' + _("Inactive"))

		scanning = _("Enable Swap at startup")
		self['lab1'].setText(scanning)
		self['lab1'].show()
		self["actions"].setEnabled(True)

		name = self['labplace'].text
		self['swapname_summary'].setText(name)

	def actDeact(self):
		if self.swap_active:
			self.Console.ePopen('swapoff ' + self.swap_place, self.updateSwap)
		else:
			if not self.device:
				if self.swap_place != '':
					self.Console.ePopen('swapon ' + self.swap_place, self.updateSwap)
				else:
					mybox = self.session.open(MessageBox, _("Swap File not found. You have to create the file before to activate."), MessageBox.TYPE_INFO)
					mybox.setTitle(_("Info"))
			else:
				self.Console.ePopen('swapon ' + self.swap_place, self.updateSwap)

	def createDel(self):
		if not self.device:
			if self.swap_place != '':
				if self.swap_active:
					self.Console.ePopen('swapoff ' + self.swap_place, self.createDel2)
				else:
					self.createDel2(None, 0)
			else:
				self.doCreateSwap()

	def createDel2(self, result, retval, extra_args=None):
		if retval == 0:
			remove(self.swap_place)
			if config.plugins.ldteam.swapautostart.value:
				config.plugins.ldteam.swapautostart.setValue(False)
				config.plugins.ldteam.swapautostart.save()
				configfile.save()
			self.updateSwap()

	def doCreateSwap(self):
		parts = []
		supported_filesystems = frozenset(('ext4', 'ext3', 'ext2', 'vfat'))
		candidates = []
		mounts = getProcMounts()
		for partition in harddiskmanager.getMountedPartitions(False, mounts):
			if partition.filesystem(mounts) in supported_filesystems:
				candidates.append((partition.description, partition.mountpoint))
		if len(candidates):
			self.session.openWithCallback(self.doCSplace, ChoiceBox, title=_("Please select device to use as swapfile location"), list=candidates)
		else:
			self.session.open(MessageBox, _("Sorry, no physical devices that supports SWAP attached. Can't create Swapfile on network or fat32 filesystems"), MessageBox.TYPE_INFO, timeout=10)

	def doCSplace(self, name):
		if name:
			self.new_place = name[1]
			myoptions = [[_("8 Mb"), '8196'], [_("16 Mb"), '16388'], [_("32 Mb"), '32772'], [_("64 MB"), '65540'], [_("96 MB"), '98308'], [_("128 MB"), '131076'], [_("256 MB"), '262148'], [_("512 MB"), '524292'], [_("1024 MB"), '1048580'], [_("1256 MB"), '1286148'], [_("1512 MB"), '1548292'], [_("1536 Mb"), '1572868'], [_("2048 MB"), '2097156']]
			self.session.openWithCallback(self.doCSsize, ChoiceBox, title=_("Select the Swap File Size:"), list=myoptions)

	def doCSsize(self, swapsize):
		if swapsize:
			self["actions"].setEnabled(False)
			scanning = _("Wait please while creating swapfile...")
			self['lab1'].setText(scanning)
			self['lab1'].show()
			swapsize = swapsize[1]
			myfile = self.new_place + 'swapfile'
			self.commands = []
			self.commands.append('dd if=/dev/zero of=' + myfile + ' bs=1024 count=' + swapsize + ' 2>/dev/null')
			self.commands.append('chown root:root ' + myfile + ' 2>/dev/null')
			self.commands.append('chmod 0600 ' + myfile + ' 2>/dev/null')
			self.commands.append('mkswap ' + myfile + ' 2>/dev/null')
			self.commands.append('swapon ' + myfile + ' 2>/dev/null')
			self.Console.eBatch(self.commands, self.updateSwap, debug=True)

	def autoSsWap(self):
		if self.swap_place:
			if config.plugins.ldteam.swapautostart.value:
				config.plugins.ldteam.swapautostart.setValue(False)
				if fileExists('/etc/init.d/SwapManager'):
					if fileExists('/etc/rc3.d/S98SwapManager'):
						commands.getstatusoutput('update-rc.d -f SwapManager remove')
					commands.getstatusoutput('sh /etc/init.d/SwapManager stop')
				config.plugins.ldteam.swapautostart.save()
			else:
				config.plugins.ldteam.swapautostart.setValue(True)
				if fileExists('/etc/init.d/SwapManager'):
					if not fileExists('/etc/rc3.d/S98SwapManager'):
						commands.getstatusoutput('update-rc.d -f SwapManager defaults 98')
					commands.getstatusoutput('sh /etc/init.d/SwapManager start')
				config.plugins.ldteam.swapautostart.save()
			configfile.save()
		else:
			mybox = self.session.open(MessageBox, _("You have to create a Swap File before activating autostart"), MessageBox.TYPE_INFO)
			mybox.setTitle(_("Info"))
		self.updateSwap()
