#    bitcoind_dummy.py
#    Copyright (C) 2014-2016 by CJP
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

import binascii
import random

import log
import messages

from ..utils.crypto import *
from ..utils import base58



class Bitcoind_Dummy:
	"""
	Simulated connection to a Bitcoin daemon process.
	"""

	def __init__(self, settings):
		self.random = random.Random()
		self.random.seed(42)
		self.keys = []
		self.numConfirmations = {}


	def isConnected(self):
		return True
		

	def getBalance(self):
		return 0


	def getBlockCount(self):
		return 0


	def getNewAddress(self):
		return self.__getAddressFromKey(self.__makeNewKey())


	def getPrivateKey(self, address):
		for k in self.keys:
			if self.__getAddressFromKey(k) == address:
				return base58.encodeBase58Check(k.getPrivateKey(), 128)

		while True:
			k = self.__makeNewKey()
			if self.__getAddressFromKey(k) == address:
				return base58.encodeBase58Check(k.getPrivateKey(), 128)


	def getTransactionHashesByBlockHeight(self, height):
		return self.numConfirmations.keys()


	def getTransaction(self, thash):
		#This is a partial, unfinished implementation
		if thash in self.numConfirmations.keys():
			self.numConfirmations[thash] += 1
		else:
			self.numConfirmations[thash] = 0
		return {"confirmations": self.numConfirmations[thash]}


	def importprivkey(self, privateKey, description, rescan):
		pass


	def listUnspent(self):
		k1 = self.__makeNewKey()
		k2 = self.__makeNewKey()
		return \
		[
			{
			"address": self.__getAddressFromKey(k),
			"amount": 1000000000,
			"scriptPubKey": "",
			"txid": SHA256(k.getPublicKey()), #Wrong, but good enough for testing
			"vout": 0
			}

			for k in [k1, k2]
		]


	def sendRawTransaction(self, txData):
		pass


	def __makeNewKey(self):
		newKey = Key()
		privKey = "".join([chr(self.random.getrandbits(8)) for i in range(32)])
		privKey += "\0" #indicate the use of compressed keys
		newKey.setPrivateKey(privKey)
		self.keys.append(newKey)
		return newKey


	def __getAddressFromKey(self, key):
		return base58.encodeBase58Check(
			RIPEMD160(SHA256(key.getPublicKey())),
			0)


	def handleMessage(self, msg):
		return \
		[
		messages.BitcoinReturnValue(
			value=msg.function(self),
			ID=msg.returnID, channelIndex=msg.returnChannelIndex)
		]



if __name__ == "__main__":
	#Test:
	bitcoind = Bitcoind_Dummy(None)
	for i in range(10):
		a = bitcoind.getNewAddress()
		print a, bitcoind.getPrivateKey(a)

