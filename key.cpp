/*
    key.cpp
	Copyright (C) 2009-2012 by the Bitcoin developers
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

#include <openssl/ecdsa.h>
#include <openssl/obj_mac.h>

#include "key.h"


CKey::CKey()
{
	m_KeyData = EC_KEY_new_by_curve_name(NID_secp256k1);
	if(m_KeyData == NULL)
		throw CConstructError("CKey::CKey() : EC_KEY_new_by_curve_name failed");
}


CKey::CKey(const CKey &b)
{
	m_KeyData = EC_KEY_dup(b.m_KeyData);
	if(m_KeyData == NULL)
		throw CConstructError("CKey::CKey(const CKey&) : EC_KEY_dup failed");
}


CKey::~CKey()
{
	EC_KEY_free(m_KeyData);
}


CKey &CKey::operator=(const CKey& b)
{
	if(!EC_KEY_copy(m_KeyData, b.m_KeyData))
		throw CKeyError("CKey::operator=(const CKey&) : EC_KEY_copy failed");	
	return *this;
}


void CKey::makeNewKey()
{
	if(!EC_KEY_generate_key(m_KeyData))
		throw CKeyError("CKey::makeNewKey() : EC_KEY_generate_key failed");
}


void CKey::setPublicKey(const CBinBuffer &key)
{
	const unsigned char *pbegin = &key[0];
	if(!o2i_ECPublicKey(&m_KeyData, &pbegin, key.size()))
	{
		//TODO: reset key state
		throw CKeyError("CKey::setPublicKey(const CBinBuffer &): o2i_ECPublicKey failed");
	}
}


CBinBuffer CKey::getPublicKey() const
{
	int size = i2o_ECPublicKey(m_KeyData, NULL);
	if(!size)
		throw CKeyError("CKey::getPublicKey() : i2o_ECPublicKey failed");

	CBinBuffer ret;
	ret.resize(size);
	unsigned char *pbegin = &ret[0];
	if(i2o_ECPublicKey(m_KeyData, &pbegin) != size)
		throw CKeyError("CKey::getPublicKey() : i2o_ECPublicKey returned unexpected size");

	return ret;
}


void CKey::setPrivateKey(const CBinBuffer &key)
{
    const unsigned char *pbegin = &key[0];
    if(!d2i_ECPrivateKey(&m_KeyData, &pbegin, key.size()))
    {
		// If vchPrivKey data is bad d2i_ECPrivateKey() can
		// leave pkey in a state where calling EC_KEY_free()
		// crashes.
		// TODO: find a way to prevent this
		throw CKeyError("CKey::setPrivateKey(const BinBuffer &): d2i_ECPrivateKey failed");
    }

    // In testing, d2i_ECPrivateKey can return true
    // but fill in pkey with a key that fails
    // EC_KEY_check_key, so:
    if(!EC_KEY_check_key(m_KeyData))
    {
		// If vchPrivKey data is bad d2i_ECPrivateKey() can
		// leave pkey in a state where calling EC_KEY_free()
		// crashes.
		// TODO: find a way to prevent this
		throw CKeyError("CKey::setPrivateKey(const BinBuffer &): EC_KEY_check_key failed");
    }
}


CBinBuffer CKey::getPrivateKey() const
{
	int size = i2d_ECPrivateKey(m_KeyData, NULL);
	if(!size)
		throw CKeyError("CKey::getPrivateKey() : i2d_ECPrivateKey failed");

	CBinBuffer ret;
	ret.resize(size);
	unsigned char *pbegin = &ret[0];
	if(i2d_ECPrivateKey(m_KeyData, &pbegin) != size)
		throw CKeyError("CKey::getPrivateKey() : i2d_ECPrivateKey returned unexpected size");

	return ret;
}


CBinBuffer CKey::sign(const CBinBuffer &hash) const
{
	unsigned int size = ECDSA_size(m_KeyData);
	CBinBuffer ret;
	ret.resize(size); // Make sure it is big enough
	if(!ECDSA_sign(0, &hash[0], hash.size(), &ret[0], &size, m_KeyData))
		throw CKeyError("CKey::sign(const CBinBuffer &): ECDSA_sign failed");

	ret.resize(size); // Shrink to fit actual size
	return ret;
}


bool CKey::verify(const CBinBuffer &hash, const CBinBuffer &signature) const
{
	// -1 = error, 0 = bad sig, 1 = good
	int result = ECDSA_verify(0, &hash[0], hash.size(), &signature[0], signature.size(), m_KeyData);
	if(result == 1) return true;
	if(result == 0) return false;
	throw CKeyError("CKey::verify(const CBinBuffer &, const CBinBuffer &) failed");
}

