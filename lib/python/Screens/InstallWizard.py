from Screens.Screen import Screen
from Components.ConfigList import ConfigListScreen, ConfigList
from Components.ActionMap import ActionMap
from Components.Sources.StaticText import StaticText
from Components.config import config, ConfigSubsection, ConfigBoolean, getConfigListEntry, ConfigSelection, ConfigYesNo, ConfigIP
from Components.Network import iNetwork
from Components.Ipkg import IpkgComponent
from enigma import eDVBDB

config.misc.installwizard = ConfigSubsection()
config.misc.installwizard.hasnetwork = ConfigBoolean(default = False)
config.misc.installwizard.ipkgloaded = ConfigBoolean(default = False)
config.misc.installwizard.channellistdownloaded = ConfigBoolean(default = False)


class InstallWizard(Screen, ConfigListScreen):

	STATE_UPDATE = 0
	STATE_CHOISE_CHANNELLIST = 1
	INSTALL_PLUGINS = 2
	INSTALL_SKINS = 3
#	STATE_CHOISE_SOFTCAM = 4

	def __init__(self, session, args = None):
		Screen.__init__(self, session)

		self.index = args
		self.list = []
		ConfigListScreen.__init__(self, self.list)

		if self.index == self.STATE_UPDATE:
			config.misc.installwizard.hasnetwork.value = False
			config.misc.installwizard.ipkgloaded.value = False
			modes = {0: " "}
			self.enabled = ConfigSelection(choices = modes, default = 0)
			self.adapters = [adapter for adapter in iNetwork.getAdapterList() if adapter in ('eth0', 'eth1')]
			self.checkNetwork()
		elif self.index == self.STATE_CHOISE_CHANNELLIST:
			self.enabled = ConfigYesNo(default = True)
			modes = {"19e": "Astra 1", "23e": "Astra 3", "19e-23e": "Astra 1 Astra 3", "19e-23e-28e": "Astra 1 Astra 2 Astra 3", "13e-19e-23e-28e": "Astra 1 Astra 2 Astra 3 Hotbird"}
			self.channellist_type = ConfigSelection(choices = modes, default = "19e")
			self.createMenu()
		elif self.index == self.INSTALL_PLUGINS:
			self.enabled = ConfigYesNo(default = True)
			self.createMenu()
		elif self.index == self.INSTALL_SKINS:
			self.enabled = ConfigYesNo(default = True)
			self.createMenu()
#		elif self.index == self.STATE_CHOISE_SOFTCAM:
#			self.enabled = ConfigYesNo(default = True)
#			modes = {"ncam": _("default") + " (Ncam)", "cccam": "CCcam", "scam": "scam", "oscam": "Oscam"}
#			self.softcam_type = ConfigSelection(choices = modes, default = "ncam")
#			self.createMenu()

	def checkNetwork(self):
		if self.adapters:
			self.adapter = self.adapters.pop(0)
			if iNetwork.getAdapterAttribute(self.adapter, 'up'):
				iNetwork.checkNetworkState(self.checkNetworkStateCallback)
			else:
				iNetwork.restartNetwork(self.restartNetworkCallback)
		else:
			self.createMenu()

	def checkNetworkStateCallback(self, data):
		if data < 3:
			config.misc.installwizard.hasnetwork.value = True
			self.createMenu()
		else:
			self.checkNetwork()

	def restartNetworkCallback(self, retval):
		if retval:
			iNetwork.checkNetworkState(self.checkNetworkStateCallback)
		else:
			self.checkNetwork()

	def createMenu(self):
		try:
			test = self.index
		except:
			return
		self.list = []
		if self.index == self.STATE_UPDATE:
			if config.misc.installwizard.hasnetwork.value:
				ip = ".".join([str(x) for x in iNetwork.getAdapterAttribute(self.adapter, "ip")])
				self.list.append(getConfigListEntry(_("Your internet connection is working (ip: %s)") % ip, self.enabled))
			else:
				self.list.append(getConfigListEntry(_("Your receiver does not have an internet connection"), self.enabled))
		elif self.index == self.STATE_CHOISE_CHANNELLIST:
			self.list.append(getConfigListEntry(_("Install channel list"), self.enabled))
			if self.enabled.value:
				self.list.append(getConfigListEntry(_("Channel list type"), self.channellist_type))
		elif self.index == self.INSTALL_PLUGINS:
			self.list.append(getConfigListEntry(_("Do you want to install plugins"), self.enabled))
		elif self.index == self.INSTALL_SKINS:
			self.list.append(getConfigListEntry(_("Do you want to change the default skin"), self.enabled))
#		elif self.index == self.STATE_CHOISE_SOFTCAM:
#			self.list.append(getConfigListEntry(_("Install softcam"), self.enabled))
#			if self.enabled.value:
#				self.list.append(getConfigListEntry(_("Softcam type"), self.softcam_type))
		self["config"].list = self.list
		self["config"].l.setList(self.list)

	def keyLeft(self):
		if self.index == 0:
			return
		ConfigListScreen.keyLeft(self)
		self.createMenu()

	def keyRight(self):
		if self.index == 0:
			return
		ConfigListScreen.keyRight(self)
		self.createMenu()

	def run(self):
		if self.index == self.STATE_UPDATE:
			if config.misc.installwizard.hasnetwork.value:
				self.session.open(InstallWizardIpkgUpdater, self.index, _('Please wait (updating packages)'), IpkgComponent.CMD_UPDATE)
		elif self.index == self.STATE_CHOISE_CHANNELLIST and self.enabled.value:
			self.session.open(InstallWizardIpkgUpdater, self.index, _('Please wait (downloading channel list)'), IpkgComponent.CMD_REMOVE, {'package': 'enigma2-plugin-settings-henksat-' + self.channellist_type.value})
		elif self.index == self.INSTALL_PLUGINS and self.enabled.value:
			from PluginBrowser import PluginDownloadBrowser
			self.session.open(PluginDownloadBrowser, 0, True, "", "PluginDownloadBrowserWizard")
		elif self.index == self.INSTALL_SKINS and self.enabled.value:
			from SkinSelector import SkinSelector
			self.session.open(SkinSelector, "", "SkinSelectorWizard")
#		elif self.index == self.STATE_CHOISE_SOFTCAM and self.enabled.value:
#			self.session.open(InstallWizardIpkgUpdater, self.index, _('Please wait (downloading softcam)'), IpkgComponent.CMD_INSTALL, {'package': 'enigma2-plugin-softcams-' + self.softcam_type.value})
		return

class InstallWizardIpkgUpdater(Screen):
	skin = """
	<screen position="c-300,c-25" size="600,50" title=" ">
		<widget source="statusbar" render="Label" position="10,5" zPosition="10" size="e-10,30" halign="center" valign="center" font="Regular;22" transparent="1" shadowColor="black" shadowOffset="-1,-1" />
	</screen>"""

	def __init__(self, session, index, info, cmd, pkg = None):
		Screen.__init__(self, session)

		self["statusbar"] = StaticText(info)

		self.pkg = pkg
		self.index = index
		self.state = 0

		self.ipkg = IpkgComponent()
		self.ipkg.addCallback(self.ipkgCallback)

		if self.index == InstallWizard.STATE_CHOISE_CHANNELLIST:
			self.ipkg.startCmd(cmd, {'package': 'enigma2-plugin-settings-*'})
		else:
			self.ipkg.startCmd(cmd, pkg)

	def ipkgCallback(self, event, param):
		if event == IpkgComponent.EVENT_DONE:
			if self.index == InstallWizard.STATE_UPDATE:
				config.misc.installwizard.ipkgloaded.value = True
			elif self.index == InstallWizard.STATE_CHOISE_CHANNELLIST:
				if self.state == 0:
					self.ipkg.startCmd(IpkgComponent.CMD_INSTALL, self.pkg)
					self.state = 1
					return
				else:
					config.misc.installwizard.channellistdownloaded.value = True
					eDVBDB.getInstance().reloadBouquets()
					eDVBDB.getInstance().reloadServicelist()
			self.close()
