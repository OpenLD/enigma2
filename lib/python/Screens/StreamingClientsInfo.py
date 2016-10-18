from Screen import Screen
from Components.ActionMap import ActionMap
from Components.Button import Button
from Components.ScrollLabel import ScrollLabel
from Components.Converter.ClientsStreaming import ClientsStreaming
from Components.config import config
from Components.Sources.StaticText import StaticText
import skin
import gettext


class StreamingClientsInfo(Screen):
	skin ="""<screen name="StreamingClientsInfo" position="center,center" size="720,630" flags="wfNoBorder">
	<eLabel position="center,27" zPosition="-2" size="680,600" backgroundColor="#25062748" />
	<widget source="Title" render="Label" position="center,36" size="540,44" font="Regular;35" valign="top" zPosition="0" halign="center" />
	<widget source="total" render="Label" position="center,104" size="540,50" zPosition="1" font="Regular; 22" halign="left" backgroundColor="#25062748" valign="center" />
	<widget source="liste" render="Label" position="center,164" size="540,370" zPosition="1" noWrap="1" font="Regular;21" valign="top" />
	<widget source="ScrollLabel" render="Label" position="0,00" size="540,470" zPosition="2" font="Regular;19" halign="left"/>
</screen>"""
	def __init__(self, session):
		Screen.__init__(self, session)
		self.setTitle(_("Streaming clients info"))

		if ClientsStreaming("NUMBER").getText() == "0":
			self["total"] = StaticText( _("No stream clients") )
			text = ""
		else:
			self["total"] = StaticText( _("Total Clients streaming: ") + ClientsStreaming("NUMBER").getText())
			text = ClientsStreaming("EXTRA_INFO").getText()
			clients = ClientsStreaming("INFO_RESOLVE")
			text = clients.getText()

		self["liste"] = StaticText(text)
		self["ScrollLabel"] = ScrollLabel(text)

		self["key_red"] = Button(_("Close"))
		self["actions"] = ActionMap(["ColorActions", "SetupActions", "DirectionActions"],
			{
				"cancel": self.close,
				"ok": self.close,
				"red": self.close,
				"up": self["ScrollLabel"].pageUp,
				"down": self["ScrollLabel"].pageDown
			})
