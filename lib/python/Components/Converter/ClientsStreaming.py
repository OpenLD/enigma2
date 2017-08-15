from Converter import Converter
from Poll import Poll
from Components.Element import cached
from Components.Sources.StreamService import StreamServiceList
from enigma import eStreamServer
from ServiceReference import ServiceReference
import socket
try:
	from Plugins.Extensions.OpenWebif.controllers.stream import streamList
except:
	streamList = []

class ClientsStreaming(Converter, Poll, object):
	UNKNOWN = -1
	REF = 0
	IP = 1
	NAME = 2
	ENCODER = 3
	NUMBER = 4
	SHORT_ALL = 5
	ALL = 6
	INFO = 7
	INFO_RESOLVE = 8
	INFO_RESOLVE_SHORT = 9
	EXTRA_INFO = 10

	def __init__(self, type):
		Converter.__init__(self, type)
		Poll.__init__(self)
		self.poll_interval = 30000
		self.poll_enabled = True
		if type == "REF":
			self.type = self.REF
		elif type == "IP":
			self.type = self.IP
		elif type == "NAME":
			self.type = self.NAME
		elif type == "ENCODER":
			self.type = self.ENCODER
		elif type == "NUMBER":
			self.type = self.NUMBER
		elif type == "SHORT_ALL":
			self.type = self.SHORT_ALL
		elif type == "ALL":
			self.type = self.ALL
		elif type == "INFO":
			self.type = self.INFO
		elif type == "INFO_RESOLVE":
			self.type = self.INFO_RESOLVE
		elif type == "INFO_RESOLVE_SHORT":
			self.type = self.INFO_RESOLVE_SHORT
		elif type == "EXTRA_INFO":
			self.type = self.EXTRA_INFO
		else:
			self.type = self.UNKNOWN

		self.streamServer = eStreamServer.getInstance()

	@cached
	def getText(self):
		if self.streamServer is None:
			return ""
		if StreamServiceList and streamList is None:
			return ""

		clients = []
		refs = []
		ips = []
		names = []
		encoders = []
		extrainfo = _("ClientIP") + "\t\t" + _("Transcode")  + "\t" + _("Channel")  + "\n"
		info = ""

		for x in self.streamServer.getConnectedClients():
			refs.append((x[1]))
			servicename = ServiceReference(x[1]).getServiceName() or "(unknown service)"
			service_name = servicename
			names.append((service_name))
			ip = x[0]

			ips.append((ip))

			if int(x[2]) == 0:
				strtype = "S"
				encoder = _('NO')
			else:
				strtype = "T"
				encoder = _('YES')

			encoders.append((encoder))

			if self.type == self.INFO_RESOLVE or self.type == self.INFO_RESOLVE_SHORT:
				try:
					raw = socket.gethostbyaddr(ip)
					ip  = raw[0]
				except:
					pass

				if self.type == self.INFO_RESOLVE_SHORT:
					ip, sep, tail = ip.partition('.')

			info += ("%s %-8s %s\n") % (strtype, ip, service_name)

			clients.append((ip, service_name, encoder))

			extrainfo += ("%-8s\t%s\t%s") % (ip, encoder, service_name) +"\n"

		if StreamServiceList and streamList:
			for x in StreamServiceList:
				ip = "ip n/a"
				servicename = "(unknown service)"
				service_name = servicename
				names.append((service_name))
				for stream in streamList:
					if hasattr(stream, 'getService') and stream.getService() and stream.getService().__deref__() == x:
						service_name = ServiceReference(stream.ref.toString()).getServiceName()
						ip = stream.clientIP or ip
			info = ("T %s %s\n") % (ip, service_name)
			clients.append((ip, service_name))
			extrainfo += ("T\t%s\t%s") % (ip, service_name) +"\n"

		if self.type == self.REF:
			return ' '.join(refs)
		elif self.type == self.IP:
			return ' '.join(ips)
		elif self.type == self.NAME:
			return ' '.join(names)
		elif self.type == self.ENCODER:
			return _("Transcoding: ") + ' '.join(encoders)
		elif self.type == self.NUMBER:
			return str(len(clients))
		elif self.type == self.EXTRA_INFO:
			return extrainfo
		elif self.type == self.SHORT_ALL:
			return _("Total clients streaming: %d (%s)") % (len(clients), ' '.join(names))
		elif self.type == self.ALL:
			return '\n'.join(' '.join(elems) for elems in clients)
		elif self.type == self.INFO or self.type == self.INFO_RESOLVE or self.type == self.INFO_RESOLVE_SHORT:
			return info
		else:
			return "(unknown)"

		return ""

	text = property(getText)

	@cached
	def getBoolean(self):
		if self.streamServer is None:
			return False
		if StreamServiceList and streamList is None:
			return  False
		return (self.streamServer.getConnectedClients() or StreamServiceList or streamList) and True or False

	boolean = property(getBoolean)

	def changed(self, what):
		Converter.changed(self, (self.CHANGED_POLL,))

	def doSuspend(self, suspended):
		pass
