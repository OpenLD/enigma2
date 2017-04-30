from Screen import Screen
from Components.ActionMap import ActionMap
from Components.Button import Button
from Components.ScrollLabel import ScrollLabel
from Components.Converter.ClientsStreaming import ClientsStreaming
from Components.config import config
from Components.Sources.StaticText import StaticText
from enigma import eLabel, eTimer, eStreamServer
import skin
import gettext


class StreamingClientsInfo(Screen):
	skin ="""<screen name="StreamingClientsInfo" position="center,center" size="720,630" flags="wfNoBorder">
	<eLabel position="center,27" zPosition="-2" size="680,600" backgroundColor="#25062748" />
	<widget source="Title" render="Label" position="center,36" size="540,44" font="Regular;34" valign="top" zPosition="0" halign="center" />
	<widget source="total" render="Label" position="center,104" size="540,50" zPosition="1" font="Regular; 21" halign="left" backgroundColor="#25062748" valign="center" />
	<widget source="liste" render="Label" position="center,164" size="540,370" zPosition="1" noWrap="1" font="Regular;20" valign="top" />
	<widget source="ScrollLabel" render="Label" position="0,00" size="540,470" zPosition="2" font="Regular;18" halign="left"/>
</screen>"""
	def __init__(self, session):
		Screen.__init__(self, session)
		self.DynamicTimer = eTimer()
		self.DynamicTimer.callback.append(self.update_info)
		self.onShow.append(self.update_info)
		self.setTitle(_("Streaming clients info"))

		self["total"] = StaticText()
		self["liste"] = StaticText()
		self["ScrollLabel"] = ScrollLabel()

		self["key_red"] = Button(_("Close"))
		self["actions"] = ActionMap(["ColorActions", "SetupActions", "DirectionActions"],
			{
				"cancel": self.exit,
				"ok": self.exit,
				"red": self.exit,
				"up": self["ScrollLabel"].pageUp,
				"down": self["ScrollLabel"].pageDown
			})

		self.onLayoutFinish.append(self.update_info)

	def exit(self):
		self.stop()
		self.close()

	def start(self):
		if self.update_info not in self.DynamicTimer.callback:
			self.DynamicTimer.callback.append(self.update_info)

	def stop(self):
		if self.update_info in self.DynamicTimer.callback:
			self.DynamicTimer.callback.remove(self.update_info)
		self.DynamicTimer.stop()
		del self.DynamicTimer

	def update_info(self):
		self["total"].setText(_("Total Clients streaming: ") + str(ClientsStreaming("NUMBER").getText()))
		myclients = ClientsStreaming("EXTRA_INFO")
		text = myclients.getText()

		clients = ClientsStreaming("INFO_RESOLVE")
		text = clients.getText()
		self["liste"].setText(text or _("No stream clients"))
		self["ScrollLabel"].setText(text or _("No stream clients"))
		self.DynamicTimer.start(5000)
