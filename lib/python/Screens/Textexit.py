# -*- coding: utf-8 -*-
from enigma import eConsoleAppContainer
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.ScrollLabel import ScrollLabel
from enigma import getDesktop
from Components.Sources.StaticText import StaticText

class Textexit(Screen):
	global HD_es
	try:
		sz_w = getDesktop(0).size().width()
	except:
		sz_w = 720
	if sz_w == 1280:
		HD_es = True
	else:
		HD_es = False

	if HD_es:
		skin = """
	<screen name="TextOut" position="160,100" size="920,565" transparent="0" title="TextOut...">
		<widget name="text" position="20,0" size="900,565" transparent="0" font="Regular;20" />
	</screen>"""

	else:
		skin = """
	<screen name="TextOut" position="50,60" size="620,450" title="TextOut...">
		<widget name="text" position="5,0" size="610,440" font="Regular;18" />
	</screen>"""

	def __init__(self, session, title = "Console", cmdlist = None, finishedCallback = None, closeOnSuccess = False):
		Screen.__init__(self, session)

		self.finishedCallback = finishedCallback
		self.closeOnSuccess = closeOnSuccess

		self["text"] = ScrollLabel("")
		self["actions"] = ActionMap(["WizardActions", "DirectionActions"], 
		{
			"ok": self.cancel,
			"back": self.cancel,
			"up": self["text"].pageUp,
			"down": self["text"].pageDown
		}, -1)

		self.cmdlist = cmdlist
		self.newtitle = title

		self.onShown.append(self.updateTitle)

		self.container = eConsoleAppContainer()
		self.run = 0
		self.container.appClosed.append(self.runFinished)
		self.container.dataAvail.append(self.dataAvail)
		self.onLayoutFinish.append(self.startRun) # dont start before gui is finished

	def updateTitle(self):
		self.setTitle(self.newtitle)

	def startRun(self):
		self["text"].setText("")
		print "Console: executing in run", self.run, " the command:", self.cmdlist[self.run]
		if self.container.execute(self.cmdlist[self.run]): #start of container application failed...
			self.runFinished(-1) # so we must call runFinished manual

	def runFinished(self, retval):
		self.run += 1
		if self.run != len(self.cmdlist):
			if self.container.execute(self.cmdlist[self.run]): #start of container application failed...
				self.runFinished(-1) # so we must call runFinished manual
		else:
			str = self["text"].getText()

			self["text"].setText(str)

			if self.finishedCallback is not None:
				self.finishedCallback()
			if not retval and self.closeOnSuccess:
				self.cancel()

	def cancel(self):
		if self.run == len(self.cmdlist):
			self.close()
			self.container.appClosed.remove(self.runFinished)
			self.container.dataAvail.remove(self.dataAvail)

	def dataAvail(self, str):
		self["text"].setText(self["text"].getText() + str)
