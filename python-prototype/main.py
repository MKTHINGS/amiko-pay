#!/usr/bin/env python
#    main.py
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

import time

import amiko
import event
import network


a = amiko.Amiko()
a.start()

time.sleep(0.1)
connection = network.Connection(a.context, "amikolink://localhost:4321/X")
connection.send("hello")

time.sleep(2.0)

a.sendSignal(event.signals.quit)
a.stop()


