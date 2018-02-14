#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from Renderer import Renderer
from Components.VariableText import VariableText
#import library to do http requests:
import urllib2
from enigma import eLabel, ePixmap
#import easy to use xml parser called minidom:
from xml.dom.minidom import parseString
from Components.config import config, configfile, ConfigSubsection, ConfigSelection, ConfigNumber, ConfigSelectionNumber, ConfigYesNo, ConfigText, ConfigDateTime, ConfigInteger
from threading import Timer, Thread
from time import time, strftime, localtime

g_updateRunning = False

def initWeatherConfig():
	config.plugins.SimpleWeather = ConfigSubsection()

	#SimpleWeather
	config.plugins.SimpleWeather.enabled = ConfigYesNo(default=False)
	config.plugins.SimpleWeather.woeid = ConfigNumber(default=779304) #Location (visit http://weather.open-store.net/)
	config.plugins.SimpleWeather.tempUnit = ConfigSelection(default="Celsius", choices = [
		("Celsius", _("Celsius")),
		("Fahrenheit", _("Fahrenheit"))
	])
	config.plugins.SimpleWeather.refreshInterval = ConfigSelectionNumber(default = 90, stepwidth = 1, min = 0, max = 1440, wraparound = True)

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

	config.plugins.SimpleWeather.save()
	configfile.save()

initWeatherConfig()

class SimpleWeatherWidget(Renderer, VariableText, Thread):

	def __init__(self):
		Renderer.__init__(self)
		VariableText.__init__(self)
		Thread.__init__(self)
		self.woeid = config.plugins.SimpleWeather.woeid.value
		self.Timer = None
		self.refreshcnt = 0
		self.getWeather()

	GUI_WIDGET = eLabel

	def __del__(self):
		try:
			if self.Timer is not None:
				self.Timer.cancel()
		except AttributeError:
			pass

	def startTimer(self, refresh=False):
		seconds = int(config.plugins.SimpleWeather.refreshInterval.value) * 60

		if seconds < 60:
			seconds = 300

		if refresh:
			if self.refreshcnt >= 6:
				self.refreshcnt = 0
				seconds=300
			else:
				seconds=10

		if self.Timer:
			self.Timer.cancel()
			self.Timer = None

		self.Timer = Timer(seconds, self.getWeather)
		self.Timer.start()

	def onShow(self):
		self.text = config.plugins.SimpleWeather.currentWeatherCode.value

	def getWeather(self):
		self.startTimer()

		# skip if weather-widget is disabled
		if config.plugins.SimpleWeather.enabled.value == "False":
			config.plugins.SimpleWeather.currentWeatherDataValid.value = False
			return

		global g_updateRunning
		if g_updateRunning:
			print "[SimpleWeather] lookup for ID " + str(self.woeid) + " skipped, allready running..."
			return
		g_updateRunning = True
		Thread(target = self.getWeatherThread).start()

	def getWeatherThread(self):
		global g_updateRunning
		print "[SimpleWeather] lookup for ID " + str(self.woeid)
		url = "http://query.yahooapis.com/v1/public/yql?q=select%20item%20from%20weather.forecast%20where%20woeid%3D%22"+str(self.woeid)+"%22&format=xml"

		# where location in (select id from weather.search where query="oslo, norway")
		try:
			file = urllib2.urlopen(url, timeout=2)
			data = file.read()
			file.close()
		except Exception as error:
			print "Cant get weather data: %r" % error

			# cancel weather function
			config.plugins.SimpleWeather.currentWeatherDataValid.value = False
			g_updateRunning = False
			return


		dom = parseString(data)
		try:
			title = self.getText(dom.getElementsByTagName('title')[0].childNodes)
		except IndexError as error:
			print "Cant get weather data: %r" % error
			g_updateRunning = False
			self.startTimer(True,30)
			if self.check:
				#text = "%s\n%s|" % (str(error),data)
				text = "%s|" % str(error)
				self.writeCheckFile(text)
			return

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

		self.save()
		g_updateRunning = False
		self.refreshcnt = 0

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
