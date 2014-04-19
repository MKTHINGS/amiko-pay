#    paymentchannel.py
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



class PaymentChannel:
	def __init__(self, state):

		#Current balances:
		self.amountLocal             = state["amountLocal"]
		self.amountRemote            = state["amountRemote"]

		self.transactionsIncomingReserved  = state["transactionsIncomingReserved"]
		self.transactionsOutgoingReserved  = state["transactionsOutgoingReserved"]
		self.transactionsIncomingLocked    = state["transactionsIncomingLocked"]
		self.transactionsOutgoingLocked    = state["transactionsOutgoingLocked"]

	def list(self):
		return \
		{
		"amountLocal"           : self.amountLocal,
		"amountRemote"          : self.amountRemote,

		"transactionsIncomingReserved": self.transactionsIncomingReserved,
		"transactionsOutgoingReserved": self.transactionsOutgoingReserved,
		"transactionsIncomingLocked"  : self.transactionsIncomingLocked,
		"transactionsOutgoingLocked"  : self.transactionsOutgoingLocked
		}

