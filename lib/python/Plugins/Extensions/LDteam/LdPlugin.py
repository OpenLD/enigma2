from Screens.Screen import Screen
from Screens.Standby import TryQuitMainloop
from Screens.MessageBox import MessageBox
from Screens.Console import Console
from Components.ActionMap import ActionMap
from Components.config import config, ConfigText, configfile
from Components.Sources.List import List
from Components.Label import Label
from Components.PluginComponent import plugins
from Tools.Directories import resolveFilename, SCOPE_CURRENT_SKIN, SCOPE_SKIN_IMAGE, fileExists, pathExists, createDir
from Tools.LoadPixmap import LoadPixmap
from Plugins.Plugin import PluginDescriptor
from os import system, listdir, chdir, getcwd, remove as os_remove
from enigma import eDVBDB

config.misc.fast_plugin_button = ConfigText(default="")

class LDPluginPanel(Screen):
	skin = """
	<screen name="LDPluginPanel" position="center,center" size="800,560" title="Plugins OpenLD">
<ePixmap position="460,10" size="310,165" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/LDteam/images/menu/ld.png" alphatest="blend" transparent="1" />
<widget source="list" render="Listbox" position="10,10" size="750,540" scrollbarMode="showOnDemand">
<convert type="TemplatedMultiContent">
{"template": [
MultiContentEntryText(pos = (60, 1), size = (300, 36), flags = RT_HALIGN_LEFT|RT_VALIGN_CENTER, text = 0),
MultiContentEntryPixmapAlphaTest(pos = (4, 2), size = (36, 36), png = 1),
],
"fonts": [gFont("Regular", 24)],
"itemHeight": 36
}
</convert>
</widget>    
</screen>"""
		
	def __init__(self, session):
		Screen.__init__(self, session)

		self.list = []
		self["list"] = List(self.list)
		self.updateList()

		self["actions"] = ActionMap(["WizardActions", "ColorActions"],
		{
			"ok": self.runPlug,
			"back": self.close,
			#"red": self.keyRed,
			#"green": self.keyGreen,
			#"yellow": self.keyYellow,
			#"blue": self.keyBlue
		}, -1)

	def runPlug(self):
		mysel = self["list"].getCurrent()
		if mysel:
			plugin = mysel[3]
			plugin(session=self.session)

	def updateList(self):
		self.list = [ ]
		self.pluginlist = plugins.getPlugins(PluginDescriptor.WHERE_PLUGINMENU)
		for plugin in self.pluginlist:
			if plugin.icon is None:
				png = LoadPixmap(resolveFilename(SCOPE_SKIN_IMAGE, "skin_default/icons/plugin.png"))
			else:
				png = plugin.icon
			res = (plugin.name, plugin.description, png, plugin)
			self.list.append(res)

		self["list"].list = self.list	

	def keyYellow(self):
		self.session.open(LDAddons)

	def keyRed(self):
		self.session.open(LDSetupFp)

	def keyGreen(self):
		runplug = None
		for plugin in self.list:
			if  plugin[3].name == config.misc.fast_plugin_button.value:
				runplug = plugin[3]
				break

		if runplug is not None:
			runplug(session=self.session)
		else:
			self.session.open(MessageBox, "Fast Plugin not found. You have to setup Fast Plugin before to use this shortcut.", MessageBox.TYPE_INFO)

	def keyBlue(self):
		self.session.open(LDScript)

class LDPl:
	def __init__(self):
		self["LDPl"] = ActionMap( [ "InfobarSubserviceSelectionActions" ],
			{
				"LDPlshow": (self.showLDPl),
			})

	def showLDPl(self):
		self.session.openWithCallback(self.callNabAction, LDPluginPanel)

	def callNabAction(self, *args):
		if len(args):
			(actionmap, context, action) = args
			actionmap.action(context, action)