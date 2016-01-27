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
from Components.Network import iNetwork
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Components.Label import Label

class RestartNetwork(Screen):
    def __init__(self, session):
        Screen.__init__(self, session)
        skin = """
            <screen name="RestartNetwork" position="center,center" size="600,100" title="Restart Network Adapter">
            <widget name="label" position="10,30" size="500,50" halign="center" font="Regular;20" transparent="1" foregroundColor="white" />
            </screen> """
        self.skin = skin
        self["label"] = Label(_("Please wait while your network is restarting..."))
        self.onShown.append(self.setWindowTitle)
        self.onLayoutFinish.append(self.restartLan)

    def setWindowTitle(self):
        self.setTitle(_("Restart Network Adapter"))

    def restartLan(self):
        iNetwork.restartNetwork(self.restartLanDataAvail)

    def restartLanDataAvail(self, data):
        if data is True:
            iNetwork.getInterfaces(self.getInterfacesDataAvail)

    def getInterfacesDataAvail(self, data):
        self.close()
