
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.ChoiceBox import ChoiceBox
from Screens.Standby import TryQuitMainloop
from Components.ActionMap import ActionMap
from Components.Sources.List import List
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.ConfigList import ConfigListScreen
from Components.config import getConfigListEntry, ConfigSelection, NoSave
from Tools.LoadPixmap import LoadPixmap
from Tools.Directories import fileExists, pathExists, createDir, resolveFilename, SCOPE_CURRENT_SKIN
from os import system, listdir, remove as os_remove, rename as os_rename, stat as os_stat
from enigma import eTimer
import stat


class LDDevicesPanel(Screen):
	skin = """
	<screen name="LDDevicesPanel" position="240,100" size="800,560" title="OpenLD - Devices Manager">
<widget source="list" render="Listbox" position="10,0" size="780,510" scrollbarMode="showOnDemand" >
<convert type="TemplatedMultiContent">
{"template": [
MultiContentEntryText(pos = (90, 0), size = (690, 30), font=0, text = 0),
MultiContentEntryText(pos = (110, 30), size = (670, 50), font=1, flags = RT_VALIGN_TOP, text = 1),
MultiContentEntryPixmapAlphaTest(pos = (0, 0), size = (80, 80), png = 2),
],
"fonts": [gFont("Regular", 24),gFont("Regular", 20)],
"itemHeight": 85
}
</convert>
</widget>
<widget name="lab1" zPosition="2" position="50,40" size="700,40" font="Regular;24" halign="center" transparent="1"/>
<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/LDteam/images/buttons/red200x30.png" position="200,520" size="200,30" alphatest="on" />
<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/LDteam/images/buttons/yellow150x30.png" position="450,520" size="150,30" alphatest="on" />
<widget name="key_red" position="200,522" zPosition="1" size="200,25" font="Regular;20" halign="center" backgroundColor="transpBlack" transparent="1" />
<widget name="key_yellow" position="450,522" zPosition="1" size="150,25" font="Regular;20" halign="center" backgroundColor="transpBlack" transparent="1" />
</screen>"""
	
	def __init__(self, session):
		Screen.__init__(self, session)
		self["key_red"] = Label(_("Mountpoints"))
		self["key_yellow"] = Label(_("Cancel"))
		self["lab1"] = Label("Por favor, espere mientras se escanean los dispositivos ...")
		
		self.list = []
		self["list"] = List(self.list)
		
		self["actions"] = ActionMap(["WizardActions", "ColorActions"],
		{
			"back": self.close,
			"red": self.mapSetup,
			"yellow": self.close
		})
		
		self.activityTimer = eTimer()
		self.activityTimer.timeout.get().append(self.updateList)
		self.gO()
	
	def gO(self):
		paths = ["/media/hdd","/media/usb","/media/downloads","/media/music","/media/personal","/media/photo","/media/video"]
		for path in paths:
			if not pathExists(path):
				createDir(path)
# hack !
		self.activityTimer.start(1)
		
	def updateList(self):
		self.activityTimer.stop()
		self.list = [ ]
		self.conflist = [ ]
		rc = system("blkid > /tmp/blkid.log")
		
		f = open("/tmp/blkid.log",'r')
		for line in f.readlines():
			parts = line.strip().split()
			device = parts[0][5:-2]
			partition = parts[0][5:-1]
			pos = line.find("UUID") + 6
			end = line.find('"', pos)
			uuid = line[pos:end]
			dtype = self.get_Dtype(device)
			category = dtype[0]
			png = LoadPixmap(dtype[1])
			size = self.get_Dsize(device, partition)
			model = self.get_Dmodel(device)
			mountpoint = self.get_Dpoint(uuid)
			name = "%s: %s" % (category, model)
			description = " Dispositivo: %s  Capacidad: %s\n Punto Montaje: %s" % (parts[0], size, mountpoint)
			self.list.append((name, description, png))
			description = "%s  %s  %s" % (name, size, partition)
			self.conflist.append((description, uuid))
			
		self["list"].list = self.list
		self["lab1"].hide()
		os_remove("/tmp/blkid.log")
		
		
	def get_Dpoint(self, uuid):
		point = "NO MAPEADO"
		f = open("/etc/fstab",'r')
		for line in f.readlines():
			if line.find(uuid) != -1:
				parts = line.strip().split()
				point = parts[1]
				break
		f.close()
		return point
		
	def get_Dmodel(self, device):
		model = "Generico"
		filename = "/sys/block/%s/device/vendor" % (device)
		if fileExists(filename):
			vendor = file(filename).read().strip()
			filename = "/sys/block/%s/device/model" % (device)
			mod = file(filename).read().strip()
			model = "%s %s" % (vendor, mod)
		return model
		
	def get_Dsize(self, device, partition):
		size = "0"
		filename = "/sys/block/%s/%s/size" % (device, partition)
		if fileExists(filename):
			size = int(file(filename).read().strip())
			cap = size / 1000 * 512 / 1000
			size = "%d.%03d GB" % (cap/1000, cap%1000)
		return size
		
		
	def get_Dtype(self, device):
		pixpath = resolveFilename(SCOPE_CURRENT_SKIN, "")
		if pixpath == "/usr/share/enigma2/":
			pixpath = "/usr/share/enigma2/skin_default/"
		
		name = "USB"
		pix = pixpath + "icons/dev_usb.png"
		filename = "/sys/block/%s/removable" % (device)
		if fileExists(filename):
			if file(filename).read().strip() == "0":
				name = "DISCO DURO"
				pix = pixpath + "icons/dev_hdd.png"
				
		return name, pix
		
		
	def mapSetup(self):
		self.session.openWithCallback(self.close, LDSetupDevicePanelConf, self.conflist)
						

class LDSetupDevicePanelConf(Screen, ConfigListScreen):
	skin = """
<screen name="LDSetupDevicePanelConf" position="center,center" size="902,340" title="Setup Device Panel">
<widget name="config" position="30,10" size="840,275" scrollbarMode="showOnDemand"/>
<widget name="Linconn" position="30,285" size="840,20" font="Regular;18" halign="center" valign="center" backgroundColor="#9f1313"/>
<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/LDteam/images/buttons/red250x35.png" position="180,300" size="250,35" alphatest="on"/>
<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/LDteam/images/buttons/green250x35.png" position="470,300" size="250,35" alphatest="on"/>
<widget name="key_red" position="180,300" zPosition="1" size="250,35" font="Regular;20" halign="center" valign="center" backgroundColor="transpBlack" transparent="1"/>
<widget name="key_green" position="470,300" zPosition="1" size="250,35" font="Regular;20" halign="center" valign="center" backgroundColor="transpBlack" transparent="1"/>
</screen>"""
	def __init__(self, session, devices):
		Screen.__init__(self, session)
		
		self.list = []
		ConfigListScreen.__init__(self, self.list)
		self["key_red"] = Label(_("Save"))
		self["key_green"] = Label(_("Cancel"))
		self["Linconn"] = Label("Por favor, espere mientras se escanean los dispositivos...")
		
		self["actions"] = ActionMap(["WizardActions", "ColorActions"],
		{
			"red": self.savePoints,
			"green": self.close,
			"back": self.close

		})
		
		self.devices = devices
		self.updateList()
	
	
	def updateList(self):
		self.list = []
		for device in self.devices:
			item = NoSave(ConfigSelection(default = "No mapeado", choices = self.get_Choices()))
			item.value = self.get_currentPoint(device[1])
			res = getConfigListEntry(device[0], item, device[1])
			self.list.append(res)
		
		self["config"].list = self.list
		self["config"].l.setList(self.list)
		self["Linconn"].hide()



	def get_currentPoint(self, uuid):
		point = "No mapeado"
		f = open("/etc/fstab",'r')
		for line in f.readlines():
			if line.find(uuid) != -1:
				parts = line.strip().split()
				point = parts[1].strip()
				break
		f.close()
		return point

	def get_Choices(self):
		choices = [("No mapeado", "No mapeado")]
		folders = listdir("/media")
		for f in folders:
			if f == "net":
				continue
			c = "/media/" + f
			choices.append((c,c))
		return choices
			
		

	def savePoints(self):
		f = open("/etc/fstab",'r')
		out = open("/etc/fstab.tmp", "w")
		for line in f.readlines():
			if line.find("UUID") != -1 or len(line) < 6:
				continue
			out.write(line)
		for x in self["config"].list:
			if x[1].value != "No mapeado":
				line = "UUID=%s    %s    auto   defaults    0  0\n" % (x[2], x[1].value)
				out.write(line)

		out.write("\n")
		f.close()
		out.close()
		os_rename("/etc/fstab.tmp", "/etc/fstab")
		message = "Cambios realizados al dispositivo, necesita reiniciar para tener efecto\nReiniciar su Receptor ahora?"
		self.session.openWithCallback(self.restBo, MessageBox, message, MessageBox.TYPE_YESNO)
			
	def restBo(self, answer):
		if answer is True:
			self.session.open(TryQuitMainloop, 2)
		else:
			self.close()
	
	
class LDSwap(Screen):
	skin = """
	<screen position="339,160" size="602,410" title="OpenLD - Swap File Manager">
<widget name="lab1" position="50,10" size="260,30" font="Regular;20" transparent="1"/>
<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/LDteam/images/buttons/red150x30.png" position="45,360" size="150,30" alphatest="on"/>
<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/LDteam/images/buttons/green150x30.png" position="225,360" size="150,30" alphatest="on"/>
<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/LDteam/images/buttons/yellow150x30.png" position="405,360" size="150,30" alphatest="on"/>
<widget name="key_red" position="45,362" zPosition="1" size="150,25" font="Regular;20" halign="center" backgroundColor="transpBlack" transparent="1"/>
<widget name="key_green" position="225,362" zPosition="1" size="150,25" font="Regular;20" halign="center" backgroundColor="transpBlack" transparent="1"/>
<widget name="key_yellow" position="405,362" zPosition="1" size="150,25" font="Regular;20" halign="center" backgroundColor="transpBlack" transparent="1"/>
	</screen>"""
	
	def __init__(self, session):
		Screen.__init__(self, session)
		
		self["lab1"] = Label(_("Estado Swap: desactivado"))
		self["key_red"] = Label(_("Create"))
		self["key_green"] = Label(_("Remove"))
		self["key_yellow"] = Label(_("Close"))
		
		self["actions"] = ActionMap(["WizardActions", "ColorActions"],
		{
			"back": self.close,
			"red": self.keyRed,
			"green": self.keyGreen,
			"yellow": self.close
		})

		self.onLayoutFinish.append(self.updateSwap)
		
	
	def updateSwap(self):
		self.swap_file = ""
		swapinfo = "Estado Swap: desactivado"
		f = open("/proc/swaps",'r')
 		for line in f.readlines():
			if line.find('swapfile') != -1:
				parts = line.split()
				self.swap_file = parts[0].strip()
				size = int(parts[2].strip()) / 1024
				swapinfo = "Estado Swap: activo\nArchivo Swap: %s \nCapacidad Swap: %d M \nUso Swap: %s Kb" % (self.swap_file, size, parts[3].strip())

		f.close()
		self["lab1"].setText(swapinfo)
		
		
	def keyGreen(self):
		if self.swap_file:
			cmd = "swapoff %s" % self.swap_file
			rc = system(cmd)
			try:
				os_remove("/etc/ld_swap")
				os_remove(self.swap_file)
			except:
				pass
			self.updateSwap()
		else:
			self.session.open(MessageBox, "Swap desactivada.", MessageBox.TYPE_INFO)	
	
	def keyRed(self):
		if self.swap_file:
			self.session.open(MessageBox, "Swap activada.\nElimine el actual archivo swap antes de crear uno nuevo.", MessageBox.TYPE_INFO)
		else:
			options =[]
			f = open("/proc/mounts",'r')
			for line in f.readlines():
				if line.find('/media/sd') != -1:
					continue
				elif line.find('/media/') != -1:
					if line.find(' ext') != -1:
						parts = line.split()
						options.append([parts[1].strip(), parts[1].strip()])
			f.close()
			if len(options) == 0:
				self.session.open(MessageBox, "Lo sentimos, no hay dispositivo valido encontrado.\nAsegurate de que tu dispositivo fue formateado bajo formato LINUX (ext2,ext3,ext4).\nPor favor, use  Formatear USB y Admin Dispositivos para preparar y planificar tu memoria USB.", MessageBox.TYPE_INFO)
			else:
				self.session.openWithCallback(self.selectSize,ChoiceBox, title="Selecionar capacidad archivo Swap:", list=options)
	

	def selectSize(self, device):
		if device:
			self.new_swap = device[1] + "/swapfile"
			options = [['8 MB', '8192'], ['16 MB', '16384'], ['32 MB', '32768'], ['64 MB', '65536'], ['128 MB', '131072'], ['256 MB', '262144'], ['512 MB', '524288'], ['1024 MB', '1048576']]	
			self.session.openWithCallback(self.swapOn,ChoiceBox, title="Selecionar capacidad archivo Swap:", list=options)
			
		
	def swapOn(self, size):
		if size:
			cmd = "dd if=/dev/zero of=%s bs=1024 count=%s 2>/dev/null" % (self.new_swap, size[1])
			rc = system(cmd)
			if rc == 0:
				cmd = "mkswap %s" % (self.new_swap)
				rc = system(cmd)
				cmd = "swapon %s" % (self.new_swap)
				rc = system(cmd)
				out = open("/etc/ld_swap", "w")
				out.write(self.new_swap)
				out.close()
				self.session.open(MessageBox, "Archivo Swap creado correctamente.", MessageBox.TYPE_INFO)
				self.updateSwap()
			else:
				self.session.open(MessageBox, "La creacion de el archivo Swap ha fallado. Compruebe si hay espacio disponible.", MessageBox.TYPE_INFO)
			

