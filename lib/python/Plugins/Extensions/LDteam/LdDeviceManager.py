#!/usr/bin/env python
# -*- coding: UTF-8 -*-
##
##
## Copyright (c) 2012-2015 OpenLD
##          Javier Sayago <admin@lonasdigital.com>
## Contact: javilonas@esp-desarrolladores.com
##
## Licensed under the Apache License, Version 2.0 (the "License");
## you may not use this file except in compliance with the License.
## You may obtain a copy of the License at
##
##    http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.
##
##########################################################################
from Components.Label import Label
from Components.ActionMap import ActionMap
from Components.config import config, ConfigSelection, getConfigListEntry, ConfigSubsection, ConfigEnableDisable, ConfigYesNo, ConfigInteger
from Components.ConfigList import ConfigListScreen
from Components.Console import Console
from Components.GUIComponent import GUIComponent
from Components.Harddisk import harddiskmanager
from Components.MenuList import MenuList
from Components.Pixmap import Pixmap, MultiPixmap
from Components.Sources.List import List
from Components.Sources.StaticText import StaticText
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Tools.BoundFunction import boundFunction
from Tools.LoadPixmap import LoadPixmap
from Tools.Notifications import AddNotificationWithCallback
from Tools.Directories import pathExists, fileExists, resolveFilename, SCOPE_PLUGINS, SCOPE_CURRENT_PLUGIN, SCOPE_CURRENT_SKIN, SCOPE_METADIR
from skin import loadSkin
from os import system, makedirs, path, listdir, statvfs, popen
import os
import re
import time

from Components.Sources.StaticText import StaticText
from Components.FileList import FileList
from Screens.InputBox import InputBox
from Components.Input import Input
from Screens.ChoiceBox import ChoiceBox
from enigma import eTimer

config.plugins.devicemanager = ConfigSubsection()
config.plugins.devicemanager.hotplug_enable = ConfigEnableDisable(default=True)
config.plugins.devicemanager.mountcheck_enable = ConfigEnableDisable(default=True)

def readFile(filename):
	file = open(filename)
	data = file.read().strip()
	file.close()
	return data

def byteConversion(byte):
	if type(byte) == str and len(byte) == 0:
		return ""
	if type(byte) != long:
		byte = long(byte)
	if byte > 1024*1024*1024:
		int_part = byte/1024/1024/1024
		dec_part = byte%(1024*1024*1024)/(1024*1024)
		return "%d.%d GB"%(int_part, dec_part)
	else:
		int_part = byte/1024/1024
		dec_part = byte%(1024*1024)/1024
		return "%d.%d MB"%(int_part, dec_part)

def checkStrValue(value , empty = ""):
	if type(value) != str or len(value) == 0:
		return empty
	return value

class DeviceManagerConfiguration(Screen, ConfigListScreen):
	def __init__(self,session):
		self.session = session
		Screen.__init__(self,session)
		self.skinName = "Setup"
		self.createConfigList()
		ConfigListScreen.__init__(self, self.list, session = self.session)
		self["key_red"] = StaticText(_("Cancel"))
		self["key_green"] = StaticText(_("OK"))
		self["shortcuts"] = ActionMap(["ShortcutActions", "SetupActions" ],
		{
			"ok": self.keySave,
			"cancel": self.keyCancel,
			"red": self.keyCancel,
			"green": self.keySave,
		}, -2)
		self.onShown.append(self.setWindowTitle)
		self.old_hotplug_enable = config.plugins.devicemanager.hotplug_enable.value

	def setWindowTitle(self):
		self.setTitle(_("DeviceManager configuration"))

	def createConfigList(self):
		self.list = []
		self.list.append(getConfigListEntry(_("Enable mount check for HDD : "), config.plugins.devicemanager.mountcheck_enable))
		self.list.append(getConfigListEntry(_("Harddisk standby after : "), config.usage.hdd_standby))
		self.list.append(getConfigListEntry(_("Mount known devices automatically : "), config.plugins.devicemanager.hotplug_enable))

	def keySave(self):
		if config.plugins.devicemanager.hotplug_enable.value:
			if not DeviceManagerhotplugDeviceStart in harddiskmanager.on_partition_list_change:
				harddiskmanager.on_partition_list_change.append(DeviceManagerhotplugDeviceStart)
		else:
			if DeviceManagerhotplugDeviceStart in harddiskmanager.on_partition_list_change:
				harddiskmanager.on_partition_list_change.remove(DeviceManagerhotplugDeviceStart)

		for x in self["config"].list:
			x[1].save()
		self.close()

class DeviceManager(Screen):
	skin = """
				<screen name="DeviceManager" position="center,center" size="800,560" title="OpenLD - Format/Mount HDD">
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
				{"templates":
					{"default": (54,[
							MultiContentEntryText(pos = (100, 0), size = (560, 30), font=0, flags = RT_HALIGN_LEFT|RT_VALIGN_CENTER, text = 0), # index 0 is vendor  - model
							MultiContentEntryText(pos = (100, 32), size = (130, 20), font=1, flags = RT_HALIGN_LEFT|RT_VALIGN_CENTER, text = 1), # index 1 is Device
							MultiContentEntryText(pos = (230, 32), size = (130, 20), font=1, flags = RT_HALIGN_LEFT|RT_VALIGN_CENTER, text = 2), # index 2 is Size
							MultiContentEntryText(pos = (360, 32), size = (130, 20), font=1, flags = RT_HALIGN_LEFT|RT_VALIGN_CENTER, text = 3), # index 3 is Partitions
							MultiContentEntryText(pos = (490, 32), size = (140, 20), font=1, flags = RT_HALIGN_LEFT|RT_VALIGN_CENTER, text = 4), # index 4 is Removable
							MultiContentEntryPixmapAlphaTest(pos = (0, 52), size = (670, 2), png = 5), # png 5 is the div pixmap
						]),
					"partitions": (98, [
							MultiContentEntryText(pos = (100, 0), size = (560, 30), font=0, flags = RT_HALIGN_LEFT|RT_VALIGN_CENTER, text = 0), # index 1 is Partition
							MultiContentEntryText(pos = (100, 32), size = (560, 20), font=1, flags = RT_HALIGN_LEFT|RT_VALIGN_CENTER, text = 1), # index 2 is Mounted on
							MultiContentEntryText(pos = (100, 54), size = (560, 20), font=1, flags = RT_HALIGN_LEFT|RT_VALIGN_CENTER, text = 2), # index 3 UUID
							MultiContentEntryText(pos = (100, 76), size = (140, 20), font=1, flags = RT_HALIGN_LEFT|RT_VALIGN_CENTER, text = 3), # index 4 Type
							MultiContentEntryText(pos = (230, 76), size = (140, 20), font=1, flags = RT_HALIGN_LEFT|RT_VALIGN_CENTER, text = 4), # index 5 Size_total
							MultiContentEntryText(pos = (380, 76), size = (200, 20), font=1, flags = RT_HALIGN_LEFT|RT_VALIGN_CENTER, text = 5), # index 6 Size_free
							MultiContentEntryPixmapAlphaTest(pos = (0, 96), size = (670, 2), png = 6), # png 6 is the div pixmap
						]),
					"mountpoint": (54,[
							MultiContentEntryPixmapAlphaTest(pos = (10, 7), size = (30, 30), png = 0), # index 0: picture
							MultiContentEntryText(pos = (40, 0), size = (500, 30), font=0, flags = RT_HALIGN_LEFT|RT_VALIGN_CENTER, text = 1), # index 1 name
							MultiContentEntryText(pos = (40, 32), size = (500, 20), font=1, flags = RT_HALIGN_LEFT|RT_VALIGN_CENTER, text = 2), # index 2 path
							MultiContentEntryPixmapAlphaTest(pos = (0, 52), size = (670, 2), png = 5), # index 5 is the div pixmap
						])
					},
					"fonts": [gFont("Regular", 22),gFont("Regular", 16),gFont("Regular", 28)],
					"itemHeight": 54
				}
				</convert>
			</widget>
		</screen>
		"""

	def __init__(self, session):
		Screen.__init__(self, session)
		self.session = session
		self.currList = "default"
		self.currDevice = None
		self.currPartition = None
		self.defaultMountPoint = "/media/hdd"
		self.deviceList = []
		self["menu"] = List(self.deviceList)
		self["key_red"] = Label(_("Close"))
		self["key_green"] = Label(" ")
		self["key_yellow"] = Label(" ")
		self["key_blue"] = Label(" ")

		self["shortcuts"] = ActionMap(["ShortcutActions", "SetupActions", "MenuActions" ],
		{
			"ok": self.keyOk,
			"cancel": self.keyCancel,
			"red": self.keyCancel,
			"green": self.keyOk,
			"yellow": self.keyYellow,
			"blue": self.keyBlue,
			"menu": self.keyMenu,
		}, -2)
		self.DeviceManagerConsole = Console()
		self.loadIcon()
		if not self.selectionChanged in self["menu"].onSelectionChanged:
			self["menu"].onSelectionChanged.append(self.selectionChanged)
		self.onLayoutFinish.append(self.showDeviceList)
		self.onLayoutFinish.append(self.addPartitionListChange)
		self.onClose.append(self.removePartitionListChange)
		self.onChangedEntry = []
		self.blockDevices = {}

	def addPartitionListChange(self):
		harddiskmanager.on_partition_list_change.append(self.partitionListChanged)

	def removePartitionListChange(self):
		harddiskmanager.on_partition_list_change.remove(self.partitionListChanged)

	def partitionListChanged(self, action, device):
		print "[Device manager] hotplug partitionListChanged"
		if self.currList != "default" and device.device[:3] != self.currDevice["blockdev"]:
			return
		self.showDeviceList()

	def loadIcon(self):
		self.icon_button_green = LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, "/usr/lib/enigma2/python/Plugins/Extensions/LDteam/images/buttons/button_green.png"))
		self.divpng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, "/usr/lib/enigma2/python/Plugins/Extensions/LDteam/images/menu/div-h.png"))

	def selectionChanged(self):
		if self.currList == "partitions":
			currentPartition = self.getCurrentPartition()
			if currentPartition is not None:
				if currentPartition["mountpoint"] != "":
					self["key_green"].setText(_("Umount"))
				else:
					self["key_green"].setText(_("Mount"))

				if currentPartition["fstype"] == "":
					self["key_blue"].setText("")
				elif currentPartition["fstype"][:3] == "ext":
					self["key_blue"].setText(_("Check"))
				else:
					self["key_blue"].setText("")

	def showDeviceList(self):
		self.deviceList = []
		self["key_red"].setText(_("Close"))
		self["key_green"].setText(_("Ok"))
		self["key_yellow"].setText(" ")
		self["key_blue"].setText(_("Initialize"))
		deviceinfo.refresh()
		for device in deviceinfo.getBlockDevices():
			deviceEntry = (
				"%s - %s"%(device["vendor"], device["model"]), # vendor : str, model : str, index 0
				_("device : %s")%(device["blockdev"]), # str
				_("Size : %s")%(byteConversion(device["size"])), # str, bytes
				_("Partitions : %s")%(len(device["partitions"])), # list
				_("Removable : %s")%(device["removable"] and 'Yes' or 'No'), # bool [True, False]
				self.divpng, # png 5
				device, # index 6
				)
#			print "[DeviceManager] deviceEntry : ", deviceEntry
			self.deviceList.append(deviceEntry)
		self.currList = "default"
		self["menu"].style = "default"
		self["menu"].setList(self.deviceList)

	def showPartitionList(self):
		if self.currDevice is None:
			return
		partitionList = []
		for partition in self.currDevice["partitions"]:
			partitionInfo = deviceinfo.getPartitionInfo(partition)
			partitionEntry = (
				_("Partition : /dev/%s")%partition, # index 0
				_("Mounted on : %s")%checkStrValue(partitionInfo["mountpoint"], _("not mounted")),
				_("UUID : %s")%checkStrValue(partitionInfo["uuid"], _("unknown")),
				_("Type : %s")%checkStrValue(partitionInfo["fstype"], _("unknown")),
				_("Size : %s")%checkStrValue(byteConversion(partitionInfo["size"]), _("unknown")),
				_("Free : %s")%checkStrValue(byteConversion(partitionInfo["free"]), _("unknown")),
				self.divpng, # index 6
				partitionInfo, # index 7
			)
#			print "[DeviceManager] partitionEntry : ",partitionEntry
			partitionList.append(partitionEntry)
		if len(partitionList) != 0:
			self["key_red"].setText(_("Devices"))
			self["key_green"].setText(_("Mount"))
			self["key_yellow"].setText(_("Format"))
			self["key_blue"].setText(_("Check"))
			self.currList = "partitions"
			self["menu"].style = "partitions"
			self["menu"].setList(partitionList)
			self.selectionChanged()
		else:
			self.session.open(MessageBox, _("No partition list found on device.\nPlease click BLUE key and do Initialize to use this device."), MessageBox.TYPE_ERROR, timeout = 10)

	def showMountPointSetup(self):
		if self.currDevice is None or self.currPartition is None:
			return
		partition =  self.currPartition["partition"]
		if not os.access("/autofs/%s"%partition,0):
			self.session.open(MessageBox, _("This partition is not mountable.\nYou need to check or format this partition."), MessageBox.TYPE_ERROR, timeout = 10)
			return
		self["key_red"].setText(_("Partitions"))
		self["key_green"].setText(_("Ok"))
		self["key_yellow"].setText("")
		self["key_blue"].setText("")
		self.mountPointList = []
		currentMountPoint = self.currPartition["mountpoint"]
		if currentMountPoint == "":
			currentMountPoint = "'not mounted'"
		defaultMountPoint = self.getDefaultMountPoint()
		autoMountPoint = self.getAutoMountPoint()
		defaultMountPointEntry = (self.icon_button_green, _("Set up Default Mount Point"), _("Mount Point : %s ->%s")%(currentMountPoint, defaultMountPoint), "default", defaultMountPoint, self.divpng)
		autoMountPointEntry = (self.icon_button_green, _("Automatically set up a Mount Point"), _("Mount Point : %s -> %s")%(currentMountPoint, autoMountPoint), "auto", autoMountPoint, self.divpng)
		manuallyMountPointEntry = (self.icon_button_green, _("User manually Set up a Mount Point"), _("Mount Point : click ok button on here."), "manual", "", self.divpng)
		if not path.ismount(defaultMountPoint):
			self.mountPointList.append(defaultMountPointEntry)
		self.mountPointList.append(autoMountPointEntry)
		self.mountPointList.append(manuallyMountPointEntry)
		self.currList = "mountpoint"
		self["menu"].style = "mountpoint"
		self["menu"].setList(self.mountPointList)

	def getCurrentDevice(self):
		try:
			return self["menu"].getCurrent()[6]
		except:
			return None

	def getCurrentPartition(self):
		try:
			return self["menu"].getCurrent()[7]
		except:
			return None

	def keyOk(self):
#		print "keyOk"
		if self.currList == "default":
			self.currDevice = self.getCurrentDevice()
			if self.currDevice is not None:
				if len(self.currDevice["partitions"]) == 0:
					self.session.open(MessageBox, _("No partition list found on device.\nPlease click BLUE key and do Initialize to use this device."), MessageBox.TYPE_ERROR, timeout = 10)
				else:
					self.showPartitionList()
			else:
				self.session.open(MessageBox, _("Device not found."), MessageBox.TYPE_ERROR, timeout = 10)
		elif self.currList == "partitions":
			currentPartition = self.getCurrentPartition()
			if currentPartition is not None:
				currMountPoint = currentPartition["mountpoint"]
				currUuid = currentPartition["uuid"]
				if currMountPoint == "":
					self.currPartition = currentPartition
					self.showMountPointSetup()
				else:
					self.doUmount(currMountPoint, self.showPartitionList)
			else:
				self.session.open(MessageBox, _("Partition info is not found."), MessageBox.TYPE_ERROR, timeout = 10)
		elif self.currList == "mountpoint":
# self["menu"].getCurrent() : (green_button, "menu description", "mount point description, "default", mountpoint, self.divpng)
			currEntry = self["menu"].getCurrent()[3]
			if currEntry == "default":
#				print "Setup mountpoint default!"
				self.doMount(self.currPartition, self["menu"].getCurrent()[4])
			elif currEntry == "auto":
#				print "Setup mountpoint automatically!"
				self.doMount(self.currPartition, self["menu"].getCurrent()[4])
			else:
#				print "Setup mountpoint manually!"
				self.session.openWithCallback(self.MountpointBrowserCB, MountpointBrowser)
		else:
			pass

	def keyCancel(self):
#		print "keyCancel"
		if self.DeviceManagerConsole is not None:
			if len(self.DeviceManagerConsole.appContainers):
				for name in self.DeviceManagerConsole.appContainers.keys():
					self.DeviceManagerConsole.kill(name)
		if self.currList == "partitions":
			self.currDevice = None
			self.showDeviceList()
		elif self.currList == "mountpoint":
			self.currPartition = None
			self.showPartitionList()
		else: # currList = "default"
			self.close()

	def keyYellow(self):
		if self.currList == "partitions":
			self.choiceBoxFstype()

	def keyBlue(self):
		if self.currList == "default":
			device = self.getCurrentDevice()
			if device is not None:
				self.session.openWithCallback(self.deviceInitCB, DeviceInit, device["blockdev"], device["size"])
			else:
				self.session.open(MessageBox, _("Device not found."), MessageBox.TYPE_ERROR, timeout = 10)
		elif self.currList == "partitions":
			partition = self.getCurrentPartition()
			if partition is not None:
				self.session.openWithCallback(self.deviceCheckCB, DeviceCheck, partition)
			else:
				self.session.open(MessageBox, _("Partition info is not found."), MessageBox.TYPE_ERROR, timeout = 10)

	def keyMenu(self):
		self.session.open(DeviceManagerConfiguration)

	def deviceInitCB(self, ret = True):
		self.showDeviceList()

	def deviceCheckCB(self, ret = True):
		self.showPartitionList()

	def deviceFormatCB(self, ret = True):
		self.showPartitionList()

	def choiceBoxFstype(self):
		menu = []
		menu.append((_("ext2 - recommended for USB flash memory"), "ext2"))
		menu.append((_("ext3 - recommended for harddisks"), "ext3"))
		menu.append((_("ext4 - experimental"), "ext4"))
		menu.append((_("vfat - for USB flash memory"), "vfat"))
		self.session.openWithCallback(self.choiceBoxFstypeCB, ChoiceBox, title=_("Choice filesystem."), list=menu)

	def choiceBoxFstypeCB(self, choice):
		if choice is None:
			return
		else:
			partition = self.getCurrentPartition()
			if partition is not None:
				self.session.openWithCallback(self.deviceFormatCB, DeviceFormat, partition, choice[1])
			else:
				self.session.open(MessageBox, _("Partition info is not found."), MessageBox.TYPE_ERROR, timeout = 10)

# about mount funcs..
	def doUmount(self, mountpoint, callback):
		cmd = "umount %s"%mountpoint
		print "[DeviceManager] cmd : %s"%cmd
		os.system(cmd)
		if not path.ismount(mountpoint):
			devicemanagerconfig.updateConfigList()
		else:
			self.session.open(MessageBox, _("Can't umount %s. \nMaybe device or resource busy.")%mountpoint, MessageBox.TYPE_ERROR, timeout = 10)
		callback()

	def getDefaultMountPoint(self):
		return self.defaultMountPoint

	def getAutoMountPoint(self):
		mountPoint = "/media/"+self.currDevice["model"]
		mountPoint = mountPoint.replace(' ','-')
		if path.ismount(mountPoint):
			partnum = 2
			while 1:
				mountPoint_fix = mountPoint+str(partnum)
				if not path.ismount(mountPoint_fix):
					break
				partnum +=1
			mountPoint = mountPoint_fix
		return mountPoint

	def doMount(self, partition, mountpoint):
		try:
# check mountpoint is in partition list.
			if mountpoint != self.getDefaultMountPoint():
				for p in harddiskmanager.partitions:
					if p.mountpoint == mountpoint:
						self.session.open(MessageBox, _("Can not use this mount point.(%s) \nPlease select another mount point.")%mountpoint, MessageBox.TYPE_ERROR, timeout = 10)
						return
#
			device = partition["partition"]
			filesystem = partition["fstype"]
			uuid = partition["uuid"]
			if mountpoint.endswith("/"):
				mountpoint = retval[:-1]
			if mountpoint.find(' ') != -1:
				mountpoint = mountpoint.replace(' ','-')
			devpath = "/dev/"+device
			if deviceinfo.isMounted(devpath, mountpoint):
				print "[DeviceManager] '%s -> %s' is already mounted."%(devpath, mountpoint)
				return

# check current device mounted on another mountpoint.
			mp_list = deviceinfo.checkMountDev(devpath)
			for mp in mp_list:
				if mp != mountpoint and path.ismount(mp):
					deviceinfo.umountByMountpoint(mp)
# check another device mounted on configmountpoint
			devpath_list = deviceinfo.checkMountPoint(mountpoint)
			for devpath_ in devpath_list:
				if devpath_ != devpath:
					self.session.open(MessageBox, _("Mount Failed!\nCurrent path is already mounted by \"%s\"")%devpath_list[0], MessageBox.TYPE_ERROR, timeout = 10)
					return
# do mount
			print "[DeviceManagerHotplugDevice] doMount"
			if not path.exists(mountpoint):
				os.system("mkdir %s"%mountpoint)
			if path.exists(mountpoint):
				if not path.ismount(mountpoint):
					if filesystem == "ntfs":
						cmd = "ntfs-3g %s %s"%(devpath, mountpoint)
					elif filesystem is None:
						cmd = "mount %s %s"%(devpath, mountpoint)
					else:
						cmd = "mount -t %s %s %s"%(filesystem, devpath, mountpoint)
					print "[DeviceManager] cmd : %s"%cmd
					self.DeviceManagerConsole.ePopen(cmd, self.doMountFinished, (devpath, mountpoint) )
		except:
			self.session.open(MessageBox, _("Mount Failed!\n(%s -> %s)")%(device, mountpoint), MessageBox.TYPE_ERROR, timeout = 10)

	def doMountFinished(self, result, retval, extra_args = None):
		(devpath, mountpoint) = extra_args
		if retval == 0:
			if not deviceinfo.isMounted(devpath, mountpoint):
#				print "[DeviceManager] %s doMount failed!"%devpath
				self.session.open(MessageBox, _("Mount Failed!\n(%s -> %s)")%(devpath, mountpoint), MessageBox.TYPE_ERROR, timeout = 10)
				return
			else:
# make movie directory
				if mountpoint == "/media/hdd":
					movieDir = mountpoint + "/movie"
					if not pathExists(movieDir):
						print "[DeviceManager] make dir %s"%movieDir
						os.makedirs(movieDir)
				self.showPartitionList()
# update current mount state ,devicemanager.cfg
				devicemanagerconfig.updateConfigList()

	def MountpointBrowserCB(self, retval = None):
		if retval and retval is not None:
			mountPoint = retval.strip().replace(' ','')
			if retval.endswith("/"):
				mountPoint = retval[:-1]
			print "Mount point from MountpointBrowser : %s"%mountPoint
			if not path.exists(mountPoint):
				self.session.open(MessageBox, _("Mount Point is not writeable.\nPath : %s")%mountPoint, MessageBox.TYPE_ERROR, timeout = 10)

			else:
				self.doMount(self.currPartition, mountPoint)
# mount funcs end..

# Initializing Start...
class DeviceInit(Screen):
	skin = """<screen position="0,0" size="0,0"/>"""
	def __init__(self, session, device, devicesize):
		Screen.__init__(self, session)
		self.session = session
		self.deviceInitConsole = Console()
		self.device = device
		self.devicesize = int(devicesize)
		self.inputbox_partitions = 1
		self.inputbox_partitionSizeList = []
		self.inputbox_partitionSizeTotal = int(self.devicesize/1024/1024)
		self.msgWaiting = None
		self.msgWaitingMkfs = None
		self.devicenumber = 0
		self.newpartitions = 0
		self.onLayoutFinish.append(self.timerStart)
		self.initStartTimer = eTimer()
		self.initStartTimer.callback.append(self.confirmMessage)
		self.createFSStartTimer = eTimer()
		self.createFSStartTimer.callback.append(self.createFilesystemStart)
		self.exitMessageTimer = eTimer()
		self.exitMessageTimer.callback.append(self.exitMessage)
		self.msg = ""
		self.fstype = None
		self.mkfs_cmd = ""
		self.doMkfsTimer = eTimer()
		self.doMkfsTimer.callback.append(self.doMkfs)
		self.doInitializeTimer = eTimer()
		self.doInitializeTimer.callback.append(self.doInitialize)

		self.partitionType = "MBR"
		self.maxPartNum = 4
		self.inputbox_partitionSizeRemain = self.inputbox_partitionSizeTotal
		self.unit = "MB"

	def timerStart(self):
		self.initStartTimer.start(100,True)

	def confirmMessage(self):
		message = _("Do you really want to initialize the device?\nAll data on the device will be lost!")
		self.session.openWithCallback(self.confirmed, MessageBox, message)

	def confirmed(self, ret):
		if ret:
			self.InitializeStart()
		else:
			self.exit()

	def exit(self, ret = True):
		self.close()

	def unmountAll(self, device):
		mounts = file('/proc/mounts').read().split('\n')
		cmd = ""
# umount all
		for line in mounts:
			if not line.startswith("/dev/" + device):
				continue
			cmd += "umount %s ;"% line.split()[0]
		print "[DeviceManager] %s"%cmd
		os.system(cmd)
#recheck if umounted
		mounts = file('/proc/mounts').read().split('\n')
		for line in mounts:
			if line.startswith("/dev/" + device):
				return False
		return True

	def InitializeStart(self):
		if self.devicesize >= ( 2.2 * 1000 * 1000 * 1000 * 1000 ): # 2.2TB
			self.partitionType = "GPT"
			self.maxPartNum = 20
			self.inputbox_partitionSizeRemain = 100
			self.unit = "%"

		self.InputPartitionSize_step1()

	def InputPartitionSize_step1(self):
		self.session.openWithCallback(self.InputPartitionSize_step1_CB, InputBox, title=_("How many partitions do you want?(1-%d)" % self.maxPartNum), text="1", maxSize=False, type=Input.NUMBER)

	def InputPartitionSize_step1_CB(self, ret):
		if ret is not None and int(ret) in range(1,self.maxPartNum+1): # MBR 1~4, GPT 1~20
			self.inputbox_partitions = int(ret)
			self.InputPartitionSize_step2()
		else:
			self.session.openWithCallback(self.exit, MessageBox, _("The number you entered is wrong!"), MessageBox.TYPE_ERROR, timeout = 10)

	def InputPartitionSize_step2(self):
		current_partition = len(self.inputbox_partitionSizeList)+1
		if self.inputbox_partitionSizeRemain == 0:
			self.choiceBoxFstype()
		elif current_partition == self.inputbox_partitions:
			self.inputbox_partitionSizeList.append(str(self.inputbox_partitionSizeRemain))
			self.choiceBoxFstype()
		else:
			text = str(int(self.inputbox_partitionSizeRemain/(self.inputbox_partitions-len(self.inputbox_partitionSizeList) )))
			self.session.openWithCallback(self.InputPartitionSize_step2_CB, InputBox, title=_("Input size of partition %s.(Unit = %s, Max = %d %s)")%(current_partition, self.unit, self.inputbox_partitionSizeRemain, self.unit), text=text, maxSize=False, type=Input.NUMBER)

	def InputPartitionSize_step2_CB(self, ret):
		if ret is not None:
			if self.inputbox_partitionSizeRemain < int(ret) or int(ret) == 0:
				self.InputPartitionSize_step2()
			else:
				self.inputbox_partitionSizeList.append(str(ret))
				self.inputbox_partitionSizeRemain -= int(ret)
				self.InputPartitionSize_step2()
		else:
			self.session.openWithCallback(self.exit ,MessageBox, _("The number you entered is wrong!"), MessageBox.TYPE_ERROR, timeout = 10)

	def choiceBoxFstype(self):
		menu = []
		menu.append((_("ext2 - recommended for USB flash memory"), "ext2"))
		menu.append((_("ext3 - recommended for harddisks"), "ext3"))
		menu.append((_("ext4 - experimental"), "ext4"))
		menu.append((_("vfat - for USB flash memory"), "vfat"))
		self.session.openWithCallback(self.choiceBoxFstypeCB, ChoiceBox, title=_("Choice filesystem."), list=menu)

	def choiceBoxFstypeCB(self, choice):
		if choice is None:
			self.exit()
		else:
			self.fstype = choice[1]
			if self.fstype not in ["ext2", "ext3", "ext4", "vfat"]:
				self.exit()
			else:
				self.initInitializeConfirm()

	def initInitializeConfirm(self):
#		print self.inputbox_partitionSizeList
		partitionsInfo = ""
		for index in range(len(self.inputbox_partitionSizeList)):
			print "partition %d : %s %s"%(index+1, str(self.inputbox_partitionSizeList[index]), self.unit)
			partitionsInfo += "partition %d : %s %s\n"%(index+1, str(self.inputbox_partitionSizeList[index]), self.unit)
		partitionsInfo += "filesystem type : %s"%(self.fstype)
		self.session.openWithCallback(self.initInitializeConfirmCB, MessageBoxConfirm, _("%s\nStart Device Inititlization?") % partitionsInfo , MessageBox.TYPE_YESNO)

	def initInitializeConfirmCB(self,ret):
		if ret:
			self.initInitialize()
		else:
			self.exit()

	def initInitialize(self):
		if not self.unmountAll(self.device):
			self.session.openWithCallback(self.exit, MessageBox, _("umounting failed!Maybe some files in mount point are open"), MessageBox.TYPE_ERROR, timeout = 10)
		else:
			msg = _("InitInitializing, please wait ...")
			msg += _("\nDevice : %s")%self.device
			msg += _("\nSize : %s MB\n")%self.inputbox_partitionSizeTotal
			for index in range(len(self.inputbox_partitionSizeList)):
				msg += _("\npartition %d : %s %s")%(index+1, str(self.inputbox_partitionSizeList[index]), self.unit)
			self.msgWaiting = self.session.openWithCallback(self.msgWaitingCB, MessageBox_2, msg, type = MessageBox.TYPE_INFO, enable_input = False)
			self.doInitializeTimer.start(500,True)

	def doInitialize(self):
		def CheckPartedVer():
			cmd = 'parted --version'
			lines = os.popen(cmd).readlines()
			for l in lines:
				if l.find("parted (GNU parted)") != -1:
					ver = l.split()[3].strip()
					break
			try:
				ver = float(ver)
			except:
				print "[CheckPartedVer] check parted version Failed!"
				return 0
			return ver

		partitions = len(self.inputbox_partitionSizeList) # get num of partition
		set = ""
		if self.partitionType == "MBR":
			if partitions == 1:
				cmd = 'printf "8,\n;0,0\n;0,0\n;0,0\ny\n" | sfdisk -f -uS /dev/' + self.device
			else:
				for p in range(4):
					if partitions > p+1:
						set += ",%s\n"%(self.inputbox_partitionSizeList[p])
					else:
						set +=";\n"
				set+="y\n"
				cmd = 'printf "%s" | sfdisk -f -uM /dev/%s'%(set,self.device)

		elif self.partitionType == "GPT": # partition type is GPT
			setAlign = ""
			partedVer = CheckPartedVer()
			if partedVer >= 2.1: # align option is supported in version 2.1 or later
				setAlign = "--align optimal"

			if partitions == 1:
				cmd = 'parted %s /dev/%s --script mklabel gpt mkpart disk ext2 0%% 100%%' % (setAlign, self.device)
			else: # has multiple partitions
				p_current = 0
				for p in range(partitions):
					if p == 0:
						p_start = p_current
						p_end = int( (long(self.inputbox_partitionSizeList[p]) * 100) / 100 )
						p_current = p_end
					elif p > 0 and partitions > (p + 1):
						p_start = p_current
						p_end = int( (long(self.inputbox_partitionSizeList[p]) * 100) / 100 )+ p_start
						p_current = p_end
					elif partitions == (p + 1):
						p_start = p_current
						p_end = 100
					if p_start == p_end:
						p_end +=1
					if p_end > 100:
						continue
					set += 'mkpart disk%d ext2 %d%% %d%% ' % (p + 1, p_start, p_end)
				cmd = 'parted %s /dev/%s --script mklabel gpt %s' % (setAlign, self.device, set)
		else:
			errorMsg = "Invalid partitioning type"
			self.msgWaiting.run_close(False, errorMsg)
			return
		self.deviceInitConsole.ePopen(cmd, self.initInitializeFinished)

	def initInitializeFinished(self, result, retval, extra_args = None):
		if retval == 0:
			if self.partitionType == "MBR":
				cmd = "sfdisk -R /dev/%s ; sleep 5" % (self.device)
			else: # is GPT
				cmd = "sleep 5"
			self.deviceInitConsole.ePopen(cmd, self.initInitializingRefreshFinished)
		else:
			errorMsg = "initInitializing device Error at /dev/%s"%self.device
			self.msgWaiting.run_close(False, errorMsg)

	def initInitializingRefreshFinished(self, result, retval, extra_args = None):
		cmd = "/bin/umount /dev/%s*" % (self.device)
		self.deviceInitConsole.ePopen(cmd, self.initInitializingUmountFinished)

	def initInitializingUmountFinished(self, result, retval, extra_args = None):
		partitions = open("/proc/partitions")
		self.devicenumber = 0
		self.newpartitions = 0
		for part in partitions:
			res = re.sub("\s+", " ", part).strip().split(" ")
			if res and len(res) == 4 and res[3][:3] == self.device:
				if len(res[3]) > 3 and res[3][:2] == "sd":
					self.newpartitions += 1
		partitions.close()
		partNum = len(self.inputbox_partitionSizeList) # get num of partition
		if self.newpartitions != partNum:
			errorMsg = "Partitioning device Error at /dev/%s"%self.device
			self.msgWaiting.run_close(False, errorMsg)
		else:
			self.msgWaiting.run_close(True)
#		self.createFilesystem(self.newpartitions)

	def createFilesystem(self, newpartitions):
		self.devicenumber = self.devicenumber + 1
		fulldevicename = "/dev/" + self.device + str(self.devicenumber)
		shortdevicename = self.device + str(self.devicenumber)
# get partition size
		partitions = open("/proc/partitions")
		for part in partitions:
			res = re.sub("\s+", " ", part).strip().split(" ")
			if res and len(res) == 4:
				if res[3] == shortdevicename:
					partitionsize = int(res[2])
					break
		partitions.close()

		if self.fstype == "ext4":
			cmd = "/sbin/mkfs.ext4 -F "
			if partitionsize > 2 * 1024 * 1024: # 2GB
				cmd += "-T largefile "
			cmd += "-O extent,flex_bg,large_file,uninit_bg -m1 " + fulldevicename
		elif self.fstype == "ext3":
			cmd = "/sbin/mkfs.ext3 -F "
			if partitionsize > 2 * 1024 * 1024:
				cmd += "-T largefile "
			cmd += "-m0 " + fulldevicename
		elif self.fstype == "ext2":
			cmd = "/sbin/mkfs.ext2 -F "
			if partitionsize > 2 * 1024 * 1024:
				cmd += "-T largefile "
			cmd += "-m0 " + fulldevicename
		elif self.fstype == "vfat":
			if partitionsize > 4 * 1024 * 1024 * 1024:
				cmd = "/usr/sbin/mkfs.vfat -I -S4096 " + fulldevicename
			else:
				cmd = "/usr/sbin/mkfs.vfat -I " + fulldevicename
		else:
			self.createFilesystemFinished(None, -1, (self.device, fulldevicename))
			return

		msg = _("Create filesystem, please wait ...")
		msg += _("\nPartition : %s") % (fulldevicename)
		msg += _("\nFilesystem : %s") % (self.fstype)
		msg += _("\nDisk Size : %s MB") % (self.inputbox_partitionSizeTotal)
		msg += _("\nPartition Size : %d %s\n") % (int(self.inputbox_partitionSizeList[self.devicenumber-1]), self.unit)
		self.msgWaitingMkfs = self.session.openWithCallback(self.msgWaitingMkfsCB, MessageBox_2, msg, type = MessageBox.TYPE_INFO, enable_input = False)
		self.mkfs_cmd = cmd
		self.doMkfsTimer.start(500,True)

	def doMkfs(self):
		fulldevicename = "/dev/" + self.device + str(self.devicenumber)
		self.deviceInitConsole.ePopen(self.mkfs_cmd, self.createFilesystemFinished, (self.device, fulldevicename))

	def createFilesystemFinished(self, result, retval, extra_args = None):
		device = extra_args[0]
		fulldevicename = extra_args[1]
		if retval == 0:
			self.msgWaitingMkfs.run_close(True)
		else:
			errorMsg = _("Creating filesystem Error")
			if fulldevicename is not None:
				errorMsg += _(" at /dev/%s")%fulldevicename
			self.msgWaitingMkfs.run_close(False, errorMsg)

	def createFilesystemStart(self):
		self.createFilesystem(self.newpartitions)

	def msgWaitingCB(self, ret, msg=""):
		if ret:
			self.createFSStartTimer.start(100,True)
		else:
			self.success = False
			self.msg = msg
			self.exitMessageTimer.start(100,True)

	def msgWaitingMkfsCB(self, ret, msg=""):
		if self.devicenumber < self.newpartitions:
			self.createFSStartTimer.start(100,True)
		else:
			if ret == True:
				self.success = True
				self.msg = _("Device Initialization finished sucessfully!")
				self.updateDeviceInfo()
				self.exitMessageTimer.start(100,True)
			else:
				self.success = False
				self.msg = msg
				self.exitMessageTimer.start(100,True)

	def exitMessage(self):
		if self.success:
			self.session.openWithCallback(self.exit, MessageBox, self.msg, MessageBox.TYPE_INFO, timeout = 10)
		else:
			self.session.openWithCallback(self.exit, MessageBox, self.msg, MessageBox.TYPE_ERROR, timeout = 10)

	def updateDeviceInfo(self):
# update devicemanager configs
		devicemanagerconfig.updateConfigList()

# Initializing end

# device check start..
class DeviceCheck(Screen):
	skin = """<screen position="0,0" size="0,0"/>"""
	def __init__(self, session, partition):
		Screen.__init__(self, session)
		self.session = session
		self.deviceCheckConsole = Console()
		self.partition = partition
		self.onLayoutFinish.append(self.timerStart)
		self.checkStartTimer = eTimer()
		self.checkStartTimer.callback.append(self.confirmMessage)
		self.umountTimer = eTimer()
		self.umountTimer.callback.append(self.doUnmount)

	def timerStart(self):
		self.checkStartTimer.start(100,True)

	def confirmMessage(self):
		fssize = self.partition["size"]
		if long(fssize) > 1024*1024*1024*16:
			message = _("Do you really want to check the filesystem?\nThis could take lots of time!")
			self.session.openWithCallback(self.confirmed, MessageBox, message)
		else:
			self.deviceCheckStart()

	def confirmed(self, ret):
		print "confirmed : ",ret
		if ret:
			self.deviceCheckStart()
		else:
			self.exit()

	def deviceCheckStart(self):
		print "deviceCheckStart "
		print "partition : ", self.partition
		device = self.partition["partition"]
		fstype = self.partition["fstype"]
		fssize = self.partition["size"]
		if device is not None and fstype.startswith("ext"):
			msg = _("Check filesystem, please wait ...")
			msg += _("\nDevice : /dev/%s")%(device)
			msg += _("\nFilesystem : %s")%(fstype)
			self.msgWaiting = self.session.openWithCallback(self.msgWaitingCB, MessageBox_2, msg, type = MessageBox.TYPE_INFO, enable_input = False)
			self.umountTimer.start(500,True)
		else:
			self.exit()

	def doUnmount(self):
		device = self.partition["partition"]
		mountpoint = self.partition["mountpoint"]
		fstype = self.partition["fstype"]
		if mountpoint != "":
			self.doUmountFsck(device, mountpoint, fstype)
		else:
			self.umountFsckFinished("NORESULT", 0, (device, mountpoint, fstype))

	def doUmountFsck(self, device, mountpoint, fstype):
		cmd = "umount /dev/%s" % device
		self.deviceCheckConsole.ePopen(cmd, self.umountFsckFinished, (device, mountpoint, fstype))

	def umountFsckFinished(self, result, retval, extra_args = None):
		device = extra_args[0]
		mountpoint = extra_args[1]
		fstype = extra_args[2]
		if retval == 0:
			cmd = "fsck." + fstype + " -f -p /dev/" + device
			self.deviceCheckConsole.ePopen(cmd, self.fsckFinished, extra_args)
		else:
			errorMsg = _("Can not umount device /dev/%s.\nMaybe some files of the filesystem are open")%device
			self.msgWaiting.run_close(False,errorMsg)

	def fsckFinished(self, result, retval, extra_args = None):
		device = extra_args[0]
		mountpoint = extra_args[1]
		if retval == 0:
			text = _("Filesystem check finished sucessfully")
			self.msgWaiting.run_close(True, text)
		else:
			text = _("Error checking disk. The disk or filesystem may be damaged")
			self.msgWaiting.run_close(False, text)

	def msgWaitingCB(self, ret, msg):
		if ret:
			self.session.open(MessageBox, msg, MessageBox.TYPE_INFO, timeout = 10)
		else:
			self.session.open(MessageBox, msg, MessageBox.TYPE_ERROR, timeout = 10)

		partition = self.partition["partition"]
		mountpoint = self.partition["mountpoint"]
		fstype = self.partition["fstype"]
		if mountpoint != "":
			if fstype == "ntfs":
				cmd = "ntfs-3g /dev/" + partition + " " + mountpoint
			else:
				cmd = "mount /dev/" + partition + " " + mountpoint
			self.deviceCheckConsole.ePopen(cmd, self.mountPartitionFinished)
		else:
			self.exit()

	def mountPartitionFinished(self, result, retval, extra_args = None):
		self.exit()

	def exit(self):
		self.close()

#device check end

#device format start
class DeviceFormat(Screen):
	skin = """<screen position="0,0" size="0,0"/>"""
	def __init__(self, session, partition, newfstype):
		Screen.__init__(self, session)
		self.session = session
		self.deviceFormatConsole = Console()
		self.partition = partition
		self.newfstype = newfstype
		self.unmountedList = []
		self.onLayoutFinish.append(self.timerStart)
		self.formatStartTimer = eTimer()
		self.formatStartTimer.callback.append(self.DeviceFormatStart)
		self.setHotplugDisabled = False
		self.umountTimer = eTimer()
		self.umountTimer.callback.append(self.doUnmount)

	def timerStart(self):
		self.formatStartTimer.start(100,True)

	def DeviceFormatStart(self):
		devicemanagerhotplug.setHotplugActive(False)
		self.setHotplugDisabled = True
		print "DeviceFormatStart : ", self.partition,
		print "Filesystem : ",self.newfstype
		device = self.partition["partition"]
		devicepath = "/dev/"+device
		fssize = self.partition["size"]
		newfstype = self.newfstype
		msg = _("Format filesystem, please wait ...")
		msg += _("\nDevice : %s")%(devicepath)
		msg += _("\nFilesystem : %s")%(newfstype)
		msg += _("\nSize : %s")%(byteConversion(fssize))
		self.msgWaiting = self.session.openWithCallback(self.msgWaitingCB, MessageBox_2, msg, type = MessageBox_2.TYPE_INFO, enable_input = False, msgBoxID = None)
		self.umountTimer.start(500,True)

	def doUnmount(self):
		mountpoint = self.partition["mountpoint"]
		if mountpoint != "":
			self.doumountPartition()
		else:
			self.umountPartitionFinished("NORESULT", 0)

	def doumountPartition(self):
		oldfstype = self.partition["fstype"]
		newfstype = self.newfstype

		if newfstype == oldfstype:
			device = self.partition["partition"]
		else:
			device = self.partition["partition"][:3]
		cmd = ""
		mounts = file('/proc/mounts','r')
		for line in mounts.readlines():
			if line.startswith("/dev/%s"%device):
				cmd += "umount %s;"%line.split()[0]
				self.unmountedList.append([line.split()[0], line.split()[1]])
		self.deviceFormatConsole.ePopen(cmd, self.umountPartitionFinished)

	def umountPartitionFinished(self, result, retval, extra_args = None):
		partition = self.partition["partition"]
		oldfstype = self.partition["fstype"]
		newfstype = self.newfstype
		if retval == 0:
			if oldfstype == newfstype:
				self.changePartitionIDFinished("NORESULT", 0)
			else:
				cmd = "sfdisk --change-id /dev/%s %s" % (partition[:3], partition[3:])
				if newfstype[:3] == "ext":
					cmd += " 83"
				else:
					cmd += " c"
				self.deviceFormatConsole.ePopen(cmd, self.changePartitionIDFinished)
		else:
			errorMsg = _("Can not umount device /dev/%s.\nMaybe some files of the filesystem are open")%partition[:3]
			self.msgWaiting.run_close(False,errorMsg)

	def changePartitionIDFinished(self, result, retval, extra_args = None):
		device = self.partition["partition"][:3]
		mountpoint = self.partition["mountpoint"]
		oldfstype = self.partition["fstype"]
		newfstype = self.newfstype
		if retval == 0:
			if oldfstype == newfstype:
				self.refreshPartitionFinished("NORESULT", 0)
			else:
				cmd = "sfdisk -R /dev/%s; sleep 5"%(device)
				self.deviceFormatConsole.ePopen(cmd, self.refreshPartitionFinished)
		else:
			if result and result.find("Use GNU Parted") > 0:
				print "[DeviceManager] /dev/%s use GNU Parted!" % device
				self.refreshPartitionFinished("NORESULT", 0)
			else:
				errorMsg = _("Can not change the partition ID for %s")%device
				self.msgWaiting.run_close(False,errorMsg)

	def refreshPartitionFinished(self, result, retval, extra_args = None):
		print "refreshPartitionFinished!"
		partition = self.partition["partition"]
		mountpoint = self.partition["mountpoint"]
		size = int(self.partition["size"])/1024/1024
		oldfstype = self.partition["fstype"]
		newfstype = self.newfstype
		if retval == 0:
			if newfstype == "ext4":
				cmd = "/sbin/mkfs.ext4 -F "
				if size > 2 * 1024:
					cmd += "-T largefile "
				cmd += "-O extent,flex_bg,large_file,uninit_bg -m1 /dev/" + partition
			elif newfstype == "ext3":
				cmd = "/sbin/mkfs.ext3 -F "
				if size > 2 * 1024:
					cmd += "-T largefile "
				cmd += "-m0 /dev/" + partition
			elif newfstype == "ext2":
				cmd = "/sbin/mkfs.ext2 -F "
				if size > 2 * 1024:
					cmd += "-T largefile "
				cmd += "-m0 /dev/" + partition
			elif newfstype == "vfat":
				if size > 4 * 1024 * 1024:
					cmd = "/usr/sbin/mkfs.vfat -I -S4096 /dev/" + partition
				else:
					cmd = "/usr/sbin/mkfs.vfat -I /dev/" + partition
			self.deviceFormatConsole.ePopen(cmd, self.mkfsFinished)
		else:
			errorMsg = _("Can not format device /dev/%s.\nrefresh partition information failed!")%partition
			self.msgWaiting.run_close(False,errorMsg)

	def mkfsFinished(self, result, retval, extra_args = None):
		print "mkfsFinished!"
		partition = self.partition["partition"]
		if retval == 0:
			cmd = ""
			if len(self.unmountedList) == 0:
				self.doMountFinished("NORESULT",0)
			for x in self.unmountedList:
				cmd += "mount %s %s;"%(x[0], x[1])
				self.deviceFormatConsole.ePopen(cmd, self.doMountFinished)
		else:
			text = _("Make filesystem Error /dev/%s.\nPlease check your device.")%partition
			self.msgWaiting.run_close(False, text)

	def doMountFinished(self, result, retval, extra_args = None):
		print "doMountFinished!"
		text = _("Format finished sucessfully.")
		self.msgWaiting.run_close(True, text)

	def msgWaitingCB(self, ret, msg):
		if ret:
			self.session.openWithCallback(self.exit, MessageBox, msg, MessageBox.TYPE_INFO, timeout = 10)
		else:
			self.session.openWithCallback(self.exit, MessageBox, msg, MessageBox.TYPE_ERROR, timeout = 10)

	def exit(self, ret):
		if self.setHotplugDisabled == True:
			devicemanagerhotplug.setHotplugActive(True)
			self.setHotplugDisabled = False
		self.close()

#device format end

class DeviceInfo():
	def __init__(self):
		self.blockDeviceList = []

	def getBlockDevices(self):
		return self.blockDeviceList

	def refresh(self):
		self.blockDeviceList = []
		self.getBlockDeviceList()

	def getBlockDeviceList(self):
		print "get block device Infomations..."
		for blockdev in listdir("/sys/block"):
			(error, blacklisted, removable, partitions, size, model, vendor) = self.getBlockDeviceInfo(blockdev)
			if not blacklisted and not error:
#				print "%s : error %s, blacklisted %s, removable %s, partitions %s, size %s"%(blockdev, error, blacklisted, removable, partitions, size)
				blockDevice = {}
				blockDevice["blockdev"] = blockdev # str
				blockDevice["removable"] = removable # bool [True, False]
				blockDevice["partitions"] = partitions # list
				blockDevice["size"] = size # str
				blockDevice["model"] = model # str
				blockDevice["vendor"] = vendor # str
				self.blockDeviceList.append(blockDevice)

	def SortPartList(self, partList):
		length = len(partList)-1
		sorted = False
		while sorted is False:
			sorted = True
			for idx in range(length):
				if int(partList[idx][3:]) > int(partList[idx+1][3:]):
					sorted = False
					partList[idx] , partList[idx+1] = partList[idx+1], partList[idx]

	def getBlockDeviceInfo(self, blockdev):
		devpath = "/sys/block/" + blockdev
		error = False
		removable = False
		blacklisted = False
		partitions = []
		size =""
		model = ""
		vendor = ""
		try:
			dev = int(readFile(devpath + "/dev").split(':')[0])
			if dev in (7, 31) or blockdev[0:2] != 'sd': # 7: loop, 31 : mtdblock
				blacklisted = True
				return error, blacklisted, removable, partitions, size, model, vendor
			removable = bool(int(readFile(devpath + "/removable")))
			size = str(int(readFile(devpath + "/size").strip())*512)
			model = readFile(devpath + "/device/model")
			vendor = readFile(devpath + "/device/vendor")
			for partition in listdir(devpath):
				if partition[:len(blockdev)] != blockdev:
					continue
				partitions.append(partition)
			self.SortPartList(partitions)

		except IOError:
			error = True
		return error, blacklisted, removable, partitions, size, model, vendor

	def getPartitionInfo(self, partition):
		mountPoint = self.getPartitionMountpoint(partition)
		(uuid , fsType) = self.getPartitionBlkidInfo(partition)
		size_total = self.getPartitionSize(partition)
		size_free = ""
		if mountPoint != "":
			size_free = self.getPartitionFree(mountPoint)
		partitionInfo = {}
		partitionInfo["partition"] = partition
		partitionInfo["mountpoint"] = mountPoint
		partitionInfo["uuid"] = uuid
		partitionInfo["fstype"] = fsType
		partitionInfo["size"] = size_total
		partitionInfo["free"] = size_free
		return partitionInfo

	def getPartitionMountpoint(self, partition):
		mounts = file('/proc/mounts').read().split('\n')
		for x in mounts:
			if not x.startswith('/'):
				continue
			devpath, mountpoint,  = x.split()[:2]
			if mountpoint.startswith('/autofs'):
				continue
			if path.basename(devpath) == partition:
				return mountpoint
		return ""

	def getPartitionBlkidInfo(self, partition):
		parttionDev = "/dev/"+str(partition)
		uuid = ""
		partitionType = ""
		cmd = "blkid -c /dev/null "+str(parttionDev)
		try:
			line = popen(cmd).readline().strip()
			if not line.startswith(parttionDev):
				return (uuid, partitionType)
#			print "Blikd %s : %s"%(parttionDev, line)
			if line.find(" UUID=") != -1:
				uuid = line.split(" UUID=")[1].split(' ')[0]
			if line.find(" TYPE=") != -1:
				partitionType = line.split(" TYPE=")[1].split(' ')[0].strip('"')
		except:
			print "get blkid info error (%s)"%cmd
		return (uuid, partitionType)

	def getPartitionSize(self, partition):
		devpath = "/sys/block/%s/%s"%( str(partition[:3]), str(partition) )
		try:
			size = readFile(devpath + "/size")
			return str(int(size)*512)
		except:
			return ""

	def getPartitionFree(self, mountPoint):
		try:
			stat = statvfs(mountPoint)
			size_free = stat.f_bfree*stat.f_bsize
			return size_free
		except:
			return ""

	def checkMountPoint(self, check_mountpoint):
		res = []
		try:
			mounts = file('/proc/mounts').read().split('\n')
			for x in mounts:
				if not x.startswith('/'):
					continue
				devpath, mountpoint  = x.split()[:2]
				if mountpoint == check_mountpoint:
					res.append(devpath)
		except:
			pass
		return res

	def checkMountDev(self, device):
		res = []
		try:
			mounts = file('/proc/mounts').read().split('\n')
			for x in mounts:
				if not x.startswith('/'):
					continue
				devpath, mountpoint  = x.split()[:2]
				if devpath == device:
					res.append(mountpoint)
		except:
			pass
		return res

	def isMounted(self, devpath, mountpoint):
		try:
			mounts = file('/proc/mounts').read().split('\n')
			for x in mounts:
				if not x.startswith('/'):
					continue
				_devpath, _mountpoint  = x.split()[:2]
				if devpath == _devpath and mountpoint == _mountpoint:
					return True
		except:
			pass
		return False

	def isMountable(self, partition):
		autofsPath = "/autofs/"+partition.device
		mountable = False
		try:
			os.listdir(autofsPath)
			mountable = True
		except:
			pass
		return mountable

	def isFstabAutoMounted(self, uuid, devpath, mountpoint):
#		print "	>> isFstabMounted, uuid : %s, devpath : %s, mountpoint : %s"%(uuid, devpath, mountpoint)
		if mountpoint[-1] == '/':
			mountpoint = mountpoint[:-1]
		data = file('/etc/fstab').read().split('\n')
		for line in data:
			if not line.startswith('/'):
				continue
			dev, mp, ms = line.split()[0:3]
			if uuid is not None and dev.startswith('UUID'):
				if dev.split('=')[1] == uuid.strip("\"") and mp == mountpoint and ms == 'auto':
#					print "	>> line : ", line
					return True
			elif dev == devpath and mp == mountpoint and ms == 'auto':
#				print "	>> line : ", line
				return True
		return False

	def umountByMountpoint(self, mountpoint):
		if mountpoint is None:
			return False
		try:
			if path.ismount(mountpoint):
				cmd = "umount " + mountpoint
				print "[DeviceManager] ", cmd
				os.system(cmd)
		except:
			print "Umount by mountpoint failed!"
		if not path.ismount(mountpoint):
			return True
		return False

	def umountByDevpath(self, devpath):
		cmd = "umount " + devpath
		print "[DeviceManager] ", cmd
		os.system(cmd)

deviceinfo = DeviceInfo()

class MountpointBrowser(Screen):
	skin="""
		<screen name="MountpointBrowser" position="center,120" size="670,500" title="Select mountpoint">
			<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/LDteam/images/buttons/red.png" position="20,0" size="140,40" alphatest="on" />
			<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/LDteam/images/buttons/green.png" position="180,0" size="140,40" alphatest="on" />
			<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/LDteam/images/buttons/yellow.png" position="340,0" size="140,40" alphatest="on" />
			<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/LDteam/images/buttons/blue.png" position="500,0" size="140,40" alphatest="on" />
			<widget source="key_red" render = "Label" position="20,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" foregroundColor="#ffffff" backgroundColor="#9f1313" transparent="1" />
			<widget source="key_green" render = "Label" position="180,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" foregroundColor="#ffffff" backgroundColor="#1f771f" transparent="1" />
			<widget source="key_yellow" render = "Label" position="340,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" foregroundColor="#ffffff" backgroundColor="#a08500" transparent="1" />
			<widget source="key_blue" render = "Label" position="500,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" foregroundColor="#ffffff" backgroundColor="#18188b" transparent="1" />
			<eLabel	position="10,50" size="650,1" backgroundColor="#b3b3b9"/>
			<widget name="filelist" position="10,60" size="650,440" itemHeight="30" scrollbarMode="showOnDemand"/>
		</screen>
	"""
	def __init__(self, session):
		Screen.__init__(self, session)
		self["key_red"] = StaticText(_("Cancel"))
		self["key_green"] = StaticText(_("Select"))
		self["key_yellow"] = StaticText(_("Create directory"))
		self["key_blue"] = StaticText("Delete directory")
		directory = "/media/"
		inhibitDirs = ["/autofs", "/mnt", "/hdd", "/bin", "/boot", "/dev", "/etc", "/home", "/lib", "/proc", "/sbin", "/share", "/sys", "/tmp", "/usr", "/var"]
		self.filelist = FileList(directory, matchingPattern="", inhibitDirs = inhibitDirs)
		self["filelist"] = self.filelist

		self["shortcuts"] = ActionMap(["ColorActions"],
			{
			"red": self.exit,
			"green": self.select,
			"yellow": self.createDirectory,
			"blue": self.deleteDirectory,
			}, -2)

		self["OkCancelActions"] = ActionMap(["OkCancelActions"],
			{
			"cancel": self.exit,
			"ok": self.ok,
			}, -2)

	def ok(self):
		if self.filelist.canDescent():
			self.filelist.descent()

	def select(self):
		if self["filelist"].getCurrentDirectory() is not None:
			if self.filelist.canDescent() and self["filelist"].getFilename() and self["filelist"].getFilename().startswith(self["filelist"].getCurrentDirectory()):
				self.filelist.descent()
				currDir = self["filelist"].getCurrentDirectory()
				self.close(currDir)
		else:
			self.close(self["filelist"].getFilename())

	def createDirectory(self):
		self.session.openWithCallback(self.createDirectoryCB, VirtualKeyBoard, title = (_("Input mount point path.")), text = "")

	def createDirectoryCB(self, retval = None):
		newdir=None
		try:
			if retval is not None:
				newdir = self["filelist"].getCurrentDirectory()+'/'+retval
				if not path.exists(newdir):
					os.system("mkdir %s"%newdir)
				self.filelist.refresh()
		except:
			if newdir:
				self.session.open(MessageBox, _("Create directory failed!\n%s")%newdir, MessageBox.TYPE_ERROR, timeout = 10)

	def deleteDirectory(self):
		delDir=None
		try:
			if self["filelist"].getCurrentDirectory() is not None:
				if self.filelist.canDescent() and self["filelist"].getFilename() and self["filelist"].getFilename().startswith(self["filelist"].getCurrentDirectory()):
					delDir = self["filelist"].getFilename()
					if path.exists(delDir):
						os.system("rmdir '%s'"%delDir)
					if path.exists(delDir):
						self.session.open(MessageBox, _("Delete directory failed!\nMaybe directory is not empty."), MessageBox.TYPE_ERROR, timeout = 10)
					self.filelist.refresh()
		except:
			if delDir:
				self.session.open(MessageBox, _("Delete directory failed!\n%s")%newdir, MessageBox.TYPE_ERROR, timeout = 10)

	def exit(self):
		self.close(False)

class MessageBoxConfirm(MessageBox):
	skin = 	"""
		<screen position="center,center" size="620,10" title="Message">
			<widget name="text" position="65,8" size="420,0" font="Regular;20" />
			<widget name="ErrorPixmap" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/LDteam/images/icons/input_error.png" position="5,5" size="53,53" alphatest="blend" />
			<widget name="QuestionPixmap" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/LDteam/images/icons/input_question.png" position="5,5" size="53,53" alphatest="blend" />
			<widget name="InfoPixmap" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/LDteam/images/icons/input_info.png" position="5,5" size="53,53" alphatest="blend" />
			<widget name="list" position="100,100" size="380,375" transparent="1" />
			<applet type="onLayoutFinish">
# this should be factored out into some helper code, but currently demonstrates applets.
from enigma import eSize, ePoint

orgwidth  = self.instance.size().width()
orgheight = self.instance.size().height()
orgpos    = self.instance.position()
textsize  = self[&quot;text&quot;].getSize()

# y size still must be fixed in font stuff...
textsize = (textsize[0] + 50, textsize[1] + 50)
offset = 0
if self.type == self.TYPE_YESNO:
	offset = 60
wsizex = textsize[0] + 60
wsizey = textsize[1] + offset
if (280 &gt; wsizex):
	wsizex = 280
wsize = (wsizex, wsizey)

# resize
self.instance.resize(eSize(*wsize))

# resize label
self[&quot;text&quot;].instance.resize(eSize(*textsize))

# move list
listsize = (wsizex, 50)
self[&quot;list&quot;].instance.move(ePoint(0, textsize[1]))
self[&quot;list&quot;].instance.resize(eSize(*listsize))

# center window
newwidth = wsize[0]
newheight = wsize[1]
self.instance.move(ePoint(orgpos.x() + (orgwidth - newwidth)/2, orgpos.y() + (orgheight - newheight)/2))
			</applet>
		</screen>
		"""

dmconfigfile = resolveFilename(SCOPE_PLUGINS, "SystemPlugins/DeviceManager/devicemanager.cfg")
class DeviceManagerConfig():
	def __init__(self):
		self.configList = []

	def getConfigList(self):
		return self.configList

	def updateConfigList(self):
		try:
			self.configList = []
			file = open("/proc/mounts")
			mounts = file.readlines()
			file.close()
			for x in mounts:
				if x.startswith("/dev/sd"):
					device = x.split()[0].split('/dev/')[1]
					mountpoint = x.split()[1]
					if mountpoint.startswith('/autofs'):
						continue
					(uuid, partitionType) = deviceinfo.getPartitionBlkidInfo(device)
					if uuid != '' and mountpoint != '':
						self.configList.append([uuid, mountpoint])
			self.saveConfig()
		except:
			print "updateConfigList failed!"

	def loadConfig(self):
		if not fileExists(dmconfigfile):
			os.system("touch %s" % dmconfigfile)
		self.configList = []
		data = file(dmconfigfile).read().split('\n')
		for line in data:
			if line.find(':') != -1:
				(uuid, mountpoint) = line.split(':')
				if uuid != '' and mountpoint != '':
					self.configList.append([uuid, mountpoint])

	def saveConfig(self):
		confFile = open(dmconfigfile,'w')
		data = ""
		for line in self.configList:
			data += "%s:%s\n"%(line[0],line[1]) # uuid, mountpoint
		confFile.write(data)
		confFile.close()

	def appendConfig(self, uuid, mountpoint):
		for x in self.configList:
			if x[0] == uuid or x[1] == mountpoint:
				self.configList.remove(x)
		self.configList.append([uuid, mountpoint])

	def removeConfig(self, value):
		for x in self.configList:
			if x[0] == value or x[1] == value:
				self.configList.remove(x)

devicemanagerconfig = DeviceManagerConfig()

class deviceManagerHotplug:
	def __init__(self):
		self.hotplugActive = True

	def setHotplugActive(self,value=True):
		if value:
			self.hotplugActive = True
		else:
			self.hotplugActive = False

	def printDebug(self):
		for p in harddiskmanager.partitions:
			print " # partition : %s %s %s %s %s(mp, des, f_mounted, is_hot, dev)"%(p.mountpoint, p.description, p.force_mounted, p.is_hotplug,p.device)

	def doMount(self, uuid, devpath, mountpoint, filesystem):
# check current device mounted on another mountpoint.
		mp_list = []
		mp_list = deviceinfo.checkMountDev(devpath)
		for mp in mp_list:
			if mp != mountpoint and path.ismount(mp):
				deviceinfo.umountByMountpoint(mp)
# check another device mounted on configmountpoint
		devpath_list = []
		devpath_list = deviceinfo.checkMountPoint(mountpoint)
		for devpath_ in devpath_list:
			if devpath_ != devpath:
				print "[DeviceManager] Mount Failed. (Another device is already mounted)"
				return
# do mount
#		print "[DeviceManager] doMount"
		if not path.exists(mountpoint):
			os.system("mkdir %s"%mountpoint)
		if path.exists(mountpoint):
			if not path.ismount(mountpoint):
				if filesystem == "ntfs":
					cmd = "ntfs-3g %s %s"%(devpath, mountpoint)
				elif filesystem is None:
					cmd = "mount %s %s"%(devpath, mountpoint)
				else:
					cmd = "mount -t %s %s %s"%(filesystem, devpath, mountpoint)
				print "[DeviceManager] cmd : %s"%cmd
				os.system(cmd)
				if not deviceinfo.isMounted(devpath, mountpoint):
					print "[DeviceManager] %s doMount failed!"%devpath
					return
				else:
# Update partition Info, add
					self.addPartitionAutofsMountpoint(devpath, mountpoint)

	def doUmount(self, device, mountpoint):
		devpath = "/dev/"+device
		mountpoints = deviceinfo.checkMountDev(devpath)
		if len(mountpoints) == 0:
			return
		for mp in mountpoints:
			cmd = "umount %s"%devpath
			print "[DeviceManager] cmd : %s"%cmd
			os.system(cmd)

	def addHotPlugDevice(self, partition):
		device = partition.device
		devpath = "/dev/"+device
# get BlkidInfo
		(uuid, filesystem) = deviceinfo.getPartitionBlkidInfo(device)
		if uuid == "":
# retry..
			os.system("sleep 1")
			(uuid, filesystem) = deviceinfo.getPartitionBlkidInfo(device)
		if uuid == "":
			print "[DeviceManagerHotplug] getBlkidInfo failed!"
			return
# get configList
		devicemanagerconfig.loadConfig()
		configList = devicemanagerconfig.getConfigList()
		mountpoint = None
		for line in configList:
			if uuid == line[0].strip():
				mountpoint = line[1].strip()
				break
		if mountpoint is None:
			return
# do mount
		if deviceinfo.isMounted(devpath, mountpoint):
			pass
#			print "[DeviceManagerHotplug] already mounted"
		else:
			self.doMount(uuid, devpath, mountpoint, filesystem)

	def removeHotplugDevice(self, partition):
		self.doUmount(partition.device, partition.mountpoint)

	def getHotplugAction(self, action, partition):
		if not self.hotplugActive or not config.plugins.devicemanager.hotplug_enable.value:
			return
		if partition.device is None or not partition.device.startswith("sd"):
			return
		print "[DeviceManagerHotplug] action : %s, device : %s"%(action, partition.device)

		if action == 'add':
			self.addHotPlugDevice(partition)
		elif action == 'remove':
			self.removeHotplugDevice(partition)

	def addPartitionAutofsMountpoint(self, devpath, mountpoint):
		device = path.basename(devpath)
		autofsMountpoint = harddiskmanager.getAutofsMountpoint(device)
# check already appended to partition list
		for x in harddiskmanager.partitions:
			if x.mountpoint == autofsMountpoint or x.mountpoint == mountpoint:
				return
#
		from Components.Harddisk import Partition
		physdev = path.realpath('/sys/block/' + device[:3] + '/device')[4:]
		description = harddiskmanager.getUserfriendlyDeviceName(device, physdev)
		p = Partition(mountpoint = autofsMountpoint, description = description, force_mounted = True, device = device)
		harddiskmanager.partitions.append(p)
		harddiskmanager.on_partition_list_change("add", p)

	def autoMountOnStartup(self):
		devicemanagerconfig.loadConfig()
		configList = devicemanagerconfig.getConfigList()
# get blkid info
		blkiddata = []
		data = os.popen("blkid -c /dev/NULL /dev/sd*").readlines()
		for line in data:
			devpath = uuid = filesystem = ""
			devpath = line.split(':')[0]
			if line.find(" UUID=") != -1:
				uuid = line.split(" UUID=")[1].split(' ')[0]
			if line.find(" TYPE=") != -1:
				filesystem = line.split(" TYPE=")[1].split(' ')[0].strip('"')
			blkiddata.append((devpath, uuid, filesystem))
# check configList
		for c in configList:
			uuid_cfg = c[0].strip()
			mountpoint_cfg = c[1].strip()
			for (devpath, uuid, filesystem) in blkiddata:
				if uuid_cfg == uuid:
# do mount
					if deviceinfo.isMounted(devpath, mountpoint_cfg):
#						print "[Devicemanager startup] already mounted"
						self.addPartitionAutofsMountpoint(devpath, mountpoint_cfg)
					else:
#						print "[autoMountOnStartup] do mount(%s %s %s)"%(devpath, configmountpoint, filesystem)
						self.doMount(uuid, devpath, mountpoint_cfg, filesystem)

	def umountOnShutdown(self):
		devicemanagerconfig.loadConfig()
		configList = devicemanagerconfig.getConfigList()
# get mount info
		mounts = []
		data = file('/proc/mounts').read().split('\n')
		for x in data:
			if not x.startswith('/dev/sd'):
				continue
			devpath, mountpoint  = x.split()[:2]
			mounts.append((path.basename(devpath), mountpoint))
# get blkid info
		data = self.getBlkidInfo()
# check configList
		for c in configList:
			uuid_cfg = c[0].strip()
			mountpoint_cfg = c[1].strip()
			device_cfg = None
			if uuid_cfg in data.keys():
				device_cfg = data[uuid_cfg]
			if device_cfg is None:
				continue
			for (device, mountpoint) in mounts:
				if device_cfg == device:
					if not deviceinfo.isFstabAutoMounted(uuid_cfg, "/dev/"+device_cfg, mountpoint_cfg):
						self.doUmount(device, mountpoint)

	def getBlkidInfo(self):
		data = {}
		blkid_data = os.popen("blkid -c /dev/NULL /dev/sd*").read()
		for line in blkid_data.split('\n'):
#			print "[DeviceManager] getBlkidInfo line : ",line
			device = uuid = ""
			device = path.basename(line.split(':')[0])
			if line.find(" UUID=") != -1:
				blkid_uuid = line.split(" UUID=")[1].split(' ')[0]
				data[blkid_uuid] = device
		return data

devicemanagerhotplug = deviceManagerHotplug()

def DeviceManagerhotplugDeviceStart(action, device):
	devicemanagerhotplug.getHotplugAction(action, device)

def callBackforDeviceManager(session, callback_result = False):
	if callback_result == True:
		session.open(DeviceManager)

def checkMounts(session):
	try:
		noMountable_dev = ""
		for blockdev in listdir("/sys/block"):
			devpath = "/sys/block/" + blockdev
			dev = int(readFile(devpath + "/dev").split(':')[0])
			if dev in (7, 31) or blockdev[0:2] != 'sd': # 7: loop, 31 : mtdblock
				continue
			partitions = []
			noMountable_partitions = []
			for partition in listdir(devpath):
				if not partition.startswith(blockdev):
					continue
				partitions.append(partition)
				if os.access('/autofs/'+partition,0) is False:
					noMountable_partitions.append(partition)
			if len(partitions) == 0 or len(noMountable_partitions) != 0:
				if noMountable_dev != "":
					noMountable_dev +=  ' '
				noMountable_dev += blockdev

		if noMountable_dev != "":
				print "Umountable partitions found."
				InfoText = _("No mountable devices found.! (%s)\nDo you want to open DeviceManager and do initialize or format this device?\n\n(Open 'Menu->Setup->System -> Harddisk -> DeviceManager'\n and press MENU button to deactivate this check.)")%noMountable_dev
				AddNotificationWithCallback(
								boundFunction(callBackforDeviceManager, session),
								MessageBox, InfoText, timeout = 60, default = False
				)
	except:
		print "checkMounts failed!"

def sessionstart(reason, **kwargs):
	if reason == 0:
		if kwargs.has_key("session") and config.plugins.devicemanager.mountcheck_enable.value == True:
			session = kwargs["session"]
			checkMounts(session)
		if config.plugins.devicemanager.hotplug_enable.value:
			harddiskmanager.on_partition_list_change.append(DeviceManagerhotplugDeviceStart)
	elif reason == 1:
		if config.plugins.devicemanager.hotplug_enable.value:
			harddiskmanager.on_partition_list_change.remove(DeviceManagerhotplugDeviceStart)

def autostart(reason, **kwargs):
	if reason == 0:
		try:
# check at first enigma2 start
			if not fileExists(dmconfigfile):
				print "[DeviceManager] autostart : check devices at first start"
				sda_isremovable = False
				sda_UUID = ""
				os.system("touch %s"%dmconfigfile)
# check sda
				sda_data = popen("cat /proc/partitions | grep sda1").read()
				if sda_data != '':
					sda_UUID = popen("blkid -o value -s UUID /dev/sda1").read().strip('\n')
					sda_isremovable = bool(int(readFile("/sys/block/sda/removable")))
					print "sda : %s, %s"%(sda_UUID, sda_isremovable)
				cfg = ""
				if sda_data != '':
					cfg += '"%s":/media/hdd\n'%sda_UUID
				confFile = open(dmconfigfile,'w')
				confFile.write(cfg)
				confFile.close()
				if not path.exists("/media/hdd"):
					os.system("mkdir -p /media/hdd")
# auto mount
			devicemanagerhotplug.autoMountOnStartup()
		except:
			print "[DeviceManager] autostart failed!"
	elif reason == 1:
		devicemanagerhotplug.umountOnShutdown()

def menu(menuid, **kwargs):
	if menuid == "system":
		return [(_("DeviceManager"), main, "device_manager", 50)]
	return []

def main(session, **kwargs):
	session.open(DeviceManager)

def Plugins(path, **kwargs):
	return [
		PluginDescriptor(name = _("DeviceManager"), description = _("manage block devices of your VU+"), where = PluginDescriptor.WHERE_MENU,fnc=menu),
		PluginDescriptor(where = PluginDescriptor.WHERE_SESSIONSTART, needsRestart = True, fnc = sessionstart),
		PluginDescriptor(where = PluginDescriptor.WHERE_AUTOSTART, needsRestart = True, fnc = autostart)
		]

class MessageBox_2(MessageBox):
	def __init__(self, session, text, type = MessageBox.TYPE_YESNO, timeout = -1, close_on_any_key = False, default = True, enable_input = True, msgBoxID = None):
		MessageBox.__init__(self, session, text, type, timeout, close_on_any_key, default, enable_input, msgBoxID)
		self.skinName = "MessageBox"
		self.closeTimer = eTimer()
		self.closeTimer.callback.append(self.msg_close)
		self.devicemanager_ret = False
		self.devicemanager_msg = ""

	def msg_close(self):
		self.close(self.devicemanager_ret, self.devicemanager_msg)

	def run_close(self, ret, msg=""):
		self.devicemanager_ret = ret
		self.devicemanager_msg = msg
		self.closeTimer.start(100,True)

	def createSummary(self):
		return MessageBox_2_Summary

class MessageBox_2_Summary(Screen):
	skin="""
		<screen name="MessageBox_2_Summary" position="0,0" size="256,64" id="1">
			<widget source="parent.Text" render="Label" position="0,0" size="256,64" font="Regular;13" halign="center" valign="center" />
		</screen>
	"""
