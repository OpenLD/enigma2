#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from Components.Converter.Converter import Converter
from Components.config import config, ConfigText, ConfigNumber, ConfigDateTime
from Components.Element import cached
from Poll import Poll

class SimpleWeather(Poll, Converter, object):

	def __init__(self, type):
		Converter.__init__(self, type)
		self.type = type
		Poll.__init__(self)
		self.poll_interval = 1100000
		self.poll_enabled = True

	@cached
	def getText(self):
		try:
			if config.plugins.SimpleWeather.enabled.value:
				if self.type == "currentLocation":
					return config.plugins.SimpleWeather.currentLocation.value
				elif self.type == "currentWeatherTemp":
					return config.plugins.SimpleWeather.currentWeatherTemp.value
				elif self.type == "currentWeatherText":
					return config.plugins.SimpleWeather.currentWeatherText.value
				elif self.type == "currentWeatherCode":
					return config.plugins.SimpleWeather.currentWeatherCode.value
				elif self.type == "forecastTodayCode":
					return config.plugins.SimpleWeather.forecastTodayCode.value
				elif self.type == "forecastTodayTempMin":
					return config.plugins.SimpleWeather.forecastTodayTempMin.value + self.getCF()
				elif self.type == "forecastTodayTempMax":
					return config.plugins.SimpleWeather.forecastTodayTempMax.value + self.getCF()
				elif self.type == "forecastTodayText":
					return config.plugins.SimpleWeather.forecastTodayText.value
				elif self.type == "forecastTodayDay":
					return config.plugins.SimpleWeather.forecastTodayDay.value
				elif self.type == "forecastTomorrowCode":
					return config.plugins.SimpleWeather.forecastTomorrowCode.value
				elif self.type == "forecastTomorrowTempMin":
					return config.plugins.SimpleWeather.forecastTomorrowTempMin.value + self.getCF()
				elif self.type == "forecastTomorrowTempMax":
					return config.plugins.SimpleWeather.forecastTomorrowTempMax.value + self.getCF()
				elif self.type == "forecastTomorrowText":
					return config.plugins.SimpleWeather.forecastTomorrowText.value
				elif self.type == "forecastTomorrowDay":
					return config.plugins.SimpleWeather.forecastTomorrowDay.value
				elif self.type == "title":
					return self.getCF() + " | " + config.plugins.SimpleWeather.currentLocation.value
				elif self.type == "CF":
					return self.getCF()
				else:
					return ""
			else:
				return ""
		except:
			return ""

	@cached
	def getBoolean(self):
		if self.type == "currentDataValid":
			return config.plugins.SimpleWeather.currentWeatherDataValid.value
		return False

	@cached
	def getCF(self):
		if config.plugins.SimpleWeather.tempUnit.value == "Fahrenheit":
			return "°"
		else:
			return "°"

	boolean = property(getBoolean)
	text = property(getText)
