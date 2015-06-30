from Plugins.Plugin import PluginDescriptor

from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.Sources.StaticText import StaticText

from Screens.MessageBox import MessageBox

from Components.PluginComponent import plugins

from Components.Pixmap import Pixmap
from Components.Console import Console
from Components.FileList import FileList

from Components.ConfigList import ConfigListScreen
from Components.config import config, getConfigListEntry, ConfigSubsection, ConfigYesNo, ConfigText, ConfigDirectory, ConfigSelection

from os import system

_default = {
	"type"  :"ftp",
	"server":"",
	"userid":"",
	"passwd":"",
	"mountpoint":"/media/net/",
	"startup":False,
}
config.plugins.netdrivesetup = ConfigSubsection()
config.plugins.netdrivesetup.type   = ConfigSelection(default=_default["type"], choices=[("ftp", _("FTP"))])
config.plugins.netdrivesetup.server = ConfigText(default=_default["server"], visible_width=60, fixed_size=False)
config.plugins.netdrivesetup.userid = ConfigText(default=_default["userid"], visible_width=60, fixed_size=False)
config.plugins.netdrivesetup.passwd = ConfigText(default=_default["passwd"], visible_width=60, fixed_size=False)
config.plugins.netdrivesetup.mountpoint = ConfigDirectory(default=_default["mountpoint"])
config.plugins.netdrivesetup.startup = ConfigYesNo(default=_default["startup"])

def isempty(data):
	if data is not None:
		if len(data) > 0:
			return False
	return True

class NetDrivebrowser(Screen):
	skin = 	"""
		<screen name="NetDrivebrowser" position="center,120" size="600,390" title="NetDrive Setup > Mount Point">
			<ePixmap pixmap="skin_default/buttons/red.png" position="5,0" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/green.png" position="155,0" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/yellow.png" position="305,0" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/blue.png" position="455,0" size="140,40" alphatest="on" />

			<widget source="key_red" render="Label" position="5,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" foregroundColor="#ffffff" transparent="1" />
			<widget source="key_green" render="Label" position="155,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" foregroundColor="#ffffff" transparent="1" />
			<widget source="key_yellow" render="Label" position="305,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#a08500" foregroundColor="#ffffff" transparent="1" />
			<widget source="key_blue" render="Label" position="455,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#18188b" foregroundColor="#ffffff" transparent="1" />

			<widget source="status" render="Label" position="0,40" zPosition="1" size="600,40" font="Regular;18" halign="center" valign="center" />
			<widget name="filelist" position="0,80" size="600,310" scrollbarMode="showOnDemand" />
		</screen>
		"""
	def __init__(self, session):
		self.session = session

		Screen.__init__(self, session)

		self["actions"] = ActionMap(["OkCancelActions", "ShortcutActions", "WizardActions", "ColorActions", ], {
			"red"   : self.OnKeyRed,
			"green" : self.OnKeyGreen,
			"ok"    : self.OnKeyOK,
			"cancel": self.OnKeyCancel,
			"up"    : self.OnKeyUp,
			"down"  : self.OnKeyDown,
			"left"  : self.OnKeyLeft,
			"right" : self.OnKeyRight,
		}, -1)

		inhibitdirs = ["/bin", "/boot", "/dev", "/etc", "/lib", "/proc", "/sbin", "/sys", "/usr", "/var"]
		self["filelist"] = FileList("/", showDirectories=True, showFiles=False, inhibitMounts=[], inhibitDirs=inhibitdirs)
		self["status"]   = StaticText(_(" "))

		self["key_red"]    = StaticText(_("Close"))
		self["key_green"]  = StaticText(_("Select"))
		self["key_yellow"] = StaticText(_(" "))
		self["key_blue"]   = StaticText(_(" "))

		self.OnKeyDown()

	def UpdateStatus(self):
		current = self["filelist"].getSelection()[0]
		self["status"].setText(current)

	def OnKeyRed(self):
		self.OnKeyCancel()

	def OnKeyGreen(self):
		self.close(self["status"].getText())

	def OnKeyOK(self):
		if not self["filelist"].canDescent():
			return
		self["filelist"].descent()
		self.UpdateStatus()

	def OnKeyCancel(self):
		self.close(None)

	def OnKeyDown(self):
		self["filelist"].down()
		self.UpdateStatus()

	def OnKeyUp(self):
		self["filelist"].up()
		self.UpdateStatus()

	def OnKeyLeft(self):
		self["filelist"].pageUp()
		self.UpdateStatus()

	def OnKeyRight(self):
		self["filelist"].pageDown()
		self.UpdateStatus()

class NetDriveSetup(ConfigListScreen, Screen):
	skin = 	"""
		<screen name="NetDriveSetup" position="center,120" size="600,390" title="Network Drive Setup">
			<ePixmap pixmap="skin_default/buttons/red.png" position="5,0" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/green.png" position="155,0" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/yellow.png" position="305,0" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/blue.png" position="455,0" size="140,40" alphatest="on" />

			<widget source="key_red" render="Label" position="5,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" foregroundColor="#ffffff" transparent="1" />
			<widget source="key_green" render="Label" position="155,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" foregroundColor="#ffffff" transparent="1" />
			<widget source="key_yellow" render="Label" position="305,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#a08500" foregroundColor="#ffffff" transparent="1" />
			<widget source="key_blue" render="Label" position="455,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#18188b" foregroundColor="#ffffff" transparent="1" />

			<widget name="config" position="5,70" size="590,250" scrollbarMode="showOnDemand" />
			<widget name="introduction" position="5,335" size="590,60" font="Regular;18" halign="center" />
			<widget name="VKeyIcon" pixmap="skin_default/buttons/key_text.png" position="565,365" zPosition="10" size="35,25" transparent="1" alphatest="on" />
		</screen>
		"""
	def __init__(self, session):
		self.configlist = []
		self.session = session
		Screen.__init__(self, session)
		ConfigListScreen.__init__(self, self.configlist)

		self["actions"]  = ActionMap(["OkCancelActions", "ColorActions", "WizardActions",], {
			"ok"    : self.OnKeyOK2,
			"cancel": self.OnKeyCancel,
			"green" : self.OnKeyGreen,
			"red"   : self.OnKeyRed,
			"yellow": self.OnKeyYellow,
			"blue"  : self.OnKeyBlue,
		}, -2)

		self["VirtualKB"] = ActionMap(["VirtualKeyboardActions" ], {
			"showVirtualKeyboard": self.KeyText,
		}, -1)

		self["VKeyIcon"]   = Pixmap()
		self["key_red"]    = StaticText(_("Close"))
		self["key_green"]  = StaticText(_("Mount"))
		self["key_yellow"] = StaticText(_("Default"))
		self["key_blue"]   = StaticText(_("Save"))
		self["introduction"] = Label(" ")

		self.backup = {
			"type"  :config.plugins.netdrivesetup.type.value,
			"server":config.plugins.netdrivesetup.server.value,
			"userid":config.plugins.netdrivesetup.userid.value,
			"passwd":config.plugins.netdrivesetup.passwd.value,
			"mountpoint":config.plugins.netdrivesetup.mountpoint.value,
			"startup":config.plugins.netdrivesetup.startup.value,
			}
		self.console = Console()
		self.configEntryMountPoint = None

		self.MakeConfigList()
		self.onLayoutFinish.append(self.LayoutFinished)

	@staticmethod
	def IsMounted(self=None):
		local = config.plugins.netdrivesetup.mountpoint.value
		if local[len(local)-1] == '/':
			local = local[:-1]
		mounts = file('/proc/mounts').read()
		for mountpoint in mounts.splitlines():
			if mountpoint.find('curlftpfs') >= 0 and mountpoint.find(local) >= 0:
				print "[NetDriveSetup] Already mounted"
				return True
		print "[NetDriveSetup] No mounted point"
		return False

	@staticmethod
	def Umount(self=None):
		command = "umount %s" % (config.plugins.netdrivesetup.mountpoint.value)
		ret = NetDriveSetup.Execute(command, self)

	@staticmethod
	def Execute(command, owner=None):
		print "[NetDriveSetup] Excute :", command
		def ConsoleFinishCB(result, retval, extra_args=None):
			if owner is None:
				return
			if not isempty(result):
				owner.UpdateInfo(result)
			else:
				owner.LayoutFinished()
				owner.close()
		if owner is None:
			system(command)
			return
		owner.console.ePopen(command, ConsoleFinishCB)

	@staticmethod
	def RunCurlFTPFS(self=None):
		if (isempty(config.plugins.netdrivesetup.server.value) or
		    isempty(config.plugins.netdrivesetup.userid.value) or
		    isempty(config.plugins.netdrivesetup.passwd.value) or
		    isempty(config.plugins.netdrivesetup.mountpoint.value)):
			print "[NetDriveSetup] Option Empty..\n   SVR [%(server)s], MP [%(mountpoint)s], ID [%(userid)s], PWD [%(passwd)s]" % {
				"server":config.plugins.netdrivesetup.server.value,
				"userid":config.plugins.netdrivesetup.userid.value,
				"passwd":config.plugins.netdrivesetup.passwd.value,
				"mountpoint":config.plugins.netdrivesetup.mountpoint.value
				}
			return

		if(NetDriveSetup.IsMounted()):
			NetDriveSetup.Umount()

		command = "modprobe fuse && curlftpfs %(server)s %(mountpoint)s -o user=%(userid)s:%(passwd)s,allow_other" % {
				"server":config.plugins.netdrivesetup.server.value,
				"userid":config.plugins.netdrivesetup.userid.value,
				"passwd":config.plugins.netdrivesetup.passwd.value,
				"mountpoint":config.plugins.netdrivesetup.mountpoint.value
				}
		NetDriveSetup.Execute(command, self)

	def LayoutFinished(self):
		if(NetDriveSetup.IsMounted()):
			self.SetGreenButtonText(_("Umount"))
		else:	self.SetGreenButtonText(_("Mount"))
		self.UpdateInfo()

	def SetGreenButtonText(self, data):
		self["key_green"].setText(data)

	def UpdateInfo(self, data=None):
		if data is not None:
			self["introduction"].setText(data)
			return
		info = " "
		local = config.plugins.netdrivesetup.mountpoint.value
		if local[len(local)-1] == '/':
			local = local[:-1]
		mounts = file('/proc/mounts').read()
		for mountpoint in mounts.splitlines():
			if mountpoint.find('curlftpfs') >= 0 and mountpoint.find(local) >= 0:
				info = mountpoint
		self["introduction"].setText(info)

	def MakeConfigList(self):
		self.UpdateConfigList()

	def UpdateConfigList(self):
		self.configlist = []
		self.configEntryMountPoint = getConfigListEntry(_("Mount Point"), config.plugins.netdrivesetup.mountpoint)

		self.configlist.append(getConfigListEntry(_("Server"), config.plugins.netdrivesetup.server))
		self.configlist.append(getConfigListEntry(_("User ID"), config.plugins.netdrivesetup.userid))
		self.configlist.append(getConfigListEntry(_("Password"), config.plugins.netdrivesetup.passwd))
		self.configlist.append(self.configEntryMountPoint)
		self.configlist.append(getConfigListEntry(_("Enable mount automatically while start"), config.plugins.netdrivesetup.startup))
		self["config"].list = self.configlist
		self["config"].l.setList(self.configlist)

	def Save(self):
		config.plugins.netdrivesetup.type.save()
		config.plugins.netdrivesetup.server.save()
		config.plugins.netdrivesetup.userid.save()
		config.plugins.netdrivesetup.passwd.save()
		config.plugins.netdrivesetup.mountpoint.save()
		config.plugins.netdrivesetup.startup.save()
		config.plugins.netdrivesetup.save()
		config.plugins.save()
		config.save()

	def Restore(self):
		print "[NetDriveSetup] Restore default setting..."
		config.plugins.netdrivesetup.type.value   = self.backup["type"]
		config.plugins.netdrivesetup.server.value = self.backup["server"]
		config.plugins.netdrivesetup.userid.value = self.backup["userid"]
		config.plugins.netdrivesetup.passwd.value = self.backup["passwd"]
		config.plugins.netdrivesetup.mountpoint.value = self.backup["mountpoint"]
		config.plugins.netdrivesetup.startup.value = self.backup["startup"]

	def NetDrivebrowserCB(self, data):
		if data is None: return
		if isempty(data): data = "/"
		config.plugins.netdrivesetup.mountpoint.value = data

	def OnKeyGreen(self):
		self.Save()
		self["introduction"].setText("Plesae, wait..")
		if self["key_green"].getText() == "Mount":
			NetDriveSetup.RunCurlFTPFS(self)
		else:	NetDriveSetup.Umount(self)

	def OnKeyCancel(self):
		self.Restore()
		self.close()

	def OnKeyRed(self):
		self.OnKeyCancel()

	def OnKeyBlue(self):
		self.Save()
		self.close()

	def OnKeyOK2(self):
		if self["config"].getCurrent() != self.configEntryMountPoint:
			return
		self.session.openWithCallback(self.NetDrivebrowserCB, NetDrivebrowser)

	def OnKeyYellow(self):
		print "[NetDriveSetup] Setting default values.."
		config.plugins.netdrivesetup.type.value   = _default["type"]
		config.plugins.netdrivesetup.server.value = _default["server"]
		config.plugins.netdrivesetup.userid.value = _default["userid"]
		config.plugins.netdrivesetup.passwd.value = _default["passwd"]
		config.plugins.netdrivesetup.mountpoint.value = _default["mountpoint"]
		config.plugins.netdrivesetup.startup.value = _default["startup"]
		self.UpdateConfigList()

def SessionStartMain(session, **kwargs):
	if not config.plugins.netdrivesetup.startup.value:
		return
	NetDriveSetup.RunCurlFTPFS()

def PluginMain(session, **kwargs):
	session.open(NetDriveSetup)

def MenuSelected(selected, **kwargs):
	if selected == "system":
		return [(_("NetDrive Setup"), PluginMain, "netdrivesetup", 80)]
	return []

def Plugins(**kwargs):
	l = []
	l.append(PluginDescriptor(name=_("NetDrive Setup"), description=_("Mount a FTP server"), where=PluginDescriptor.WHERE_PLUGINMENU, fnc=PluginMain))
	l.append(PluginDescriptor(where=PluginDescriptor.WHERE_MENU, fnc=MenuSelected))
	l.append(PluginDescriptor(where=PluginDescriptor.WHERE_SESSIONSTART, fnc=SessionStartMain))
	return l

