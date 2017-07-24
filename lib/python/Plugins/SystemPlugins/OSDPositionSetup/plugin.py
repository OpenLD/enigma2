from Screens.Screen import Screen
from Components.ConfigList import ConfigListScreen
from Components.config import config, configfile, ConfigSubsection, ConfigInteger, ConfigSlider, getConfigListEntry
from Tools.Directories import fileExists
from boxbranding import getBoxType, getBrandOEM

config.plugins.OSDPositionSetup = ConfigSubsection()
config.plugins.OSDPositionSetup.dst_left = ConfigInteger(default = 0)
config.plugins.OSDPositionSetup.dst_width = ConfigInteger(default = 720)
config.plugins.OSDPositionSetup.dst_top = ConfigInteger(default = 0)
config.plugins.OSDPositionSetup.dst_height = ConfigInteger(default = 576)

def setPosition(dst_left, dst_width, dst_top, dst_height):
	if dst_left + dst_width > 720:
		dst_width = 720 - dst_left
	if dst_top + dst_height > 576:
		dst_height = 576 - dst_top
	try:
		if getBrandOEM() in ('dreambox'):
			open("/proc/stb/vmpeg/0/dst_left", "w").write('%08x' % dst_left)
		else:
			open("/proc/stb/fb/dst_left", "w").write('%08x' % dst_left)
		if getBrandOEM() in ('dreambox'):
			open("/proc/stb/vmpeg/0/dst_width", "w").write('%08x' % dst_width)
		else:
			open("/proc/stb/fb/dst_width", "w").write('%08x' % dst_width)
		if getBrandOEM() in ('dreambox'):
			open("/proc/stb/vmpeg/0/dst_top", "w").write('%08x' % dst_top)
		else:
			open("/proc/stb/fb/dst_top", "w").write('%08x' % dst_top)
		if getBrandOEM() in ('dreambox'):
			open("/proc/stb/vmpeg/0/dst_height", "w").write('%08x' % dst_height)
		else:
			open("/proc/stb/fb/dst_height", "w").write('%08x' % dst_height)
	except:
		return

def setConfiguredPosition():
	setPosition(int(config.plugins.OSDPositionSetup.dst_left.value), int(config.plugins.OSDPositionSetup.dst_width.value), int(config.plugins.OSDPositionSetup.dst_top.value), int(config.plugins.OSDPositionSetup.dst_height.value))

def main(session, **kwargs):
	from overscanwizard import OverscanWizard
	session.open(OverscanWizard, timeOut=False)

def startup(reason, **kwargs):
	setConfiguredPosition()

def OSDPosSetup(menuid, **kwargs):
	if menuid == "osd_menu":
		return [(_("Position and size"), main, "osd_position_setup", 80)]
	else:
		return []

def Plugins(**kwargs):
	from Plugins.Plugin import PluginDescriptor
	return [PluginDescriptor(name = "Overscan Wizard", description = "", where = PluginDescriptor.WHERE_SESSIONSTART, fnc = startup),
		PluginDescriptor(name = "Overscan Wizard", description = _("Wizard to arrange the overscan"), where = PluginDescriptor.WHERE_MENU, fnc = OSDPosSetup)]
