################################################################################
#    Extended NumberZap Plugin for Enigma2
#    Version: 1.0-rc12 (12.04.2014 22:00)
#    Copyright (C) 2011,2012 vlamo <vlamodev@gmail.com>
#    mod Dima73
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
################################################################################

from Components.Language import language
import os, gettext

PLUGIN_NAME = "NumberZapExt"
PLUGIN_PATH = os.path.dirname( __file__ )

def localeInit():
	lang = language.getLanguage()[:2]
	os.environ["LANGUAGE"] = lang
	gettext.bindtextdomain(PLUGIN_NAME, "%s/locale"%(PLUGIN_PATH))

def _(txt):
	t = gettext.dgettext(PLUGIN_NAME, txt)
	if t == txt:
		t = gettext.gettext(txt)
	return t

localeInit()
language.addCallback(localeInit)
