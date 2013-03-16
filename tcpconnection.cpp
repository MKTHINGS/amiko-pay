/*
    tcpconnection.cpp
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
#include <cstdlib>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h>
#include <unistd.h>
#include <errno.h>

#include "tcpconnection.h"

/*
Wrapper-class of getaddrinfo functionality, to have a RAII way of dealing
with its result data structure.
*/
class CAddrInfo
{
public:
	CAddrInfo(const CString &hostname, const CString &service, const struct addrinfo &hints)
	{
		int s = getaddrinfo(hostname.c_str(), service.c_str(), &hints, &m_Info);
		if (s != 0)
			throw CTCPConnection::CConnectException(CString::format("getaddrinfo() failed: %s", 256, gai_strerror(s)));
	}

	~CAddrInfo()
	{
		freeaddrinfo(m_Info);
	}

	struct addrinfo *m_Info;
};


CTCPConnection::CTCPConnection(const CString &hostname, const CString &service)
{
	struct addrinfo hints;

	// Obtain address(es) matching host/port
	memset(&hints, 0, sizeof(struct addrinfo));
	hints.ai_family = AF_UNSPEC;     // Allow IPv4 or IPv6
	hints.ai_socktype = SOCK_STREAM; // TCP
	hints.ai_flags = 0;
	hints.ai_protocol = 0;           // Any protocol

	CAddrInfo result(hostname, service, hints);

	/*
	getaddrinfo() returns a list of address structures.
	Try each address until we successfully connect().
	If socket() (or connect()) fails, we (close the socket
	and) try the next address.
	*/
	struct addrinfo *rp;
	for(rp = result.m_Info; rp != NULL; rp = rp->ai_next)
	{
		m_FD = socket(rp->ai_family, rp->ai_socktype, rp->ai_protocol);
		if(m_FD == -1)
			continue;

		if(connect(m_FD, rp->ai_addr, rp->ai_addrlen) != -1)
			break; // Success

		close(m_FD);
	}

	if(rp == NULL) // No address succeeded
		throw CConnectException("Failed to connect");
}


CTCPConnection::CTCPConnection(const CTCPListener &listener)
{
	//TODO: use this client info if needed
	struct sockaddr addr;
	socklen_t addrlen;

	m_FD = accept(listener.getFD(), &addr, &addrlen);
	if(m_FD == -1)
		throw CConnectException(CString::format("accept() failed: error code: %d", 256, errno));
}


CTCPConnection::~CTCPConnection()
{
	//TODO: check return values and log (not throw) errors
	shutdown(m_FD, SHUT_RDWR);
	close(m_FD);
}


void CTCPConnection::send(const CBinBuffer &buffer) const
{
	size_t start = 0;
	while(start < buffer.size())
	{
		ssize_t ret = write(m_FD, &(buffer[start]), buffer.size() - start);

		if(ret < 0)
			throw CSendException(CString::format("Error sending to TCP connection; error code: %d", 256, errno));

		if(ret > ssize_t(buffer.size() - start))
			throw CSendException(CString::format(
				"Error sending to TCP connection; tried to send %d bytes, but result says %d bytes were sent",
				256, buffer.size() - start, ret));

		start += ret;
	}
}


void CTCPConnection::receive(CBinBuffer &buffer, int timeout)
{
	if(m_ReceiveBuffer.size() >= buffer.size())
	{
		buffer.assign(
			m_ReceiveBuffer.begin(), m_ReceiveBuffer.begin()+buffer.size());
		m_ReceiveBuffer.erase(
			m_ReceiveBuffer.begin(), m_ReceiveBuffer.begin()+buffer.size());
		return;
	}

	CBinBuffer newBytes; newBytes.resize(buffer.size() - m_ReceiveBuffer.size());
	ssize_t ret = read(m_FD, &(newBytes[0]), newBytes.size());

	if(ret == 0)
		throw CReceiveException("Unexpected close of TCP connection");

	if(ret < 0)
		throw CReceiveException(CString::format(
			"Error receiving from TCP connection; error code: %d", 256, errno));

	if(ret < ssize_t(newBytes.size()))
	{
		m_ReceiveBuffer += newBytes;
		throw CTimeoutException("Data not available");
	}

	buffer = m_ReceiveBuffer + newBytes;
	m_ReceiveBuffer.clear();
}


