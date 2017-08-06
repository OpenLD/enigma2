#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

from Renderer import Renderer
from Components.VariableText import VariableText
import urllib2
from enigma import eLabel, ePixmap, eTimer, eListboxPythonMultiContent, gFont, eEnv, getDesktop, pNavigation
from datetime import datetime
from Components.Element import cached
from xml.dom.minidom import parseString
from Components.config import config, configfile, ConfigSubsection, ConfigSelection, ConfigNumber, ConfigSelectionNumber, ConfigYesNo, ConfigText, ConfigInteger
from threading import Timer, Thread
from types import *
from time import time, strftime, localtime

g_updateRunning = False

def initWeatherConfig():
	config.plugins.SimpleWeather = ConfigSubsection()

	#SimpleWeather
	config.plugins.SimpleWeather.enabled = ConfigYesNo(default=False)
	config.plugins.SimpleWeather.refreshInterval = ConfigNumber(default=60)
	config.plugins.SimpleWeather.lastUpdated = ConfigText(default="2001-01-01 01:01:01")
	config.plugins.SimpleWeather.woeid = ConfigNumber(default=758816) #Location (visit http://weather.open-store.net/)
	config.plugins.SimpleWeather.tempUnit = ConfigSelection(default="Celsius", choices = [
		("Celsius", _("Celsius")),
		("Fahrenheit", _("Fahrenheit"))
	])

	## RENDERER CONFIG:
	config.plugins.SimpleWeather.currentWeatherDataValid = ConfigYesNo(default=False)
	config.plugins.SimpleWeather.currentLocation = ConfigText(default="N/A")
	config.plugins.SimpleWeather.currentWeatherCode = ConfigText(default="(")
	config.plugins.SimpleWeather.currentWeatherText = ConfigText(default="N/A")
	config.plugins.SimpleWeather.currentWeatherTemp = ConfigText(default="0")

	config.plugins.SimpleWeather.forecastTodayCode = ConfigText(default="(")
	config.plugins.SimpleWeather.forecastTodayDay = ConfigText(default="N/A")
	config.plugins.SimpleWeather.forecastTodayText = ConfigText(default="N/A")
	config.plugins.SimpleWeather.forecastTodayTempMin = ConfigText(default="0")
	config.plugins.SimpleWeather.forecastTodayTempMax = ConfigText(default="0")

	config.plugins.SimpleWeather.forecastTomorrowCode = ConfigText(default="(")
	config.plugins.SimpleWeather.forecastTomorrowDay = ConfigText(default="N/A")
	config.plugins.SimpleWeather.forecastTomorrowText = ConfigText(default="N/A")
	config.plugins.SimpleWeather.forecastTomorrowTempMin = ConfigText(default="0")
	config.plugins.SimpleWeather.forecastTomorrowTempMax = ConfigText(default="0")

	config.plugins.SimpleWeather.forecast2daysCode = ConfigText(default="(")
	config.plugins.SimpleWeather.forecast2daysDay = ConfigText(default="N/A")
	config.plugins.SimpleWeather.forecast2daysText = ConfigText(default="N/A")
	config.plugins.SimpleWeather.forecast2daysTempMin = ConfigText(default="0")
	config.plugins.SimpleWeather.forecast2daysTempMax = ConfigText(default="0")

	config.plugins.SimpleWeather.forecast3daysCode = ConfigText(default="(")
	config.plugins.SimpleWeather.forecast3daysDay = ConfigText(default="N/A")
	config.plugins.SimpleWeather.forecast3daysText = ConfigText(default="N/A")
	config.plugins.SimpleWeather.forecast3daysTempMin = ConfigText(default="0")
	config.plugins.SimpleWeather.forecast3daysTempMax = ConfigText(default="0")

	config.plugins.SimpleWeather.forecast4daysCode = ConfigText(default="(")
	config.plugins.SimpleWeather.forecast4daysDay = ConfigText(default="N/A")
	config.plugins.SimpleWeather.forecast4daysText = ConfigText(default="N/A")
	config.plugins.SimpleWeather.forecast4daysTempMin = ConfigText(default="0")
	config.plugins.SimpleWeather.forecast4daysTempMax = ConfigText(default="0")

	config.plugins.SimpleWeather.save()
	configfile.save()

initWeatherConfig()

class SimpleWeatherWidget(Renderer, VariableText):

	def __init__(self):
		Renderer.__init__(self)
		VariableText.__init__(self)
		self.getWeather()

	def changed(self, what):
		if self.instance:
			if what[0] != self.CHANGED_CLEAR:
				if config.plugins.SimpleWeather.enabled.value:
					self.instance.show()
					self.getWeather()
				else:
					self.instance.hide()
	GUI_WIDGET = eLabel

	def startTimer(self, refresh=False):
		# skip if weather-widget is already up to date
		tdelta = datetime.now() - datetime.strptime(config.plugins.SimpleWeather.lastUpdated.value,"%Y-%m-%d %H:%M:%S")
		if int(tdelta.seconds) < (config.plugins.SimpleWeather.refreshInterval.value * 60):   ##### 1=60 for testing purpose #####
			return

	def onShow(self):
		self.text = config.plugins.SimpleWeather.currentWeatherCode.value

	def getWeather(self):
		self.startTimer()

		# skip if weather-widget is disabled
		if config.plugins.SimpleWeather.enabled.getValue() is False:
			config.plugins.SimpleWeather.currentWeatherDataValid.value = False
			return

		global g_updateRunning
		if g_updateRunning:
			woeid = config.plugins.SimpleWeather.woeid.value
			#print "[SimpleWeather] lookup for ID " + str(woeid) + " skipped, allready running..."
			return
		g_updateRunning = True
		Thread(target = self.getWeatherThread).start()

	def getWeatherThread(self):
		global g_updateRunning
		woeid = config.plugins.SimpleWeather.woeid.value
		#print "[SimpleWeather] lookup for ID " + str(woeid)
		url = "https://query.yahooapis.com/v1/public/yql?q=select%20item%20from%20weather.forecast%20where%20woeid%3D%22"+str(woeid)+"%22&format=xml"
		# where location in (select id from weather.search where query="oslo, norway")
		try:
			file = urllib2.urlopen(url, timeout=10)
			data = file.read()
			file.close()
		except Exception as error:
			print "Cant get weather data: %r" % error
			# cancel weather function
			config.plugins.SimpleWeather.lastUpdated.value = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
			config.plugins.SimpleWeather.currentWeatherDataValid.value = False
			g_updateRunning = False
			return

		dom = parseString(data)
		try:
			title = self.getText(dom.getElementsByTagName('title')[0].childNodes)
		except IndexError as error:
			print "Cant get weather data: %r" % error
			g_updateRunning = False

		config.plugins.SimpleWeather.currentLocation.value = str(title).split(',')[0].replace("Conditions for ","")

		currentWeather = dom.getElementsByTagName('yweather:condition')[0]
		t=time()
		lastday = strftime("%d %b %Y", localtime(t-3600*24)).strip("0")
		currday = strftime("%d %b %Y", localtime(t)).strip("0")
		currentWeatherDate = currentWeather.getAttributeNode('date').nodeValue
		config.plugins.SimpleWeather.currentWeatherDataValid.value = True
		currentWeatherCode = currentWeather.getAttributeNode('code')
		config.plugins.SimpleWeather.currentWeatherCode.value = self.ConvertCondition(currentWeatherCode.nodeValue)
		currentWeatherTemp = currentWeather.getAttributeNode('temp')
		config.plugins.SimpleWeather.currentWeatherTemp.value = self.getTemp(currentWeatherTemp.nodeValue)
		currentWeatherText = currentWeather.getAttributeNode('text')
		config.plugins.SimpleWeather.currentWeatherText.value = currentWeatherText.nodeValue

		n = 0
		currentWeather = dom.getElementsByTagName('yweather:forecast')[n]
		if lastday in currentWeather.getAttributeNode('date').nodeValue and currday in currentWeatherDate:
			n = 1
			currentWeather = dom.getElementsByTagName('yweather:forecast')[n]
		currentWeatherCode = currentWeather.getAttributeNode('code')
		config.plugins.SimpleWeather.forecastTodayCode.value = self.ConvertCondition(currentWeatherCode.nodeValue)
		currentWeatherTemp = currentWeather.getAttributeNode('high')
		config.plugins.SimpleWeather.forecastTodayTempMax.value = self.getTemp(currentWeatherTemp.nodeValue)
		currentWeatherTemp = currentWeather.getAttributeNode('low')
		config.plugins.SimpleWeather.forecastTodayTempMin.value = self.getTemp(currentWeatherTemp.nodeValue)
		currentWeatherText = currentWeather.getAttributeNode('text')
		config.plugins.SimpleWeather.forecastTodayText.value = currentWeatherText.nodeValue
		currentWeatherDay = currentWeather.getAttributeNode('day')
		config.plugins.SimpleWeather.forecastTodayDay.value = currentWeatherDay.nodeValue

		currentWeather = dom.getElementsByTagName('yweather:forecast')[n + 1]
		currentWeatherCode = currentWeather.getAttributeNode('code')
		config.plugins.SimpleWeather.forecastTomorrowCode.value = self.ConvertCondition(currentWeatherCode.nodeValue)
		currentWeatherTemp = currentWeather.getAttributeNode('high')
		config.plugins.SimpleWeather.forecastTomorrowTempMax.value = self.getTemp(currentWeatherTemp.nodeValue)
		currentWeatherTemp = currentWeather.getAttributeNode('low')
		config.plugins.SimpleWeather.forecastTomorrowTempMin.value = self.getTemp(currentWeatherTemp.nodeValue)
		currentWeatherText = currentWeather.getAttributeNode('text')
		config.plugins.SimpleWeather.forecastTomorrowText.value = currentWeatherText.nodeValue
		currentWeatherDay = currentWeather.getAttributeNode('day')
		config.plugins.SimpleWeather.forecastTomorrowDay.value = currentWeatherDay.nodeValue

		currentWeather = dom.getElementsByTagName('yweather:forecast')[2]
		currentWeatherCode = currentWeather.getAttributeNode('code')
		config.plugins.SimpleWeather.forecast2daysCode.value = self.ConvertCondition(currentWeatherCode.nodeValue)
		currentWeatherTemp = currentWeather.getAttributeNode('high')
		config.plugins.SimpleWeather.forecast2daysTempMax.value = self.getTemp(currentWeatherTemp.nodeValue)
		currentWeatherTemp = currentWeather.getAttributeNode('low')
		config.plugins.SimpleWeather.forecast2daysTempMin.value = self.getTemp(currentWeatherTemp.nodeValue)
		currentWeatherText = currentWeather.getAttributeNode('text')
		config.plugins.SimpleWeather.forecast2daysText.value = currentWeatherText.nodeValue
		currentWeatherDay = currentWeather.getAttributeNode('day')
		config.plugins.SimpleWeather.forecast2daysDay.value = currentWeatherDay.nodeValue

		currentWeather = dom.getElementsByTagName('yweather:forecast')[3]
		currentWeatherCode = currentWeather.getAttributeNode('code')
		config.plugins.SimpleWeather.forecast3daysCode.value = self.ConvertCondition(currentWeatherCode.nodeValue)
		currentWeatherTemp = currentWeather.getAttributeNode('high')
		config.plugins.SimpleWeather.forecast3daysTempMax.value = self.getTemp(currentWeatherTemp.nodeValue)
		currentWeatherTemp = currentWeather.getAttributeNode('low')
		config.plugins.SimpleWeather.forecast3daysTempMin.value = self.getTemp(currentWeatherTemp.nodeValue)
		currentWeatherText = currentWeather.getAttributeNode('text')
		config.plugins.SimpleWeather.forecast3daysText.value = currentWeatherText.nodeValue
		currentWeatherDay = currentWeather.getAttributeNode('day')
		config.plugins.SimpleWeather.forecast3daysDay.value = currentWeatherDay.nodeValue

		currentWeather = dom.getElementsByTagName('yweather:forecast')[4]
		currentWeatherCode = currentWeather.getAttributeNode('code')
		config.plugins.SimpleWeather.forecast4daysCode.value = self.ConvertCondition(currentWeatherCode.nodeValue)
		currentWeatherTemp = currentWeather.getAttributeNode('high')
		config.plugins.SimpleWeather.forecast4daysTempMax.value = self.getTemp(currentWeatherTemp.nodeValue)
		currentWeatherTemp = currentWeather.getAttributeNode('low')
		config.plugins.SimpleWeather.forecast4daysTempMin.value = self.getTemp(currentWeatherTemp.nodeValue)
		currentWeatherText = currentWeather.getAttributeNode('text')
		config.plugins.SimpleWeather.forecast4daysText.value = currentWeatherText.nodeValue
		currentWeatherDay = currentWeather.getAttributeNode('day')
		config.plugins.SimpleWeather.forecast4daysDay.value = currentWeatherDay.nodeValue

		self.save()

		g_updateRunning = False

	def save(self):
		config.plugins.SimpleWeather.save()
		configfile.save()

	def getText(self,nodelist):
		rc = []
		for node in nodelist:
			if node.nodeType == node.TEXT_NODE:
				rc.append(node.data)
		return ''.join(rc)

	def ConvertCondition(self, c):
		c = int(c)
		condition = "("
		if c == 0 or c == 1 or c == 2:
			condition = "S"
		elif c == 3 or c == 4:
			condition = "Z"
		elif c == 5  or c == 6 or c == 7 or c == 18:
			condition = "U"
		elif c == 8 or c == 10 or c == 25:
			condition = "G"
		elif c == 9:
			condition = "Q"
		elif c == 11 or c == 12 or c == 40:
			condition = "R"
		elif c == 13 or c == 14 or c == 15 or c == 16 or c == 41 or c == 46 or c == 42 or c == 43:
			condition = "W"
		elif c == 17 or c == 35:
			condition = "X"
		elif c == 19:
			condition = "F"
		elif c == 20 or c == 21 or c == 22:
			condition = "L"
		elif c == 23 or c == 24:
			condition = "S"
		elif c == 26 or c == 44:
			condition = "N"
		elif c == 27 or c == 29:
			condition = "I"
		elif c == 28 or c == 30:
			condition = "H"
		elif c == 31 or c == 33:
			condition = "C"
		elif c == 32 or c == 34:
			condition = "B"
		elif c == 36:
			condition = "B"
		elif c == 37 or c == 38 or c == 39 or c == 45 or c == 47:
			condition = "0"
		else:
			condition = ")"
		return str(condition)

	def getTemp(self,temp):
		if config.plugins.SimpleWeather.tempUnit.value == "Fahrenheit":
			return str(int(round(float(temp),0)))
		else:
			celsius = (float(temp) - 32 ) * 5 / 9
			return str(int(round(float(celsius),0)))
