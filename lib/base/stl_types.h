#ifndef __lib_base_stl_types_h__
#define __lib_base_stl_types_h__

//
// This file contains simple and reusable STL-based typedefs.
//

#include <list>
#include <map>
#include <set>
#include <string>
#include <vector>

typedef std::vector<unsigned char> byteVector;
typedef std::list<byteVector> byteVectorList;

typedef std::list<int> intList;
typedef std::pair<int, int> intPair;
typedef std::list<intPair> intPairList;

typedef std::list<std::string> stringList;
typedef std::set<std::string> stringSet;
typedef std::map<std::string, std::string> stringMap;
typedef std::vector<stringMap> stringMapVector;

#endif
