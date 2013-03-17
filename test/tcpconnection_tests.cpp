/*
    tcpconnection_tests.cpp
    Copyright (C) 2013 by CJP

    This file is part of Amiko Pay.

    Amiko Pay is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Amiko Pay is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Amiko Pay. If not, see <http://www.gnu.org/licenses/>.
*/

#include <cstdio>
#include <stdint.h>

#include <unistd.h>

#include "tcpconnection.h"
#include "tcplistener.h"
#include "timer.h"

#include "test.h"

void receiveWithTimeout(void *arg);

/*
TODO: document and expand
*/
class CTCPConnectionTest : public CTest
{
public:
	CTCPConnection *m_C1;
	CTCPConnection *m_C2;

private:
	virtual const char *getName()
		{return "tcpconnection";}

	virtual void run()
	{
		CTCPListener *listener = new CTCPListener("4321");

		m_C1 = new CTCPConnection("localhost", "4321");
		m_C2 = new CTCPConnection(*listener);

		m_C1->send(CBinBuffer("abcdef"));

		{
			CBinBuffer result(6);
			m_C2->receive(result, 1); //1 ms timeout
			test("  CTCPConnection transfers data",
				result.toString() == "abcdef");
		}

		{
			uint64_t t1 = CTimer::getTime();
			test("  receive times out when there is no data",
				throws<CTCPConnection::CTimeoutException>(receiveWithTimeout, this)
				);
			uint64_t t2 = CTimer::getTime();
			//give it 50ms space:
			test("  time-out time is as expected",
				int64_t(t2-t1) >= 1200 && int64_t(t2-t1) < 1250);
		}

		m_C1->send(CBinBuffer("gh"));

		test("  receive times out when there is partial data",
			throws<CTCPConnection::CTimeoutException>(receiveWithTimeout, this)
			);

		m_C1->send(CBinBuffer("ijkl"));

		{
			CBinBuffer result(4);
			m_C2->receive(result, 1); //1 ms timeout
			test("  receive returns old data + first part of new data",
				result.toString() == "ghij");
		}

		{
			CBinBuffer result(2);
			m_C2->receive(result, 1); //1 ms timeout
			test("  receive returns remaining old data",
				result.toString() == "kl");
		}

		m_C1->send(CBinBuffer("mnop"));
		{
			CBinBuffer result(2);
			m_C2->receive(result, 1); //1 ms timeout
			m_C2->unreceive(CBinBuffer("qr"));
			m_C1->send(CBinBuffer("st"));
			result.resize(6);
			m_C2->receive(result, 1); //1 ms timeout
			test("  unreceive inserts data in correct position",
				result.toString() == "qropst");
		}

		//Delete in the correct order, to allow release of the port number
		delete m_C1;

		test("  receive gives exception when peer closes",
			throws<CTCPConnection::CReceiveException>(receiveWithTimeout, this)
			);

		delete m_C2;

		delete listener;
	}

} tcpconnectionTest;


void receiveWithTimeout(void *arg)
{
	CTCPConnectionTest *test = (CTCPConnectionTest *)arg;
	CBinBuffer b(4);
	test->m_C2->receive(b, 1200);
}

