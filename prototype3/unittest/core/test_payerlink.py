#!/usr/bin/env python
#    test_payerlink.py
#    Copyright (C) 2015-2016 by CJP
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
#
#    Additional permission under GNU GPL version 3 section 7
#
#    If you modify this Program, or any covered work, by linking or combining it
#    with the OpenSSL library (or a modified version of that library),
#    containing parts covered by the terms of the OpenSSL License and the SSLeay
#    License, the licensors of this Program grant you additional permission to
#    convey the resulting work. Corresponding Source for a non-source form of
#    such a combination shall include the source code for the parts of the
#    OpenSSL library used as well as that of the covered work.

import unittest
import copy
import threading
import time

import testenvironment

from amiko.core import messages

from amiko.core import payerlink



class Test(unittest.TestCase):
	def setUp(self):
		self.payerLink = payerlink.PayerLink()


	def test_defaultAttributes(self):
		"Test default attributes"

		self.assertEqual(self.payerLink.payeeHost, None)
		self.assertEqual(self.payerLink.payeePort, None)
		self.assertEqual(self.payerLink.payeeLinkID, None)

		self.assertEqual(self.payerLink.amount, None)
		self.assertEqual(self.payerLink.receipt, None)
		self.assertEqual(self.payerLink.transactionID, None)
		self.assertEqual(self.payerLink.token, None)

		self.assertEqual(self.payerLink.routingContext, None)
		self.assertEqual(self.payerLink.meetingPointID, None)

		self.assertEqual(self.payerLink.state, payerlink.PayerLink.states.initial)


	def test_getTimeoutMessage(self):
		"Test getTimeoutMessage"

		msg = self.payerLink.getTimeoutMessage()
		self.assertTrue(isinstance(msg, messages.PayerTimeout))
		self.assertEqual(msg.state, payerlink.PayerLink.states.initial)

		self.payerLink.state = payerlink.PayerLink.states.receivedRequestCommit

		msg = self.payerLink.getTimeoutMessage()
		self.assertTrue(isinstance(msg, messages.PayerTimeout))
		self.assertEqual(msg.state, payerlink.PayerLink.states.receivedRequestCommit)


	def test_msg_timeout_initial(self):
		"Test msg_timeout (state: initial)"

		ret = self.payerLink.handleMessage(
			messages.PayerTimeout(state=payerlink.PayerLink.states.initial))

		self.assertEqual(self.payerLink.state, payerlink.PayerLink.states.cancelled)

		self.assertEqual(len(ret), 2)

		msg = ret[0]
		self.assertTrue(isinstance(msg, messages.FilterTimeouts))
		function = msg.function
		self.assertFalse(function(messages.PayerTimeout()))
		self.assertTrue(function(messages.NodeStateTimeout_Route()))
		msg = ret[1]
		self.assertTrue(isinstance(msg, messages.SetEvent))
		self.assertEqual(msg.event, messages.SetEvent.events.receiptReceived)


	def test_msg_timeout_receivedRequestCommit(self):
		"Test msg_timeout (state: receivedRequestCommit)"

		self.payerLink.state = payerlink.PayerLink.states.receivedRequestCommit

		ret = self.payerLink.handleMessage(
			messages.PayerTimeout(state=payerlink.PayerLink.states.receivedRequestCommit))

		self.assertEqual(self.payerLink.state, payerlink.PayerLink.states.committed)

		self.assertEqual(len(ret), 2)

		msg = ret[0]
		self.assertTrue(isinstance(msg, messages.FilterTimeouts))
		function = msg.function
		self.assertFalse(function(messages.PayerTimeout()))
		self.assertTrue(function(messages.NodeStateTimeout_Route()))
		msg = ret[1]
		self.assertTrue(isinstance(msg, messages.SetEvent))
		self.assertEqual(msg.event, messages.SetEvent.events.paymentFinished)


	def test_msg_timeout_other(self):
		"Test msg_timeout (state: other)"

		ret = self.payerLink.handleMessage(
			messages.PayerTimeout(state=payerlink.PayerLink.states.receivedRequestCommit))

		self.assertEqual(self.payerLink.state, payerlink.PayerLink.states.initial)

		self.assertEqual(len(ret), 0)


	def test_msg_receipt(self):
		"Test msg_receipt"

		ret = self.payerLink.handleMessage(
			messages.Receipt(
				amount=123,
				receipt="receipt",
				transactionID="txID",
				meetingPoints=["MPID"]
				))

		self.assertEqual(self.payerLink.state, payerlink.PayerLink.states.hasReceipt)
		self.assertEqual(self.payerLink.amount, 123)
		self.assertEqual(self.payerLink.receipt, "receipt")
		self.assertEqual(self.payerLink.transactionID, "txID")
		#self.assertEqual(self.payerLink.meetingPointID, "MPID") #TODO

		self.assertEqual(len(ret), 1)

		msg = ret[0]
		self.assertTrue(isinstance(msg, messages.SetEvent))
		self.assertEqual(msg.event, messages.SetEvent.events.receiptReceived)


	def test_msg_confirm(self):
		"Test msg_confirm"
		self.assertRaises(Exception,
			self.payerLink.handleMessage, messages.PayerLink_Confirm(agreement=True))

		self.payerLink.state = payerlink.PayerLink.states.hasReceipt

		ret = self.payerLink.handleMessage(messages.PayerLink_Confirm(agreement=True))

		self.assertEqual(self.payerLink.state, payerlink.PayerLink.states.confirmed)

		self.assertEqual(len(ret), 2)
		msg = ret[0]
		self.assertTrue(isinstance(msg, messages.OutboundMessage))
		self.assertEqual(msg.localID, messages.payerLocalID)
		msg = msg.message
		self.assertTrue(isinstance(msg, messages.Confirm))
		self.assertEqual(msg.ID, None)
		self.assertEqual(msg.meetingPointID, self.payerLink.meetingPointID)
		msg = ret[1]
		self.assertTrue(isinstance(msg, messages.MakeRoute))
		self.assertEqual(msg.amount, self.payerLink.amount)
		self.assertEqual(msg.transactionID, self.payerLink.transactionID)
		#self.assertEqual(msg.startTime, None) #TODO
		#self.assertEqual(msg.endTime, None) #TODO
		self.assertEqual(msg.meetingPointID, self.payerLink.meetingPointID)
		self.assertEqual(msg.ID, messages.payerLocalID)
		self.assertEqual(msg.isPayerSide, True)

		self.payerLink.state = payerlink.PayerLink.states.hasReceipt

		ret = self.payerLink.handleMessage(messages.PayerLink_Confirm(agreement=False))

		self.assertEqual(self.payerLink.state, payerlink.PayerLink.states.cancelled)

		self.assertEqual(len(ret), 3)
		msg = ret[0]
		self.assertTrue(isinstance(msg, messages.FilterTimeouts))
		function = msg.function
		self.assertFalse(function(messages.PayerTimeout()))
		self.assertTrue(function(messages.NodeStateTimeout_Route()))
		msg = ret[1]
		self.assertTrue(isinstance(msg, messages.OutboundMessage))
		self.assertEqual(msg.localID, messages.payerLocalID)
		msg = msg.message
		self.assertTrue(isinstance(msg, messages.Cancel))
		self.assertEqual(msg.ID, None)
		msg = ret[2]
		self.assertTrue(isinstance(msg, messages.SetEvent))
		self.assertEqual(msg.event, messages.SetEvent.events.paymentFinished)


	def test_msg_cancel(self):
		"Test msg_cancel"

		self.payerLink.transactionID = 'txID'

		for s in (payerlink.PayerLink.states.confirmed, payerlink.PayerLink.states.hasPayerRoute):
			self.payerLink.state = s

			ret = self.payerLink.msg_cancel(None)

			self.assertEqual(self.payerLink.state, payerlink.PayerLink.states.cancelled)

			self.assertEqual(len(ret), 3)
			msg = ret[0]
			self.assertTrue(isinstance(msg, messages.FilterTimeouts))
			function = msg.function
			self.assertFalse(function(messages.PayerTimeout()))
			self.assertTrue(function(messages.NodeStateTimeout_Route()))
			msg = ret[1]
			self.assertTrue(isinstance(msg, messages.CancelRoute))
			self.assertTrue(msg.transactionID, 'txID')
			self.assertTrue(msg.isPayerSide, True)
			msg = ret[2]
			self.assertTrue(isinstance(msg, messages.SetEvent))
			self.assertEqual(msg.event, messages.SetEvent.events.paymentFinished)

		self.payerLink.state = payerlink.PayerLink.states.locked
		self.assertRaises(Exception, self.payerLink.msg_cancel, None)
		self.assertEqual(self.payerLink.state, payerlink.PayerLink.states.locked)


	def test_haveNoRouteOutgoing(self):
		"Test haveNoRouteOutgoing"

		ret = self.payerLink.haveNoRouteOutgoing(None, None)

		self.assertEqual(self.payerLink.state, payerlink.PayerLink.states.cancelled)

		self.assertEqual(len(ret), 3)
		msg = ret[0]
		self.assertTrue(isinstance(msg, messages.FilterTimeouts))
		function = msg.function
		self.assertFalse(function(messages.PayerTimeout()))
		self.assertTrue(function(messages.NodeStateTimeout_Route()))
		msg = ret[1]
		self.assertTrue(isinstance(msg, messages.OutboundMessage))
		self.assertEqual(msg.localID, messages.payerLocalID)
		msg = msg.message
		self.assertTrue(isinstance(msg, messages.Cancel))
		msg = ret[2]
		self.assertTrue(isinstance(msg, messages.SetEvent))
		self.assertEqual(msg.event, messages.SetEvent.events.paymentFinished)


	def test_cancelOutgoing(self):
		"Test cancelOutgoing"

		self.assertRaises(Exception,
			self.payerLink.cancelOutgoing, None)

		self.payerLink.state = payerlink.PayerLink.states.confirmed

		ret = self.payerLink.cancelOutgoing(None)
		self.assertEqual(len(ret), 0)


	def test_haveRouteOutgoing(self):
		"Test haveRouteOutgoing"

		self.payerLink.amount = 123

		self.assertRaises(Exception, self.payerLink.haveRouteOutgoing,
			messages.HaveRoute(
				ID=messages.payerLocalID,
				transactionID=self.payerLink.transactionID,
				isPayerSide=True
				))

		self.payerLink.state = payerlink.PayerLink.states.confirmed

		ret = self.payerLink.haveRouteOutgoing(
			messages.HaveRoute(
				ID=messages.payerLocalID,
				transactionID=self.payerLink.transactionID,
				isPayerSide=True
				))

		self.assertEqual(self.payerLink.state, payerlink.PayerLink.states.hasPayerRoute)

		self.assertEqual(len(ret), 0)

		self.payerLink.state = payerlink.PayerLink.states.hasPayeeRoute

		ret = self.payerLink.haveRouteOutgoing(
			messages.HaveRoute(
				ID=messages.payerLocalID,
				transactionID=self.payerLink.transactionID,
				isPayerSide=True
				))

		self.assertEqual(self.payerLink.state, payerlink.PayerLink.states.locked)

		self.assertEqual(len(ret), 1)
		msg = ret[0]
		self.assertTrue(isinstance(msg, messages.Lock))
		self.assertEqual(msg.transactionID, self.payerLink.transactionID)
		self.assertEqual(msg.isPayerSide, True)
		self.assertEqual(msg.amount, 123)
		#TODO: verify startTime and endTime
		#Don't verify channelIndex: its value is irrelevant here.


	def test_haveRouteIncoming(self):
		"Test haveRouteIncoming)"

		self.payerLink.amount = 123

		self.assertRaises(Exception, self.payerLink.haveRouteIncoming,
			messages.HaveRoute(
				ID=messages.payerLocalID,
				transactionID=self.payerLink.transactionID,
				isPayerSide=False
				))

		self.payerLink.state = payerlink.PayerLink.states.confirmed

		ret = self.payerLink.haveRouteIncoming(
			messages.HaveRoute(
				ID=messages.payerLocalID,
				transactionID=self.payerLink.transactionID,
				isPayerSide=False
				))

		self.assertEqual(self.payerLink.state, payerlink.PayerLink.states.hasPayeeRoute)

		self.assertEqual(len(ret), 0)

		self.payerLink.state = payerlink.PayerLink.states.hasPayerRoute

		ret = self.payerLink.haveRouteIncoming(
			messages.HaveRoute(
				ID=messages.payerLocalID,
				transactionID=self.payerLink.transactionID,
				isPayerSide=False
				))

		self.assertEqual(self.payerLink.state, payerlink.PayerLink.states.locked)

		self.assertEqual(len(ret), 1)
		msg = ret[0]
		self.assertTrue(isinstance(msg, messages.Lock))
		self.assertEqual(msg.transactionID, self.payerLink.transactionID)
		self.assertEqual(msg.isPayerSide, True)
		self.assertEqual(msg.amount, 123)
		#TODO: verify startTime and endTime
		#Don't verify channelIndex: its value is irrelevant here.


	def test_requestCommitOutgoing(self):
		"Test requestCommitOutgoing"

		self.assertRaises(Exception, self.payerLink.requestCommitOutgoing,
			messages.RequestCommit(token="bar")
			)

		self.payerLink.state = payerlink.PayerLink.states.locked

		ret = self.payerLink.requestCommitOutgoing(messages.RequestCommit(token="bar"))

		self.assertEqual(self.payerLink.state, payerlink.PayerLink.states.receivedRequestCommit)
		self.assertEqual(self.payerLink.token, "bar")

		self.assertEqual(len(ret), 1)
		msg = ret[0]
		self.assertTrue(isinstance(msg, messages.TimeoutMessage))
		msg = msg.message
		self.assertTrue(isinstance(msg, messages.PayerTimeout))
		self.assertEqual(msg.state, payerlink.PayerLink.states.receivedRequestCommit)


	def test_settleCommitIncoming(self):
		"Test settleCommitIncoming"

		ret = self.payerLink.settleCommitIncoming(messages.SettleCommit(token="bar"))

		self.assertEqual(self.payerLink.state, payerlink.PayerLink.states.committed)

		self.assertEqual(len(ret), 2)

		msg = ret[0]
		self.assertTrue(isinstance(msg, messages.FilterTimeouts))
		function = msg.function
		self.assertFalse(function(messages.PayerTimeout()))
		self.assertTrue(function(messages.NodeStateTimeout_Route()))
		msg = ret[1]
		self.assertTrue(isinstance(msg, messages.SetEvent))
		self.assertEqual(msg.event, messages.SetEvent.events.paymentFinished)


	def test_settleRollbackOutgoing(self):
		"Test settleRollbackOutgoing"

		self.assertRaises(Exception, self.payerLink.settleRollbackOutgoing,
			messages.SettleRollback(
				transactionID=self.payerLink.transactionID))

		self.payerLink.state = payerlink.PayerLink.states.locked

		ret = self.payerLink.settleRollbackOutgoing(
			messages.SettleRollback(
				transactionID=self.payerLink.transactionID))

		self.assertEqual(self.payerLink.state, payerlink.PayerLink.states.cancelled)

		self.assertEqual(len(ret), 3)

		msg = ret[0]
		self.assertTrue(isinstance(msg, messages.FilterTimeouts))
		function = msg.function
		self.assertFalse(function(messages.PayerTimeout()))
		self.assertTrue(function(messages.NodeStateTimeout_Route()))
		msg = ret[1]
		self.assertTrue(isinstance(msg, messages.OutboundMessage))
		self.assertEqual(msg.localID, messages.payerLocalID)
		msg = msg.message
		self.assertTrue(isinstance(msg, messages.Cancel))
		msg = ret[2]
		self.assertTrue(isinstance(msg, messages.SetEvent))
		self.assertEqual(msg.event, messages.SetEvent.events.paymentFinished)


if __name__ == "__main__":
	unittest.main(verbosity=2)

