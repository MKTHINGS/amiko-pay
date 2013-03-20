/*
    comlink.h
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

#ifndef COMLINK_H
#define COMLINK_H

#include <map>
#include <queue>

#include "exception.h"
#include "cstring.h"
#include "uriparser.h"

#include "cthread.h"
#include "cominterface.h"

/*
A ComLink object is a ComInterface that sends messages to and from a (remote)
peer process. It contains its own thread which manages sending and receiving
of messages.
A ComLink object can have the following states:
  pending
  operational
  closed
The initial state is 'pending'. An object can spontaneously perform the
following state transitions:
  pending->operational
  pending->closed
  operational->closed
Sending and receiving of messages only happens in the operational state.
As soon as the closed state is reached, the ComLink object should be deleted
to free up system resources (such as memory, the thread and the network socket).

This class also contains some factory infrastructure for creating objects from
derived classes, based on an URI.
*/
class CComLink : public CComInterface, public CThread
{
public:
	SIMPLEEXCEPTIONCLASS(CConstructionFailed)
	SIMPLEEXCEPTIONCLASS(CNoDataAvailable)

	enum eState
	{
	ePending,
	eOperational,
	eClosed
	};

	/*
	Constructed object:
	comlink in pending state

	Exceptions:
	none
	*/
	CComLink();

	virtual ~CComLink();

	/*
	message:
	Reference to properly formed CBinBuffer object (NOT CHECKED)
	Reference lifetime: at least until the end of this function

	Exceptions:
	TODO
	*/
	void sendMessage(const CBinBuffer &message);

	/*
	This object:
	comlink in pending state (CHECKED)
	*/
	void threadFunc();


	inline eState getState()
	{
		CMutexLocker lock(m_State);
		return m_State.m_Value;
	}


protected:
	/*
	This object:
	Uninitialized (NOT CHECKED)

	Exceptions:
	TODO
	*/
	virtual void initialize()=0;

	/*
	message:
	Reference to properly formed CBinBuffer object (NOT CHECKED)
	Reference lifetime: at least until the end of this function

	Exceptions:
	TODO
	*/
	virtual void sendMessageDirect(const CBinBuffer &message)=0;

	/*
	Return value:
	CBinBuffer object

	Exceptions:
	CNoDataAvailable
	TODO
	*/
	virtual CBinBuffer receiveMessageDirect()=0;


private:

	CCriticalSection< std::queue<CBinBuffer> > m_SendQueue;
	CSemaphore m_HasNewSendData;

	CCriticalSection<eState> m_State;


public:
	/*
	uri:
	Reference to a properly formed CURI object (NOT CHECKED)
	Reference lifetime: at least until the end of this function

	Return value:
	Pointer to a newly constructed communication link object
	Pointer ownership is passed to the caller

	Exceptions:
	CConstructionFailed
	*/
	static CComLink *make(const CURI &uri);

	/*
	uri:
	Reference to a properly formed CString object (NOT CHECKED)
	Reference lifetime: at least until the end of this function

	Return value:
	Pointer to a newly constructed communication link object
	Pointer ownership is passed to the caller

	Exceptions:
	CConstructionFailed
	*/
	static inline CComLink *make(const CString &uri)
		{return make(CURI(uri));}


protected:

	/*
	Handler function for a communication link URI scheme.

	uri:
	Reference to a properly formed CURI object (NOT CHECKED)
	Reference lifetime: at least until the end of this function

	Return value:
	Pointer to a newly constructed communication link object
	Pointer ownership is passed to the caller

	Exceptions:
	any CException-derived class
	*/
	typedef CComLink *(*t_schemeHandler)(const CURI &uri);

	/*
	scheme:
	Reference to a properly formed CString object (NOT CHECKED)
	Reference lifetime: at least until the end of this function

	handler:
	Function pointer to a function which conforms to the
	description of t_schemeHandler

	WARNING:
	NOT thread-safe; only meant to be called at program initialization

	Exceptions:
	none
	*/
	static void registerSchemeHandler(const CString &scheme, t_schemeHandler handler);


private:


	static std::map<CString, t_schemeHandler> m_schemeHandlers;
};

#endif


