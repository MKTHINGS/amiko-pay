#    event.py
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

import select
import time

import network



class Enum(set):
	def __getattr__(self, name):
		if name in self:
			return name
		raise AttributeError



signals = Enum([
	"readyForRead",
	"readyForWrite",
	"closed",
	"link",
	"quit"
	])



class Context:

	class EventConnection:
		# For network signals, sender must be the socket object
		# sender == None: common place-holder
		def __init__(self, sender, signal, handler):
			self.sender = sender
			self.signal = signal
			self.handler = handler
			self.hasHappened = False

	class Timer:
		def __init__(self, timestamp, handler):
			self.timestamp = timestamp
			self.handler = handler


	def __init__(self):
		# Each element is an EventConnection
		self.__eventConnections = []

		# Each element is a Timer
		self.__timers = []


	def connect(self, sender, signal, handler):
		self.__eventConnections.append(
			Context.EventConnection(sender, signal, handler))


	def setTimer(self, timestamp, handler):
		self.__timers.append(Context.Timer(timestamp, handler))


	def removeConnectionsBySender(self, sender):
		self.__eventConnections = filter(lambda c: c.sender != sender,
			self.__eventConnections)


	def removeConnectionsByHandler(self, handler):
		self.__eventConnections = filter(lambda c: c.handler != handler,
			self.__eventConnections)


	def dispatchNetworkEvents(self):
		rlist = set([c.sender for c in self.__eventConnections
			if c.signal == signals.readyForRead])
		wlist = set([c.sender for c in self.__eventConnections
			if c.signal == signals.readyForWrite])

		# wait for network events, with 0.01 s timeout:
		#print "select.select(%s, %s, [], 0.01)" % (str(rlist), str(wlist))
		rlist, wlist, xlist = select.select(rlist, wlist, [], 0.01)
		#print " = %s, %s, %s" % (rlist, wlist, xlist)

		#Call read handlers without removing the connections:
		for r in rlist:
			self.sendSignal(r, signals.readyForRead)

		#Mark relevant write connections as happened
		for w in wlist:
			for c in self.__eventConnections:
				if c.sender == w and c.signal == signals.readyForWrite:
					c.hasHappened = True

		#Call handlers for all connections marked as happened
		for w in wlist:
			for c in self.__eventConnections:
				if c.hasHappened:
					c.handler()

		#Remove connections which have just been called
		self.__eventConnections = filter(
			lambda c: not c.hasHappened, self.__eventConnections)


	def dispatchTimerEvents(self):
		now = time.time()
		for t in self.__timers:
			if not (t.timestamp > now):
				t.handler()
		self.__timers = filter(lambda t: t.timestamp > now, self.__timers)


	def sendSignal(self, sender, signal, *args, **kwargs):
		handlers = [c.handler for c in self.__eventConnections
			if c.sender == sender and c.signal == signal]
		for h in handlers:
			h(*args, **kwargs)

