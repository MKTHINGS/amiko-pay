/*
    test.h
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

#include <vector>

class CTest;

class CFailure
{
public:
	CFailure(const CString &testName, const CString &description) :
		m_testName(testName), m_description(description)
		{}

	CString m_testName, m_description;
};

/*
TODO: document
*/
//implemented in tests_main.cpp
std::vector<CTest *> &getTestList();
std::vector<CFailure> &getFailureList();

/*
TODO: document
*/
class CTest
{
public:

	CTest()
	{
		getTestList().push_back(this);
	}

	virtual const char *getName() const=0;
	virtual void run()=0;


protected:

	inline void test(const char *description, bool result) const
	{
		if(result)
		{
			printf("%s: OK\n", description);
		}
		else
		{
			printf("%s: FAIL\n", description);
			getFailureList().push_back(CFailure(getName(), description));
		}
	}

	template<class T>
	inline bool throws(void (*function)(void *), void *arg) const
	{
		try
		{
			function(arg);
		}
		catch(T &e)
		{
			return true;
		}
		return false;
	}
};

