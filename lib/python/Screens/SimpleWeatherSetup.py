#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from Screens.Screen import Screen
from Components.Renderer import SimpleWeatherWidget
from Components.Label import Label
from Components.config import ConfigSelection, getConfigListEntry, config, configfile, ConfigSubsection, ConfigNumber, ConfigSelectionNumber, ConfigYesNo, ConfigText
from Components.ConfigList import ConfigListScreen
from Components.ActionMap import ActionMap
from Components.Sources.StaticText import StaticText

class SimpleWeatherSetup(Screen, ConfigListScreen):
	skin = """
		<screen name="SimpleWeatherSetup" position="160,150" size="450,200" title="Weather Setup">
			<ePixmap pixmap="skin_default/buttons/red.png" position="10,0" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/green.png" position="300,0" size="140,40" alphatest="on" />
			<widget source="key_red" render="Label" position="10,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
			<widget source="key_green" render="Label" position="300,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />
			<widget name="config" position="10,44" size="430,146" />
		</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		self["key_red"] = StaticText(_("Cancel"))
		self["key_green"] = StaticText(_("Save"))

		ConfigListScreen.__init__(self, [])
		self.initConfigList()

		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"], {
			"green": self.save,
			"red": self.exit,
			"cancel": self.close},-1)

	def save(self):
		config.plugins.SimpleWeather.save()
		configfile.save()
		self.close()

	def initConfigList(self):
		self.list = []
		self.list.append(getConfigListEntry(_("Show Weather Widget"), config.plugins.SimpleWeather.enabled))
		self.list.append(getConfigListEntry(_(" ")))
		self.list.append(getConfigListEntry(_("Refresh Interval (min)"), config.plugins.SimpleWeather.refreshInterval))
		self.list.append(getConfigListEntry(_("Weather ID"), config.plugins.SimpleWeather.woeid))
		self.list.append(getConfigListEntry(_("Get your local Weather ID on weather.open-store.net")))
		self.list.append(getConfigListEntry(_(" ")))
		self.list.append(getConfigListEntry(_("Unit"), config.plugins.SimpleWeather.tempUnit))
		self["config"].setList(self.list)

	def exit(self):
		for x in self["config"].list:
			if len(x) > 1:
				x[1].cancel()
			else:
				pass
		self.close()
