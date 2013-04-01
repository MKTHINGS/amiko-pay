/*
    amiko.cpp
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

#include "amiko.h"


CAmiko::CAmiko(const CAmikoSettings &settings) :
	m_Settings(settings),
	m_ListenerThread(this, m_Settings.m_Value.m_portNumber)
{
}


CAmiko::~CAmiko()
{
	stop();

	{
		CMutexLocker lock(m_PendingComLinks);
		for(std::list<CComLink *>::iterator i=m_PendingComLinks.m_Value.begin();
			i != m_PendingComLinks.m_Value.end(); i++)
		{
			(*i)->setReceiver(NULL);
			(*i)->stop();
			delete (*i);
		}
	}

	{
		CMutexLocker lock(m_OperationalComLinks);
		for(std::list<CComLink *>::iterator i=m_OperationalComLinks.m_Value.begin();
			i != m_OperationalComLinks.m_Value.end(); i++)
		{
			(*i)->setReceiver(NULL);
			(*i)->stop();
			delete (*i);
		}
	}
}


void CAmiko::start()
{
	m_ListenerThread.start();
}


void CAmiko::stop()
{
	m_ListenerThread.stop();
}


void CAmiko::addPendingComLink(CComLink *link)
{
	CMutexLocker lock(m_PendingComLinks);	
	m_PendingComLinks.m_Value.push_back(link);
}


void CAmiko::processPendingComLinks()
{
	CMutexLocker lock1(m_PendingComLinks);
	CMutexLocker lock2(m_OperationalComLinks);

	for(std::list<CComLink *>::iterator i = m_PendingComLinks.m_Value.begin();
		i != m_PendingComLinks.m_Value.end(); i++)
	{
		if((*i)->getState() == CComLink::eClosed)
		{
			//Delete closed links (apparently initialization failed for these)
			CComLink *link = *i;
			link->stop();
			delete link;

			std::list<CComLink *>::iterator j = i; i++;
			m_PendingComLinks.m_Value.erase(j);
		}
		else if((*i)->getState() == CComLink::eOperational)
		{
			//Move to operational list
			//TODO: set receiver
			m_OperationalComLinks.m_Value.push_back(*i);

			std::list<CComLink *>::iterator j = i; i++;
			m_PendingComLinks.m_Value.erase(j);
		}

		//This can happen if the above code erased an item
		if(i == m_PendingComLinks.m_Value.end()) break;
	}
}

