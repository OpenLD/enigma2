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
