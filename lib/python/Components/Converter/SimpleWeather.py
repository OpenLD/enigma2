#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

from Components.Converter.Converter import Converter
from Components.config import config, ConfigText, ConfigNumber, ConfigDateTime
from Components.Element import cached
from Poll import Poll

class SimpleWeather(Poll, Converter, object):

	def __init__(self, type):
		Converter.__init__(self, type)
		self.type = type
		Poll.__init__(self)
		self.poll_interval = 60000
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
				elif self.type == "forecast2daysCode":
					return config.plugins.SimpleWeather.forecast2daysCode.value
				elif self.type == "forecast2daysTempMin":
					return config.plugins.SimpleWeather.forecast2daysTempMin.value + self.getCF()
				elif self.type == "forecast2daysTempMax":
					return config.plugins.SimpleWeather.forecast2daysTempMax.value + self.getCF()
				elif self.type == "forecast2daysText":
					return config.plugins.SimpleWeather.forecast2daysText.value
				elif self.type == "forecast2daysDay":
					return config.plugins.SimpleWeather.forecast2daysDay.value
				elif self.type == "forecast3daysCode":
					return config.plugins.SimpleWeather.forecast3daysCode.value
				elif self.type == "forecast3daysTempMin":
					return config.plugins.SimpleWeather.forecast3daysTempMin.value + self.getCF()
				elif self.type == "forecast3daysTempMax":
					return config.plugins.SimpleWeather.forecast3daysTempMax.value + self.getCF()
				elif self.type == "forecast3daysText":
					return config.plugins.SimpleWeather.forecast3daysText.value
				elif self.type == "forecast3daysDay":
					return config.plugins.SimpleWeather.forecast3daysDay.value
				elif self.type == "forecast4daysCode":
					return config.plugins.SimpleWeather.forecast4daysCode.value
				elif self.type == "forecast4daysTempMin":
					return config.plugins.SimpleWeather.forecast4daysTempMin.value + self.getCF()
				elif self.type == "forecast4daysTempMax":
					return config.plugins.SimpleWeather.forecast4daysTempMax.value + self.getCF()
				elif self.type == "forecast4daysText":
					return config.plugins.SimpleWeather.forecast4daysText.value
				elif self.type == "forecast4daysDay":
					return config.plugins.SimpleWeather.forecast4daysDay.value
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

	def getCF(self):
		if config.plugins.SimpleWeather.tempUnit.value == "Fahrenheit":
			return "°"
		else:
			return "°"

	boolean = property(getBoolean)
	text = property(getText)
