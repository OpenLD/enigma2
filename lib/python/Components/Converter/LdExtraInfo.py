#!/usr/bin/env python
# -*- coding: UTF-8 -*-
##
##
## Copyright (c) 2012-2016 OpenLD
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
from enigma import iServiceInformation, eServiceReference, eServiceCenter, iPlayableService, iPlayableServicePtr, eTimer, getBestPlayableServiceReference, eDVBFrontendParametersSatellite
from Components.Converter.Converter import Converter
from Components.Element import cached
from Components.config import config
from Tools.Directories import fileExists, resolveFilename, SCOPE_CURRENT_SKIN, SCOPE_PLUGINS
from Tools.Transponder import ConvertToHumanReadable, getChannelNumber
from Tools.GetEcmInfo import GetEcmInfo
from Components.Converter.ChannelNumbers import channelnumbers
from Components.Converter.Poll import Poll
from Poll import Poll
import NavigationInstance
import os
import time

def addspace(text):
	if text:
		text += "  "
	return text

class LdExtraInfo(Poll, Converter, object):
	def __init__(self, type):
		Converter.__init__(self, type)
		Poll.__init__(self)
		self.type = type
		self.poll_interval = 1000
		self.poll_enabled = True
		self.caid_data = (
			( "0x100",  "0x1ff", "Seca",     "S" ),
			( "0x500",  "0x5ff", "Via",      "V" ),
			( "0x600",  "0x6ff", "Irdeto",   "I" ),
			( "0x900",  "0x9ff", "NDS",      "ND" ),
			( "0xb00",  "0xbff", "Conax",    "CO" ),
			( "0xd00",  "0xdff", "CryptoW",  "CW" ),
			( "0xe00",  "0xeff", "PowerVU",  "P" ),
			("0x1000", "0x10FF", "Tandberg", "TB" ),
			("0x1700", "0x17ff", "Beta",     "B" ),
			("0x1800", "0x18ff", "Nagra",    "N" ),
			("0x2600", "0x2600", "Biss",     "BI" ),
			("0x4ae0", "0x4ae1", "Dre",      "D" ),
			("0x4aee", "0x4aee", "BulCrypt", "B1" ),
			("0x5581", "0x5581", "BulCrypt", "B2" )
		)
		self.ecmdata = GetEcmInfo()
		self.feraw = self.fedata = self.updateFEdata = None

	def getCryptoInfo(self, info):
		if info.getInfo(iServiceInformation.sIsCrypted) == 1:
			data = self.ecmdata.getEcmData()
			self.current_source = data[0]
			self.current_caid = data[1]
			self.current_provid = data[2]
			self.current_ecmpid = data[3]
		else:
			self.current_source = ""
			self.current_caid = "0"
			self.current_provid = "0"
			self.current_ecmpid = "0"

	def GetEcmInfo2(self):
		data = {}
		try:
			ecm = open('/tmp/ecm.info', 'rb').readlines()
			info = {}
			for line in ecm:
				d = line.split(':', 1)
				if len(d) > 1:
					info[d[0].strip()] = d[1].strip()

			data['system'] = info.get('system', '')
			data['caid'] = info.get('caid', '0')
			data['pid'] = info.get('pid', '0')
			data['provider'] = info.get('provider', '')
			data['provid'] = info.get('provid', '')
			if data['provider'] == '':
				data['provider'] = info.get('prov', ' ')
			data['chid'] = info.get('chid', '0')
			data['using'] = info.get('using', '')
			data['decode'] = info.get('decode', '')
			data['source'] = info.get('source', '')
			data['reader'] = info.get('reader', '')
			data['address'] = info.get('address', 'Unknown')
			data['address_from'] = info.get('from', 'Unknown')
			data['from'] = info.get('from', 'Unknown')
			data['protocol'] = info.get('protocol', '')
			data['hops'] = info.get('hops', '0')
			data['share'] = info.get('share', '')
			data['ecm_time'] = info.get('ecm time', '?')
			data['cw0'] = info.get('cw0', '0')
			data['cw1'] = info.get('cw1', '0')
		except:
			data['system'] = ''
			data['caid'] = '0x00'
			data['pid'] = '0x00'
			data['provider'] = ''
			data['provid'] = ''
			data['chid'] = '0x00'
			data['using'] = ''
			data['decode'] = ''
			data['source'] = ''
			data['reader'] = ''
			data['address'] = ''
			data['address_from'] = ''
			data['from'] = ''
			data['protocol'] = ''
			data['hops'] = '0'
			data['share'] = ''
			data['ecm_time'] = '0'
			data['cw0'] = '0'
			data['cw1'] = '0'

		return data

	def get_caName(self):
		try:
			f = open("/etc/CurrentLdCamName",'r')
			name = f.readline().strip()
			f.close()
		except:
			name = "Common Interface"
		return name

	def get_Ecmtext(self):
		ecmtext = ''
		if fileExists('/tmp/ecm.info'):
			f = open('/tmp/ecm.info', 'r')
			for line in f.readlines():
				line = line.replace('\n', '')
				line = line.strip()
				if len(line) > 3:
					ecmtext = ecmtext + line + '\n'
			f.close()
		if len(ecmtext) < 5:
			ecmtext = '\n\n    ' + _('Ecm info not available.')
		return str(ecmtext)

	def createCryptoBar(self, info):
		res = ""
		available_caids = info.getInfoObject(iServiceInformation.sCAIDs)

		for caid_entry in self.caid_data:
			if int(caid_entry[0], 16) <= int(self.current_caid, 16) <= int(caid_entry[1], 16):
				color="\c0000??00"
			else:
				color = "\c007?7?7?"
				try:
					for caid in available_caids:
						if int(caid_entry[0], 16) <= caid <= int(caid_entry[1], 16):
							color="\c00????00"
				except:
					pass

			if color != "\c007?7?7?" or caid_entry[4]:
				if res: res += " "
				res += color + caid_entry[3]

		res += "\c00??????"
		return res

	def createCryptoSeca(self, info):
		available_caids = info.getInfoObject(iServiceInformation.sCAIDs)
		if int('0x100', 16) <= int(self.current_caid, 16) <= int('0x1ff', 16):
			color="\c004c7d3f"
		else:
			color = "\c009?9?9?"
			try:
				for caid in available_caids:
					if int('0x100', 16) <= caid <= int('0x1ff', 16):
						color="\c00eeee00"
			except:
				pass
		res = color + 'S'
		res += "\c00??????"
		return res

	def createCryptoVia(self, info):
		available_caids = info.getInfoObject(iServiceInformation.sCAIDs)
		if int('0x500', 16) <= int(self.current_caid, 16) <= int('0x5ff', 16):
			color="\c004c7d3f"
		else:
			color = "\c009?9?9?"
			try:
				for caid in available_caids:
					if int('0x500', 16) <= caid <= int('0x5ff', 16):
						color="\c00eeee00"
			except:
				pass
		res = color + 'V'
		res += "\c00??????"
		return res

	def createCryptoIrdeto(self, info):
		available_caids = info.getInfoObject(iServiceInformation.sCAIDs)
		if int('0x600', 16) <= int(self.current_caid, 16) <= int('0x6ff', 16):
			color="\c004c7d3f"
		else:
			color = "\c009?9?9?"
			try:
				for caid in available_caids:
					if int('0x600', 16) <= caid <= int('0x6ff', 16):
						color="\c00eeee00"
			except:
				pass
		res = color + 'I'
		res += "\c00??????"
		return res

	def createCryptoNDS(self, info):
		available_caids = info.getInfoObject(iServiceInformation.sCAIDs)
		if int('0x900', 16) <= int(self.current_caid, 16) <= int('0x9ff', 16):
			color="\c004c7d3f"
		else:
			color = "\c009?9?9?"
			try:
				for caid in available_caids:
					if int('0x900', 16) <= caid <= int('0x9ff', 16):
						color="\c00eeee00"
			except:
				pass
		res = color + 'NDS'
		res += "\c00??????"
		return res

	def createCryptoConax(self, info):
		available_caids = info.getInfoObject(iServiceInformation.sCAIDs)
		if int('0xb00', 16) <= int(self.current_caid, 16) <= int('0xbff', 16):
			color="\c004c7d3f"
		else:
			color = "\c009?9?9?"
			try:
				for caid in available_caids:
					if int('0xb00', 16) <= caid <= int('0xbff', 16):
						color="\c00eeee00"
			except:
				pass
		res = color + 'CO'
		res += "\c00??????"
		return res

	def createCryptoCryptoW(self, info):
		available_caids = info.getInfoObject(iServiceInformation.sCAIDs)
		if int('0xd00', 16) <= int(self.current_caid, 16) <= int('0xdff', 16):
			color="\c004c7d3f"
		else:
			color = "\c009?9?9?"
			try:
				for caid in available_caids:
					if int('0xd00', 16) <= caid <= int('0xdff', 16):
						color="\c00eeee00"
			except:
				pass
		res = color + 'CW'
		res += "\c00??????"
		return res

	def createCryptoPowerVU(self, info):
		available_caids = info.getInfoObject(iServiceInformation.sCAIDs)
		if int('0xe00', 16) <= int(self.current_caid, 16) <= int('0xeff', 16):
			color="\c004c7d3f"
		else:
			color = "\c009?9?9?"
			try:
				for caid in available_caids:
					if int('0xe00', 16) <= caid <= int('0xeff', 16):
						color="\c00eeee00"
			except:
				pass
		res = color + 'P'
		res += "\c00??????"
		return res

	def createCryptoTandberg(self, info):
		available_caids = info.getInfoObject(iServiceInformation.sCAIDs)
		if int('0x1010', 16) <= int(self.current_caid, 16) <= int('0x1010', 16):
			color="\c004c7d3f"
		else:
			color = "\c009?9?9?"
			try:
				for caid in available_caids:
					if int('0x1010', 16) <= caid <= int('0x1010', 16):
						color="\c00eeee00"
			except:
				pass
		res = color + 'T'
		res += "\c00??????"
		return res

	def createCryptoBeta(self, info):
		available_caids = info.getInfoObject(iServiceInformation.sCAIDs)
		if int('0x1700', 16) <= int(self.current_caid, 16) <= int('0x17ff', 16):
			color="\c004c7d3f"
		else:
			color = "\c009?9?9?"
			try:
				for caid in available_caids:
					if int('0x1700', 16) <= caid <= int('0x17ff', 16):
						color="\c00eeee00"
			except:
				pass
		res = color + 'B'
		res += "\c00??????"
		return res

	def createCryptoNagra(self, info):
		available_caids = info.getInfoObject(iServiceInformation.sCAIDs)
		if int('0x1800', 16) <= int(self.current_caid, 16) <= int('0x18ff', 16):
			color="\c004c7d3f"
		else:
			color = "\c009?9?9?"
			try:
				for caid in available_caids:
					if int('0x1800', 16) <= caid <= int('0x18ff', 16):
						color="\c00eeee00"
			except:
				pass
		res = color + 'N'
		res += "\c00??????"
		return res

	def createCryptoBiss(self, info):
		available_caids = info.getInfoObject(iServiceInformation.sCAIDs)
		if int('0x2600', 16) <= int(self.current_caid, 16) <= int('0x26ff', 16):
			color="\c004c7d3f"
		else:
			color = "\c009?9?9?"
			try:
				for caid in available_caids:
					if int('0x2600', 16) <= caid <= int('0x26ff', 16):
						color="\c00eeee00"
			except:
				pass
		res = color + 'BI'
		res += "\c00??????"
		return res

	def createCryptoDre(self, info):
		available_caids = info.getInfoObject(iServiceInformation.sCAIDs)
		if int('0x4ae0', 16) <= int(self.current_caid, 16) <= int('0x4ae1', 16):
			color="\c004c7d3f"
		else:
			color = "\c009?9?9?"
			try:
				for caid in available_caids:
					if int('0x4ae0', 16) <= caid <= int('0x4ae1', 16):
						color="\c00eeee00"
			except:
				pass
		res = color + 'DC'
		res += "\c00??????"
		return res

	def createCryptoSpecial(self, info):
		caid_name = _("Free To Air")
		try:
			for caid_entry in self.caid_data:
				if int(caid_entry[0], 16) <= int(self.current_caid, 16) <= int(caid_entry[1], 16):
					caid_name = caid_entry[2]
					break
			return caid_name + ":%04x:%04x:%04x:%04x" % (int(self.current_caid,16), int(self.current_provid,16), info.getInfo(iServiceInformation.sSID), int(self.current_ecmpid,16))
		except:
			pass
		return ""

	def createCryptoNameCaid(self, info):
		is_crypted = info.getInfo(iServiceInformation.sIsCrypted)
		if is_crypted != 1:
			return _("Free To Air")
		caid_name = _("Encrypt")
		try:
			for caid_entry in self.caid_data:
				if int(self.current_caid,16) == 0:
					return caid_name
				elif int(caid_entry[0], 16) <= int(self.current_caid, 16) <= int(caid_entry[1], 16):
					caid_name = caid_entry[2] 
					break
			return caid_name + ":%04x" % (int(self.current_caid,16))
		except:
			pass
		return ""

	def createResolution(self, info):
		xres = info.getInfo(iServiceInformation.sVideoWidth)
		if xres == -1:
			return ""
		yres = info.getInfo(iServiceInformation.sVideoHeight)
		mode = ("i", "p", "", " ")[info.getInfo(iServiceInformation.sProgressive)]
		fps  = str((info.getInfo(iServiceInformation.sFrameRate) + 500) / 1000)
		if int(fps) <= 0:
			fps = ""
		return str(xres) + "x" + str(yres) + mode + fps

	def createVideoCodec(self, info):
		return ("MPEG2", "MPEG4 H.264", "MPEG1", "MPEG4-VC", "VC1", "VC1-SM", "HEVC H.265", "")[info.getInfo(iServiceInformation.sVideoType)]

	def createServiceRef(self, info):
		ref = info.getInfoString(iServiceInformation.sServiceref)
		if ref < 0 : ref = 0
		return "Ref: " + str(ref)

	def createPIDInfo(self, info):
		vpid = info.getInfo(iServiceInformation.sVideoPID)
		apid = info.getInfo(iServiceInformation.sAudioPID)
		pcrpid = info.getInfo(iServiceInformation.sPCRPID)
		sidpid = info.getInfo(iServiceInformation.sSID)
		tsid = info.getInfo(iServiceInformation.sTSID)
		onid = info.getInfo(iServiceInformation.sONID)
		if vpid < 0 : vpid = 0
		if apid < 0 : apid = 0
		if pcrpid < 0 : pcrpid = 0
		if sidpid < 0 : sidpid = 0
		if tsid < 0 : tsid = 0
		if onid < 0 : onid = 0
		return "Pid: %d-%d:%05d:%04d:%04d:%04d" % (onid, tsid, sidpid, vpid, apid, pcrpid)

	def createTransponderInfo(self, fedata, feraw):
		if "DVB-T" in feraw.get("tuner_type"):
			tmp = addspace(self.createChannelNumber(fedata, feraw)) + self.createFrequency(fedata) + "/" + self.createPolarization(fedata)
		else:
			tmp = addspace(self.createFrequency(fedata)) + addspace(self.createPolarization(fedata))
		return addspace(self.createTunerSystem(fedata)) + tmp + addspace(self.createSymbolRate(fedata, feraw)) + addspace(self.createFEC(fedata, feraw)) \
			+ addspace(self.createModulation(fedata)) + self.createOrbPos(feraw)

	def createFrequency(self, feraw):
		frequency = feraw.get("frequency")
		if frequency:
			return str(frequency)
		return ""

	def createChannelNumber(self, fedata, feraw):
		channel = channelnumbers.getChannelNumber(feraw.get("frequency"), feraw.get("tuner_number"))
		if channel:
			return _("CH") + "%s" % channel
		return ""

	def createSymbolRate(self, fedata, feraw):
		if "DVB-T" in feraw.get("tuner_type"):
			bandwidth = fedata.get("bandwidth")
			if bandwidth:
				return bandwidth
		else:
			symbolrate = fedata.get("symbol_rate")
			if symbolrate:
				return str(symbolrate)
		return ""

	def createPolarization(self, fedata):
		polarization = fedata.get("polarization_abbreviation")
		if polarization:
			return polarization
		return ""

	def createFEC(self, fedata, feraw):
		if "DVB-T" in feraw.get("tuner_type"):
			code_rate_lp = fedata.get("code_rate_lp")
			code_rate_hp = fedata.get("code_rate_hp")
			if code_rate_lp and code_rate_hp:
				return code_rate_lp + "-" + code_rate_hp
		else:
			fec = fedata.get("fec_inner")
			if fec:
				return fec
		return ""

	def createModulation(self, fedata):
		if fedata.get("tuner_type") == _("Terrestrial"):
			constellation = fedata.get("constellation")
			if constellation:
				return constellation
		else:
			modulation = fedata.get("modulation")
			if modulation:
				return modulation
		return ""

	def createTunerType(self, feraw):
		tunertype = feraw.get("tuner_type")
		if tunertype:
			return tunertype
		return ""

	def createTunerSystem(self, fedata):
		tunersystem = fedata.get("system")
		if tunersystem:
			return tunersystem
		return ""

	def createOrbPos(self, feraw):
		orbpos = feraw.get("orbital_position")
		if orbpos > 1800:
			return str((float(3600 - orbpos)) / 10.0) + "\xc2\xb0 W"
		elif orbpos > 0:
			return str((float(orbpos)) / 10.0) + "\xc2\xb0 E"
		return ""

	def createOrbPosOrTunerSystem(self, fedata,feraw):
		orbpos = self.createOrbPos(feraw)
		if orbpos is not "":
			return orbpos
		return self.createTunerSystem(fedata)

	def createTransponderName(self,feraw):
		orbpos = feraw.get("orbital_position")
		if orbpos is None: # Not satellite
			return ""
		freq = feraw.get("frequency")
		if freq and freq < 10700000: # C-band
			if orbpos > 1800:
				orbpos += 1
			else:
				orbpos -= 1
				
		sat_names = {
			30:   'Rascom/Eutelsat 3E',
			48:   'SES 5',
			70:   'Eutelsat 7E',
			90:   'Eutelsat 9E',
			100:  'Eutelsat 10E',  
			130:  'Hot Bird',
			160:  'Eutelsat 16E',
			192:  'Astra 1KR/1L/1M/1N',
			200:  'Arabsat 20E',
			216:  'Eutelsat 21.5E',
			235:  'Astra 3',
			255:  'Eutelsat 25.5E',
			260:  'Badr 4/5/6',
			282:  'Astra 2E/2F/2G',
			305:  'Arabsat 30.5E',
			315:  'Astra 5',
			330:  'Eutelsat 33E',
			360:  'Eutelsat 36E',
			380:  'Paksat',
			390:  'Hellas Sat',
			400:  'Express 40E',
			420:  'Turksat',
			450:  'Intelsat 45E',
			480:  'Afghansat',
			490:  'Yamal 49E',
			530:  'Express 53E',
			570:  'NSS 57E',
			600:  'Intelsat 60E',
			620:  'Intelsat 62E',
			685:  'Intelsat 68.5E',
			705:  'Eutelsat 70.5E',
			720:  'Intelsat 72E',
			750:  'ABS',
			765:  'Apstar',
			785:  'ThaiCom',
			800:  'Express 80E',
			830:  'Insat',
			851:  'Intelsat/Horizons',
			880:  'ST2',
			900:  'Yamal 90E',
			915:  'Mesat',
			950:  'NSS/SES 95E',
			1005: 'AsiaSat 100E',
			1030: 'Express 103E',
			1055: 'Asiasat 105E',
			1082: 'NSS/SES 108E',
			1100: 'BSat/NSAT',
			1105: 'ChinaSat',
			1130: 'KoreaSat',
			1222: 'AsiaSat 122E',
			1380: 'Telstar 18',
			1440: 'SuperBird',
			2310: 'Ciel',
			2390: 'Echostar/Galaxy 121W',
			2410: 'Echostar/DirectTV 119W',
			2500: 'Echostar/DirectTV 110W',
			2630: 'Galaxy 97W',
			2690: 'NIMIQ 91W',
			2780: 'NIMIQ 82W',
			2830: 'Echostar/QuetzSat',
			2880: 'AMC 72W',
			2900: 'Star One',
			2985: 'Echostar 61.5W',
			2990: 'Amazonas',
			3020: 'Intelsat 58W',
			3045: 'Intelsat 55.5W',
			3070: 'Intelsat 53W',
			3100: 'Intelsat 50W',
			3150: 'Intelsat 45W',
			3169: 'Intelsat 43.1W',
			3195: 'SES 40.5W',
			3225: 'NSS/Telstar 37W',
			3255: 'Intelsat 34.5W',
			3285: 'Intelsat 31.5W',
			3300: 'Hispasat',
			3325: 'Intelsat 27.5W',
			3355: 'Intelsat 24.5W',
			3380: 'SES 22W',
			3400: 'NSS 20W',
			3420: 'Intelsat 18W',
			3450: 'Telstar 15W',
			3460: 'Express 14W',
			3475: 'Eutelsat 12.5W',
			3490: 'Express 11W',
			3520: 'Eutelsat 8W',
			3530: 'Nilesat/Eutelsat 7W',
			3550: 'Eutelsat 5W',
			3560: 'Amos',
			3592: 'Thor/Intelsat'
		}

		if orbpos in sat_names:
			return sat_names[orbpos]
		elif orbpos > 1800:
			return str((float(3600 - orbpos)) / 10.0) + "W"
		else:
			return str((float(orbpos)) / 10.0) + "E"

	def createProviderName(self,info):
		return info.getInfoString(iServiceInformation.sProvider)

	@cached
	def getText(self):
		service = self.source.service
		if service is None:
			return ""
		info = service and service.info()
		is_crypted = info.getInfo(iServiceInformation.sIsCrypted)

		if not info:
			return ""

		if self.type == "CryptoInfo":
			self.getCryptoInfo(info)
			if int(config.usage.show_cryptoinfo.value) > 0:
				return addspace(self.createCryptoBar(info)) + self.createCryptoSpecial(info)
			else:
				return addspace(self.createCryptoBar(info)) + addspace(self.current_source) + self.createCryptoSpecial(info)

		if self.type == "CryptoBar":
			if int(config.usage.show_cryptoinfo.value) > 0:
				self.getCryptoInfo(info)
				return self.createCryptoBar(info)
			else:
				return ""

		if self.type == "CryptoSeca":
			if int(config.usage.show_cryptoinfo.value) > 0:
				self.getCryptoInfo(info)
				return self.createCryptoSeca(info)
			else:
				return ""

		if self.type == "CryptoVia":
			if int(config.usage.show_cryptoinfo.value) > 0:
				self.getCryptoInfo(info)
				return self.createCryptoVia(info)
			else:
				return ""

		if self.type == "CryptoIrdeto":
			if int(config.usage.show_cryptoinfo.value) > 0:
				self.getCryptoInfo(info)
				return self.createCryptoIrdeto(info)
			else:
				return ""

		if self.type == "CryptoNDS":
			if int(config.usage.show_cryptoinfo.value) > 0:
				self.getCryptoInfo(info)
				return self.createCryptoNDS(info)
			else:
				return ""

		if self.type == "CryptoConax":
			if int(config.usage.show_cryptoinfo.value) > 0:
				self.getCryptoInfo(info)
				return self.createCryptoConax(info)
			else:
				return ""

		if self.type == "CryptoCryptoW":
			if int(config.usage.show_cryptoinfo.value) > 0:
				self.getCryptoInfo(info)
				return self.createCryptoCryptoW(info)
			else:
				return ""

		if self.type == "CryptoBeta":
			if int(config.usage.show_cryptoinfo.value) > 0:
				self.getCryptoInfo(info)
				return self.createCryptoBeta(info)
			else:
				return ""

		if self.type == "CryptoNagra":
			if int(config.usage.show_cryptoinfo.value) > 0:
				self.getCryptoInfo(info)
				return self.createCryptoNagra(info)
			else:
				return ""

		if self.type == "CryptoBiss":
			if int(config.usage.show_cryptoinfo.value) > 0:
				self.getCryptoInfo(info)
				return self.createCryptoBiss(info)
			else:
				return ""

		if self.type == "CryptoDre":
			if int(config.usage.show_cryptoinfo.value) > 0:
				self.getCryptoInfo(info)
				return self.createCryptoDre(info)
			else:
				return ""

		if self.type == "CryptoTandberg":
			if int(config.usage.show_cryptoinfo.value) > 0:
				self.getCryptoInfo(info)
				return self.createCryptoTandberg(info)
			else:
				return ""

		if self.type == "CryptoSpecial":
			if int(config.usage.show_cryptoinfo.value) > 0:
				self.getCryptoInfo(info)
				return self.createCryptoSpecial(info)
			else:
				return ""

		if self.type == "CryptoNameCaid":
			if int(config.usage.show_cryptoinfo.value) > 0:
				self.getCryptoInfo(info)
				return self.createCryptoNameCaid(info)
			else:
				return ""

		if self.type == "ResolutionString":
			return self.createResolution(info)

		if self.type == "VideoCodec":
			return self.createVideoCodec(info)

		if self.type == "Ecmtext":
			return self.get_Ecmtext()

		if self.type == "ProviderName":
			return self.createProviderName(info)

		if self.type == "CamName":
			return self.get_caName()

		elif self.type == "NetInfo":
			if is_crypted != 1:
				return ''
			data = self.GetEcmInfo2()
			if data['using']:
				return "CAID: %s   -  %s   -  HOPS: %s   -  ECM: %ss" % (data['caid'], data['address'], data['hops'], data['ecm_time'])
			elif data['reader']:
				return "CAID: %s   -  %s   -  HOPS: %s   -  ECM: %ss" % (data['caid'], data['address_from'], data['hops'], data['ecm_time'])

		elif self.type == "EcmInfo":
			if is_crypted != 1:
				return ''
			data = self.GetEcmInfo2()
			return "Provider: %s" % (data['provider'])

		elif self.type == "EcmInfo2":
			if is_crypted != 1:
				return ''
			data = self.GetEcmInfo2()
			if data['using'] == "newcamd" or data['using'] == "NewCamd":
				return "Provider: %s" % (data['provider'])
			elif data['using'] == "CCcam" or data['using'] == "CCcam-s2s":
				return "Provider: %s" % (data['provider'])
			else:
				return "CAID: %s     Provider: %s" % (data['caid'], data['provider'])

		elif self.type == "E-C-N":
			if is_crypted != 1:
				return ''

			CamName = self.get_caName()
			if self.type == "CryptoNameCaid" or CamName == 'Common Interface':
				if int(config.usage.show_cryptoinfo.value) > 0:
					self.getCryptoInfo(info)
					return self.createCryptoNameCaid(info)
				else:
					return ""

			data = self.GetEcmInfo2()
			if data['reader'] or data['using'] or data['protocol'] or data['from'] or data['hops']:
				if data['using'] == "fta":
					return "Fta"
				elif data['using'] == "emu" or data['from'] == "constcw":
					return "Emulator"
				elif data['hops'] == "0" and data['protocol'] == "none" or data['from'] == "cache*":
					return "Cache"
				elif data['hops'] == "0" and data['using'] == "sci" or data['hops'] == "0" and data['using'] == "smartreader+":
					return "Card"
				elif data['hops'] == "0" and data['protocol'] == "cccam" or data['hops'] == "0" and data['protocol'] == "newcamd":
					return "Card"
				elif data['hops'] == "0" and data['using'] == "newcamd" or data['hops'] == "0" and data['using'] == "NewCamd":
					return "Card"
				elif data['hops'] == "0" and data['using'] == "CCcam" or data['hops'] == "0" and data['using'] == "CCcam-s2s":
					return "Card"
				else:
					return "Network"
			elif data['reader'] or data['using'] or data['protocol'] or data['from'] or data['hops']:
				pos = data['address_from'].find('.') or data['from'].find('.')
				if pos > 1:
					return "Network"
				else:
					return "Card"
			return ""

		elif self.type == "CryptoBar":
			data = self.GetEcmInfo2()
			res = ""
			available_caids = info.getInfoObject(iServiceInformation.sCAIDs)
			for caid_entry in self.caid_data:
				if int(data['caid'], 16) >= int(caid_entry[0], 16) and int(data['caid'], 16) <= int(caid_entry[1], 16):
					color="\c0000??00"
				else:
					color = "\c007?7?7?"
					try:
						for caid in available_caids:
							if caid >= int(caid_entry[0], 16) and caid <= int(caid_entry[1], 16):
								color="\c00????00"
					except:
						pass

				if res: res += " "
				res += color + caid_entry[3]

			res += "\c00??????"
			return res

		if self.updateFEdata:
			feinfo = service.frontendInfo()
			if feinfo:
				self.feraw = feinfo.getAll(config.usage.infobar_frontend_source.value == "settings")
				if self.feraw:
					self.fedata = ConvertToHumanReadable(self.feraw)

		feraw = self.feraw
		if not feraw:
			feraw = info.getInfoObject(iServiceInformation.sTransponderData)
			if not feraw:
				return ""
			fedata = ConvertToHumanReadable(feraw)
		else:
			fedata = self.fedata
		if self.type == "All":
			self.getCryptoInfo(info)
			if int(config.usage.show_cryptoinfo.value) > 0:
				return addspace(self.createProviderName(info)) + self.createTransponderInfo(fedata,feraw) + addspace(self.createTransponderName(feraw)) + "\n"\
				+ addspace(self.createCryptoBar(info)) + addspace(self.createCryptoSpecial(info)) + "\n"\
				+ addspace(self.createPIDInfo(info)) + addspace(self.createVideoCodec(info)) + self.createResolution(info)
			else:
				return addspace(self.createProviderName(info)) + self.createTransponderInfo(fedata,feraw) + addspace(self.createTransponderName(feraw)) + "\n" \
				+ addspace(self.createCryptoBar(info)) + self.current_source + "\n" \
				+ addspace(self.createCryptoSpecial(info)) + addspace(self.createVideoCodec(info)) + self.createResolution(info)

		if self.type == "ServiceInfo":
			return addspace(self.createProviderName(info)) + addspace(self.createTunerSystem(fedata)) + addspace(self.createFrequency(feraw)) + addspace(self.createPolarization(fedata)) \
			+ addspace(self.createSymbolRate(fedata, feraw)) + addspace(self.createFEC(fedata, feraw)) + addspace(self.createModulation(fedata)) + addspace(self.createOrbPos(feraw)) + addspace(self.createTransponderName(feraw))\
			+ addspace(self.createVideoCodec(info)) + self.createResolution(info)

		if self.type == "TransponderInfo2line":
			return addspace(self.createProviderName(info)) + addspace(self.createTunerSystem(fedata)) + addspace(self.createTransponderName(feraw)) + '\n'\
			+ addspace(self.createFrequency(fedata)) + addspace(self.createPolarization(fedata))\
			+ addspace(self.createSymbolRate(fedata, feraw)) + self.createModulation(fedata) + '-' + addspace(self.createFEC(fedata, feraw))

		if self.type == "PIDInfo":
			return self.createPIDInfo(info)

		if self.type == "ServiceRef":
			return self.createServiceRef(info)

		if not feraw:
			return ""

		if self.type == "TransponderInfo":
			return self.createTransponderInfo(fedata,feraw)

		if self.type == "TransponderFrequency":
			return self.createFrequency(feraw)

		if self.type == "TransponderSymbolRate":
			return self.createSymbolRate(fedata, feraw)

		if self.type == "TransponderPolarization":
			return self.createPolarization(fedata)

		if self.type == "TransponderFEC":
			return self.createFEC(fedata, feraw)

		if self.type == "TransponderModulation":
			return self.createModulation(fedata)

		if self.type == "OrbitalPosition":
			return self.createOrbPos(feraw)

		if self.type == "TunerType":
			return self.createTunerType(feraw)

		if self.type == "TunerSystem":
			return self.createTunerSystem(fedata)

		if self.type == "OrbitalPositionOrTunerSystem":
			return self.createOrbPosOrTunerSystem(fedata,feraw)

		if self.type == "TerrestrialChannelNumber":
			return self.createChannelNumber(fedata, feraw)

		return ""

	text = property(getText)

	@cached
	def getBool(self):
		service = self.source.service
		info = service and service.info()

		if not info:
			return False

		if self.type == "CryptoCaidSecaAvailable":
			request_caid = "S"
			request_selected = False
		elif self.type == "CryptoCaidViaAvailable":
			request_caid = "V"
			request_selected = False
		elif self.type == "CryptoCaidIrdetoAvailable":
			request_caid = "I"
			request_selected = False
		elif self.type == "CryptoCaidNDSAvailable":
			request_caid = "ND"
			request_selected = False
		elif self.type == "CryptoCaidConaxAvailable":
			request_caid = "CO"
			request_selected = False
		elif self.type == "CryptoCaidCryptoWAvailable":
			request_caid = "CW"
			request_selected = False
		elif self.type == "CryptoCaidPowerVUAvailable":
			request_caid = "P"
			request_selected = False
		elif self.type == "CryptoCaidBetaAvailable":
			request_caid = "B"
			request_selected = False
		elif self.type == "CryptoCaidNagraAvailable":
			request_caid = "N"
			request_selected = False
		elif self.type == "CryptoCaidBissAvailable":
			request_caid = "BI"
			request_selected = False
		elif self.type == "CryptoCaidDreAvailable":
			request_caid = "D"
			request_selected = False
		elif self.type == "CryptoCaidBulCrypt1Available":
			request_caid = "B1"
			request_selected = False
		elif self.type == "CryptoCaidBulCrypt2Available":
			request_caid = "B2"
			request_selected = False
		elif self.type == "CryptoCaidTandbergAvailable":
			request_caid = "TB"
			request_selected = False
		elif self.type == "CryptoCaidSecaSelected":
			request_caid = "S"
			request_selected = True
		elif self.type == "CryptoCaidViaSelected":
			request_caid = "V"
			request_selected = True
		elif self.type == "CryptoCaidIrdetoSelected":
			request_caid = "I"
			request_selected = True
		elif self.type == "CryptoCaidNDSSelected":
			request_caid = "ND"
			request_selected = True
		elif self.type == "CryptoCaidConaxSelected":
			request_caid = "CO"
			request_selected = True
		elif self.type == "CryptoCaidCryptoWSelected":
			request_caid = "CW"
			request_selected = True
		elif self.type == "CryptoCaidPowerVUSelected":
			request_caid = "P"
			request_selected = True
		elif self.type == "CryptoCaidBetaSelected":
			request_caid = "B"
			request_selected = True
		elif self.type == "CryptoCaidNagraSelected":
			request_caid = "N"
			request_selected = True
		elif self.type == "CryptoCaidBissSelected":
			request_caid = "BI"
			request_selected = True
		elif self.type == "CryptoCaidDreSelected":
			request_caid = "D"
			request_selected = True
		elif self.type == "CryptoCaidBulCrypt1Selected":
			request_caid = "B1"
			request_selected = True
		elif self.type == "CryptoCaidBulCrypt2Selected":
			request_caid = "B2"
			request_selected = True
		elif self.type == "CryptoCaidTandbergSelected":
			request_caid = "TB"
			request_selected = True
		else:
			return False

		request_caid = None
		for x in self.ca_table:
			if x[0] == self.type:
				request_caid = x[1]
				request_selected = x[2]
				break

		if request_caid is None:
			return False

		if info.getInfo(iServiceInformation.sIsCrypted) != 1:
			return False

		data = self.ecmdata.getEcmData()
		data = self.GetEcmInfo2()

		if data is None:
			return False

		current_caid	= data['caid'] or data[1]

		available_caids = info.getInfoObject(iServiceInformation.sCAIDs)

		for caid_entry in self.caid_data:
			if caid_entry[3] == request_caid:
				if request_selected:
					if int(caid_entry[0], 16) <= int(current_caid, 16) <= int(caid_entry[1], 16):
						return True
				else: # request available
					try:
						for caid in available_caids:
							if int(caid_entry[0], 16) <= caid <= int(caid_entry[1], 16):
								return True
					except:
						pass

		return False

	boolean = property(getBool)

	def changed(self, what):
		if what[0] == self.CHANGED_SPECIFIC:
			self.updateFEdata = False
			if what[1] == iPlayableService.evNewProgramInfo:
				self.updateFEdata = True
			if what[1] == iPlayableService.evEnd:
				self.feraw = self.fedata = None
			Converter.changed(self, what)
		elif what[0] == self.CHANGED_POLL and self.updateFEdata is not None:
			self.updateFEdata = False
			Converter.changed(self, what)
