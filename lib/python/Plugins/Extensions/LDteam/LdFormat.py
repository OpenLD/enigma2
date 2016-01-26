#!/usr/bin/env python
# -*- coding: UTF-8 -*-
##
##
## Copyright (c) 2012-2015 OpenLD
##          Javier Sayago <admin@lonasdigital.com>
## Contact: javilonas@esp-desarrolladores.com
##
## Licensed under the Apache License, Version 2.0 (the "License");
## you may not use this file except in compliance with the License.
## You may obtain a copy of the License at
##
##    http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.
##
##########################################################################
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.Console import Console
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.Pixmap import Pixmap
from Tools.Directories import fileExists
from os import system, listdir


class LD_UsbFormat(Screen):
	skin = """
	<screen position="center,center" size="580,350" title="OpenLD - Usb Format Wizard">
		<widget name="lab1" position="10,10" size="560,280" font="Regular;20" valign="top" transparent="1"/>
		<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/LDteam/images/buttons/red150x30.png" position="100,300" size="150,30" alphatest="on" />
		<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/LDteam/images/buttons/green150x30.png" position="340,300" size="150,30" alphatest="on" />
		<widget name="key_red" position="100,300" zPosition="1" size="150,30" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
		<widget name="key_green" position="340,300" zPosition="1" size="150,30" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />
	</screen>"""
	def __init__(self, session):
		Screen.__init__(self, session)

		msg = """Este asistente le ayudara a formatear su USB para Linux (EXT2).
Por favor, asegurese de que su unidad USB no se encuentra conectada al Receptor antes de continuar.
Si su unidad USB ya se encuentra conectada y montada, tiene que apagar el receptor, retirar el USB y encender el receptor.
Pulse el boton rojo para continuar cuando crea estar listo y su USB se encuentre desconectado.
"""
		self["key_red"] = Label(_("Continue >>"))
		self["key_green"] = Label(_("Cancel"))
		self["lab1"] = Label(msg)

		self["actions"] = ActionMap(["WizardActions", "ColorActions"],
		{
			"back": self.close,
			"red": self.step_Bump,
			"green": self.close
		})
		self.step = 1
		self.devices = []
		self.device = None


	def stepOne(self):
		msg = """Conecte el USB al Receptor
Pulse el boton rojo para continuar cuando se encuentre listo.
"""
		self.devices = self.get_Devicelist()
		self["lab1"].setText(msg)
		self.step = 2

	def stepTwo(self):
		msg = """El asistente va intentar identificar el USB conectado.
Pulse el boton rojo para continuar.
"""
		self["lab1"].setText(msg)
		self.step = 3

	def stepThree(self):
		newdevices = self.get_Devicelist()
		for d in newdevices:
			if d not in self.devices:
				self.device = d
		if self.device is None:
			self.wizClose("Lo sentimos, no hemos detectado ningun USB nuevo.\nAsegurese de seguir las instrucciones del asistente.")
		else:
			msg = self.get_Deviceinfo(self.device)
			msg +="\nAdvertencia: Todo los datos en el USB se eliminaran.\nSeguro que desea formatear este dispositivo?\n"
			self["lab1"].setText(msg)
			self.step = 4

	def stepFour(self):
		device = "/dev/" + self.device
		partition = device + "1"
		cmd = "umount %s" % (partition)
		rc = system(cmd)
		cmd = "umount %s" % (device)
		rc = system(cmd)
		if fileExists(partition):
			self.do_Format()
		else:
			self.do_Part()


	def do_Part(self):
		device = "/dev/%s" % (self.device)
		cmd = "echo -e 'Particiones: %s \n\n'" % (device)
		cmd2 = 'printf "0,\n;\n;\n;\ny\n" | sfdisk -f %s' % (device)
		self.session.open(Console, title="Particionamiento...", cmdlist=[cmd, cmd2], finishedCallback = self.do_Format)

	def do_Format(self):
		device = "/dev/%s1" % (self.device)
		cmd = "echo -e 'Formato: %s \n\n'" % (device)
		cmd2 = "/sbin/mkfs.ext2 %s" % (device)
		self.session.open(Console, title="Formateando...", cmdlist=[cmd, cmd2], finishedCallback = self.succesS)

	def step_Bump(self):
		if self.step == 1:
			self.stepOne()
		elif self.step == 2:
			self.stepTwo()
		elif self.step == 3:
			self.stepThree()
		elif self.step == 4:
			self.stepFour()

	def get_Devicelist(self):
		devices = []
		folder = listdir("/sys/block")
		for f in folder:
			if f.find('sd') != -1:
				devices.append(f)
		return devices

	def get_Deviceinfo(self, device):
		info = vendor = model = size = ""
		filename = "/sys/block/%s/device/vendor" % (device)
		if fileExists(filename):
			vendor = file(filename).read().strip()
			filename = "/sys/block/%s/device/model" % (device)
			model = file(filename).read().strip()
			filename = "/sys/block/%s/size" % (device)
			size = int(file(filename).read().strip())
			cap = size / 1000 * 512 / 1000
			size = "%d.%03d GB" % (cap/1000, cap%1000)
		info = "Modelo: %s %s\nCapacidad: %s\nDispositivo: /dev/%s" % (vendor, model, size, device)
		return info



	def succesS(self):
		self.wizClose("USB formateado.\nAhora puede utilizar el Admin de Dispositivos para (Mapear) asignar el punto de montaje que desea (media/hdd media/usb).")

	def wizClose(self, msg):
		self.session.openWithCallback(self.close, MessageBox, msg, MessageBox.TYPE_INFO)
