from Screen import Screen
from Screens.MessageBox import MessageBox
from Components.MenuList import MenuList
from Components.ActionMap import ActionMap
from Components.Button import Button
from Components.Label import Label
from Components.Converter.ClientsStreaming import ClientsStreaming
from Components.Sources.StreamService import StreamServiceList
from Components.config import config
from Components.Sources.StaticText import StaticText
from enigma import eLabel, eTimer, eStreamServer
from ServiceReference import ServiceReference
import os, socket, skin, gettext
try:
	from Plugins.Extensions.OpenWebif.controllers.stream import streamList
except:
	streamList = []


class StreamingClientsInfo(Screen):
	skin ="""<screen name="StreamingClientsInfo" position="center,center" size="720,630" flags="wfNoBorder">
	<eLabel position="center,27" zPosition="-2" size="680,600" backgroundColor="#25062748" />
	<widget source="Title" render="Label" position="center,36" size="540,44" font="Regular;34" valign="top" zPosition="0" halign="center" />
	<widget source="total" render="Label" position="center,104" size="540,50" zPosition="1" font="Regular; 21" halign="left" backgroundColor="#25062748" valign="center" />
	<widget name="menu" font="Regular;20" position="center,164" size="540,368" zPosition="1" />
	<widget source="info" render="Label" position="center,164" size="540,370" zPosition="1" noWrap="1" font="Regular;20" valign="top" />
</screen>"""
	def __init__(self, session):
		Screen.__init__(self, session)
		self.streamServer = eStreamServer.getInstance()
		self.clients = []
		self.DynamicTimer = eTimer()
		self.DynamicTimer.callback.append(self.update_info)
		self.onShow.append(self.update_info)
		self.setTitle(_("Streaming clients info"))

		self["total"] = StaticText()
		self["menu"] = MenuList(self.clients)
		self["info"] = Label()

		self["key_red"] = Button(_("Close"))
		self["key_blue"] = Button(_("Stop Streams"))
		self["actions"] = ActionMap(["ColorActions", "SetupActions", "DirectionActions"],
			{
				"cancel": self.exit,
				"ok": self.exit,
				"red": self.exit,
				"blue": self.stopStreams
			})

		self.onLayoutFinish.append(self.start)

	def exit(self):
		self.stop()
		self.close()

	def start(self):
		if self.update_info not in self.DynamicTimer.callback:
			self.DynamicTimer.callback.append(self.update_info)
		self.DynamicTimer.start(0)

	def stop(self):
		if self.update_info in self.DynamicTimer.callback:
			self.DynamicTimer.callback.remove(self.update_info)
		self.DynamicTimer.stop()
		del self.DynamicTimer

	def update_info(self):
		self.clients = []
		if self.streamServer:
			for x in self.streamServer.getConnectedClients():
				service_name = ServiceReference(x[1]).getServiceName() or "(unknown service)"
				ip = x[0]
				if int(x[2]) == 0:
					strtype = "S"
				else:
					strtype = "T"
				try:
					raw = socket.gethostbyaddr(ip)
					ip = raw[0]
				except:
					pass
				info = ("%s %-8s %s") % (strtype, ip, service_name)
				self.clients.append((info, (x[0], x[1])))
		if StreamServiceList and streamList:
			for x in StreamServiceList:
				ip = "ip n/a"
				service_name = "(unknown service)"
				for stream in streamList:
					if hasattr(stream, 'getService') and stream.getService() and stream.getService().__deref__() == x:
						service_name = ServiceReference(stream.ref.toString()).getServiceName()
						ip = stream.clientIP or ip
			info = ("T %s %s") % (ip, service_name)
			self.clients.append((info,(-1, x)))

		self["total"].setText(_("Total Clients streaming: ") + str(ClientsStreaming("NUMBER").getText()))
		myclients = ClientsStreaming("EXTRA_INFO")
		text = myclients.getText()

		clients = ClientsStreaming("INFO_RESOLVE")
		text = clients.getText()
		self["menu"].setList(self.clients)
		if self.clients:
			self["info"].setText("")
			self["key_blue"].setText(text and _("Stop Streams") or "")
		else:
			self["info"].setText(text or _("No stream clients"))
		self.DynamicTimer.start(4000)

	def stopStreams(self):
		self.update_info()
		streamServer = eStreamServer.getInstance()
		for x in streamServer.getConnectedClients():
			streamServer.stopStream()
		os.system("killall -9 streamproxy 2>/dev/null")
