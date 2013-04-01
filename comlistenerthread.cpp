/*
    comlistenerthread.cpp
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

#include <cstdlib>

#include "timer.h"
#include "log.h"
#include "comlink.h"

#include "comlistenerthread.h"


CComListenerThread::CComListenerThread(CAmiko *amiko, const CString &service) :
	m_Amiko(amiko),
	m_Listener(service)
{
}


CComListenerThread::~CComListenerThread()
{
}


void CComListenerThread::threadFunc()
{
	while(!m_terminate)
	{
		try
		{
			acceptNewConnections();
			m_Amiko->processPendingComLinks();
		}
		catch(CException &e)
		{
			log(CString::format(
				"CComListenerThread::threadFunc(): Caught application exception: %s\n",
				256, e.what()));
			//TODO: maybe app cleanup?
			//e.g. with atexit, on_exit
			exit(3);
		}
		catch(std::exception &e)
		{
			log(CString::format(
				"CComListenerThread::threadFunc(): Caught standard library exception: %s\n",
				256, e.what()));
			//TODO: maybe app cleanup?
			//e.g. with atexit, on_exit
			exit(3);
		}

		//wait 100ms when there are no new connections
		CTimer::sleep(100);
	}
}


void CComListenerThread::acceptNewConnections()
{
	try
	{
		// Limit number of pending links
		while(m_Amiko->getNumPendingComLinks() < 100)
		{
			CComLink *link = new CComLink(m_Listener, m_Amiko->getSettings());
			//TODO: if in the below code an exception occurs, delete the above object
			link->start(); //start comlink thread
			m_Amiko->addPendingComLink(link);
		}
	}
	catch(CTCPConnection::CTimeoutException &e)
	{}
}

