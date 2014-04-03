#    paylink.py
#    Copyright (C) 2014 by CJP
#
#    This file is part of Amiko Pay.
#
#    Amiko Pay is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Amiko Pay is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Amiko Pay. If not, see <http://www.gnu.org/licenses/>.

from urlparse import urlparse

import network
import messages
import event



class Payer(event.Handler):
	def __init__(self, context, URL):
		event.Handler.__init__(self, context)

		URL = urlparse(URL)
		self.remoteHost = URL.hostname
		self.remotePort = 4321 if URL.port == None else URL.port
		self.ID = URL.path[1:] #remove initial slash

		print self.remoteHost
		print self.remotePort
		print self.ID

		self.amount = None #unknown
		self.receipt = None #unknown

		self.connection = network.Connection(self.context,
			(self.remoteHost, self.remotePort))
		#TODO: maybe listen to closed event?

		self.connection.sendMessage(messages.Pay(self.ID))



class Payee(event.Handler):
	def __init__(self, context, ID, amount, receipt):
		event.Handler.__init__(self, context)

		self.ID = ID
		self.amount = 0 #default
		self.receipt = "" #default

		self.connection = None


