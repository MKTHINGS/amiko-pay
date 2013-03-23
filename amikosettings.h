/*
    amikosettings.h
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

#ifndef AMIKOSETTINGS_H
#define AMIKOSETTINGS_H

#include <vector>

#include "binbuffer.h"
#include "uriparser.h"
#include "key.h"

class CAmikoSettings
{
public:

	class CLink
	{
	public:
		CLink() : m_remoteURI("dummy://localhost") {}
		CURI m_remoteURI;
		CKey m_localKey;
		CKey m_remoteKey; //must either be empty or correspond with m_remoteURI
	};
	std::vector<CLink> m_links;
};

#endif
