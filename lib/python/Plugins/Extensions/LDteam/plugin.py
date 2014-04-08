from Plugins.Plugin import PluginDescriptor
from Screens.PluginBrowser import *
	
def LDpanel(menuid, **kwargs):
	if menuid == "mainmenu":
		return [("Blue Panel", main, "LDBluePanel", 11)]
	else:
		return []
		
def main(session, **kwargs):
	from LdBlue import LDBluePanel
	session.open(LDBluePanel)
		
def Plugins(**kwargs):
	return [

	#// show panel in Main Menu
	PluginDescriptor(name="Blue Panel", description="Blue panel - OpenLD", where = PluginDescriptor.WHERE_MENU, fnc = LDpanel),
	#// show panel in EXTENSIONS Menu
	PluginDescriptor(name="Blue Panel", description="Blue panel - OpenLD", where = PluginDescriptor.WHERE_EXTENSIONSMENU, fnc = main) ]

