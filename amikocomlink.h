/*
    amikocomlink.h
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

#ifndef AMIKOCOMLINK_H
#define AMIKOCOMLINK_H

#include "comlink.h"

/*
AmikoComLink is a ComLink which implements the Amiko low-level messaging
protocol.
*/
class CAmikoComLink : public CComLink
{
public:

	/*
	uri:
	Reference to properly formed CURI object (NOT CHECKED)
	Reference lifetime: at least until the end of this function

	Constructed object:
	Connected, uninitialized link object

	Exceptions:
	CTCPConnection::CConnectException
	*/
	CAmikoComLink(const CURI &uri);

	/*
	listener:
	Reference to properly formed CTCPListener object (NOT CHECKED)
	Reference lifetime: at least until the end of this function
	TODO: lifetime at least as long as lifetime of this object??

	Constructed object:
	Connected, uninitialized link object

	Exceptions:
	CTCPConnection::CConnectException
	*/
	CAmikoComLink(const CTCPListener &listener);

	~CAmikoComLink();
};

#endif


