from datetime import datetime
from Tools.BoundFunction import boundFunction
from Tools.LoadPixmap import LoadPixmap
from Tools.Directories import resolveFilename, SCOPE_CURRENT_SKIN

notifications = [ ]

notificationAdded = [ ]

# notifications which are currently on screen (and might be closed by similiar notifications)
current_notifications = [ ]

class NotificationQueueEntry():
	def __init__(self, fnc, screen, id, *args, **kwargs):
		self.timestamp = datetime.now()
		self.pending = True
		self.fnc = fnc
		self.screen = screen
		self.id = id
		self.args = args
		self.kwargs = kwargs
		self.domain = "default"

		if kwargs.has_key("domain"):
			if kwargs["domain"]:
				if kwargs["domain"] in notificationQueue.domains:
					self.domain = kwargs["domain"]
				else:
					print "[NotificationQueueEntry] WARNING: domain", kwargs["domain"], "is not registred in notificationQueue!"
			del kwargs["domain"]

		if kwargs.has_key("deferred_callable"):
			if kwargs["deferred_callable"]:
				self.deferred_callable = kwargs["deferred_callable"]
			del kwargs["deferred_callable"]
		else:
			self.deferred_callable = notificationQueue.domains[self.domain]["deferred_callable"]

		if kwargs.has_key("text"):
			self.text = kwargs["text"]
		elif len(args) and isinstance(args, tuple) and isinstance(args[0],basestring):
			self.text = args[0]
		else:
			self.text = screen.__name__
		#print "[NotificationQueueEntry] QueueEntry created", self.timestamp, "function:", self.fnc, "screen:", self.screen, "id:", self.id, "args:", self.args, "kwargs:", self,kwargs, "domain:", self.domain, "text:", self.text

def __AddNotification(fnc, screen, id, *args, **kwargs):
	if ".MessageBox'>" in `screen`:
		kwargs["simple"] = True
	entry = NotificationQueueEntry(fnc, screen, id, *args, **kwargs)
	notificationQueue.addEntry(entry)
	notifications.append((fnc, screen, args, kwargs, id))
	for x in notificationAdded:
		x()

def AddNotification(screen, *args, **kwargs):
	AddNotificationWithCallback(None, screen, *args, **kwargs)

def AddNotificationWithCallback(fnc, screen, *args, **kwargs):
	__AddNotification(fnc, screen, None, *args, **kwargs)

def AddNotificationParentalControl(fnc, screen, *args, **kwargs):
	RemovePopup("Parental control")
	__AddNotification(fnc, screen, "Parental control", *args, **kwargs)

def AddNotificationWithID(id, screen, *args, **kwargs):
	q = notificationQueue
	if q.isVisibleID(id) or q.isPendingID(id):
		print "ignore duplicate notification", id, screen
		return
	__AddNotification(None, screen, id, *args, **kwargs)

def AddNotificationWithIDCallback(fnc, id, screen, *args, **kwargs):
	__AddNotification(fnc, screen, id, *args, **kwargs)

# Entry to only have one pending item with an id.
# Only use this if you don't mind losing the callback for skipped calls.
#
def AddNotificationWithUniqueIDCallback(fnc, id, screen, *args, **kwargs):
	for x in notifications:
		if x[4] and x[4] == id:    # Already there...
			return
	__AddNotification(fnc, screen, id, *args, **kwargs)

# we don't support notifications with callback and ID as this
# would require manually calling the callback on cancelled popups.

def RemovePopup(id):
	# remove similiar notifications
	print "RemovePopup, id =", id
	notificationQueue.removeSameID(id)
	for x in notifications:
		if x[4] and x[4] == id:
			print "(found in notifications)"
			notifications.remove(x)

	for x in current_notifications:
		if x[0] == id:
			print "(found in current notifications)"
			x[1].close()

from Screens.MessageBox import MessageBox

def AddPopup(text, type, timeout, id = None, domain = None):
	if id is not None:
		RemovePopup(id)
	print "AddPopup, id =", id, "domain =", domain
	AddNotificationWithID(id, MessageBox, text = text, type = type, timeout = timeout, close_on_any_key = True, domain = domain)

def AddPopupWithCallback(fnc, text, type, timeout, id = None, domain = None):
	if id is not None:
		RemovePopup(id)
	print "AddPopup, id =", id, "domain =", domain
	AddNotificationWithIDCallback(fnc, id, MessageBox, text = text, type = type, timeout = timeout, close_on_any_key = False, domain = domain)

ICON_DEFAULT = LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, 'skin_default/icons/marker.png'))
ICON_MAIL = LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, 'skin_default/icons/notification_mail.png'))
ICON_TIMER = LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, 'skin_default/icons/clock.png'))

class NotificationQueue():
	def __init__(self):
		self.queue = []
		self.__screen = None

		# notifications which are currently on screen (and might be closed by similiar notifications)
		self.current = [ ]

		# functions which will be called when new notification is added
		self.addedCB = [ ]

		self.domains = { "default": { "name": _("unspecified"), "icon": ICON_DEFAULT, "deferred_callable": False } }

	def registerDomain(self, key, name, icon = ICON_DEFAULT, deferred_callable = False):
		if not key in self.domains:
			self.domains[key] = { "name": name, "icon": icon, "deferred_callable": deferred_callable }

	def addEntry(self, entry):
		assert isinstance(entry, NotificationQueueEntry)

		self.queue.append(entry)
		for x in self.addedCB:
			x()

	def removeSameID(self, id):
		for entry in self.queue:
			if entry.pending and entry.id == id:
				print "(found in notifications)"
				self.queue.remove(entry)

		for entry, dlg in self.current:
			if entry.id == id:
				print "(found in current notifications)"
				dlg.close()

	def getPending(self, domain = None):
		res = []
		for entry in self.queue:
			if entry.pending and (domain == None or entry.domain == domain):
				res.append(entry)
		return res

	def popNotification(self, parent, entry = None):
		if entry:
			performCB = entry.deferred_callable
		else:
			pending = self.getPending()
			if len(pending):
				entry = pending[0]
			else:
				return
			performCB = True

		print "[NotificationQueue::popNotification] domain", entry.domain, "deferred_callable:", entry.deferred_callable

		if performCB and entry.kwargs.has_key("onSessionOpenCallback"):
			entry.kwargs["onSessionOpenCallback"]()
			del entry.kwargs["onSessionOpenCallback"]

		entry.pending = False
		if performCB and entry.fnc is not None:
			dlg = parent.session.openWithCallback(entry.fnc, entry.screen, *entry.args, **entry.kwargs)
		else:
			dlg = parent.session.open(entry.screen, *entry.args, **entry.kwargs)

		# remember that this notification is currently active
		d = (entry, dlg)
		self.current.append(d)
		dlg.onClose.append(boundFunction(self.__notificationClosed, d))

	def __notificationClosed(self, d):
		#print "[NotificationQueue::__notificationClosed]", d, self.current
		self.current.remove(d)

notificationQueue = NotificationQueue()
