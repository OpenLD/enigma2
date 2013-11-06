from Plugins.Plugin import PluginDescriptor

def main(session, **kwargs):
	from LdBlue import LDBluePanel
	session.open(LDBluePanel)

def Plugins(**kwargs):
	return PluginDescriptor(name = "LDteam", description = "Lets you execute your LDPanels", where = PluginDescriptor.WHERE_EXTENSIONSMENU, fnc = main)
