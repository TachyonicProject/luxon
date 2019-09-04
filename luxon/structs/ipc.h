/*
 Copyright (c) 2019 Christiaan Rademan <christiaan.rademan@gmail.com>
 All rights reserved.

 Redistribution and use in source and binary forms, with or without
 modification, are permitted provided that the following conditions are met:

 * Redistributions of source code must retain the above copyright notice, this                                            
   list of conditions and the following disclaimer.

 * Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

 * Neither the name of the copyright holders nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

 THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
 LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF
 THE POSSIBILITY OF SUCH DAMAGE.
*/

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <iostream>
#include <string>
#include <boost/interprocess/sync/interprocess_sharable_mutex.hpp>
#include <boost/interprocess/sync/interprocess_upgradable_mutex.hpp>
#include <boost/interprocess/sync/sharable_lock.hpp>
#include <boost/interprocess/sync/upgradable_lock.hpp>
#include <boost/interprocess/managed_shared_memory.hpp>
#include <boost/interprocess/allocators/allocator.hpp>
#include <boost/interprocess/containers/vector.hpp>
#include <boost/container/scoped_allocator.hpp>
#include <boost/interprocess/sync/scoped_lock.hpp>
#include <boost/interprocess/containers/map.hpp>
#include <boost/unordered_map.hpp>
#include <exception>
#include <boost/interprocess/containers/string.hpp>
#include <boost/interprocess/containers/list.hpp>

using boost::unordered_map;
using boost::interprocess::map;
using boost::interprocess::basic_string;


namespace bip = boost::interprocess;
namespace bcon = boost::container;


typedef unsigned char Byte;
typedef bip::allocator<Byte, bip::managed_shared_memory::segment_manager> ByteAlloc;
typedef bip::vector<Byte> Bytes;
typedef bip::vector<Byte, ByteAlloc> ShmBytes;

template <typename BytesContainer>
struct BytesHash
{
    std::size_t operator()(BytesContainer const& c) const
    {
        return boost::hash_range(c.begin(), c.end());
    }
};

typedef ShmBytes ShmKeyType;
typedef ShmBytes ShmMappedType;
typedef std::pair<ShmKeyType, ShmMappedType> ValueType;

typedef bip::allocator<
    ValueType,
    bip::managed_shared_memory::segment_manager> ShmMapAlloc;

typedef unordered_map<
    ShmKeyType,
    ShmMappedType,
    BytesHash<ShmKeyType>,
    std::equal_to<ShmKeyType>,
    bcon::scoped_allocator_adaptor<ShmMapAlloc> > ShmMap;


struct StopIteration : public std::exception {
   const char * what () const throw () {
      return "StopIteration";
   }
};

struct KeyError : public std::exception {
   const char * what () const throw () {
      return "Bytes 'Key' not found";
   }
};

void shmfree(const char *name)
{
    bip::shared_memory_object::remove(name);
}

class BoostHashMap {
    private:
        bip::managed_shared_memory shm;
        const char *shm_name;
        const char *map_name;
    public:
        BoostHashMap(const char *shm_name, long unsigned int size, const char *map_name)
            : shm(bip::open_or_create, shm_name, size)
        {
            this->shm_name = shm_name;
            this->map_name = map_name;
        }
        ~BoostHashMap()
        {
        }


        void set(char *key, long unsigned key_len, char *value, long unsigned int value_len)
        {
            bip::interprocess_sharable_mutex *mtx = this->shm.find_or_construct<boost::interprocess::interprocess_sharable_mutex>("mtx")();
            bip::scoped_lock<bip::interprocess_sharable_mutex> lock(*mtx);
            ShmMap *shm_map = this->shm.find_or_construct<ShmMap>(this->map_name)(this->shm.get_segment_manager());
            shm_map->erase(ShmKeyType { key, key+key_len, this->shm.get_segment_manager() });
            shm_map->insert(ValueType(ShmKeyType { key, key+key_len, this->shm.get_segment_manager() }, ShmMappedType { value, value+value_len, this->shm.get_segment_manager() }));
        }

        Bytes get(char *key, long unsigned key_len)
        {
            bip::interprocess_sharable_mutex *mtx = this->shm.find_or_construct<boost::interprocess::interprocess_sharable_mutex>("mtx")();
            bip::scoped_lock<bip::interprocess_sharable_mutex> lock_sharable(*mtx);
            ShmMap *shm_map = this->shm.find_or_construct<ShmMap>(this->map_name)(this->shm.get_segment_manager());
            ShmMap::iterator f = shm_map->find(ShmKeyType { key, key+key_len, this->shm.get_segment_manager() });
            if (f != shm_map->end())
            {
                return Bytes { f->second.data(), f->second.data()+f->second.size() };
            } 
            else
            {
                throw KeyError();
            }
        }

        void erase(char *key, long unsigned key_len) {
            bip::interprocess_sharable_mutex *mtx = this->shm.find_or_construct<boost::interprocess::interprocess_sharable_mutex>("mtx")();
            bip::scoped_lock<bip::interprocess_sharable_mutex> lock(*mtx);
            ShmMap *shm_map = this->shm.find_or_construct<ShmMap>(this->map_name)(this->shm.get_segment_manager());
            shm_map->erase(ShmKeyType { key, key+key_len, this->shm.get_segment_manager() });
        }

        Bytes iter(long unsigned pos) {
            bip::interprocess_sharable_mutex *mtx = this->shm.find_or_construct<boost::interprocess::interprocess_sharable_mutex>("mtx")();
            bip::scoped_lock<bip::interprocess_sharable_mutex> lock(*mtx);
            ShmMap *shm_map = this->shm.find_or_construct<ShmMap>(this->map_name)(this->shm.get_segment_manager());
            ShmMap::iterator f = shm_map->begin();
            advance(f, pos);
            if (f != shm_map->end())
            {
                return Bytes { f->second.data(), f->second.data()+f->second.size() };
            }
            else
            {
                throw StopIteration();
            }
        }

        void clear()
        {
            bip::interprocess_sharable_mutex *mtx = this->shm.find_or_construct<boost::interprocess::interprocess_sharable_mutex>("mtx")();
            bip::scoped_lock<bip::interprocess_sharable_mutex> lock(*mtx);
            ShmMap *shm_map = this->shm.find_or_construct<ShmMap>(this->map_name)(this->shm.get_segment_manager());
            shm_map->clear();
        }

        long unsigned size()
        {
            return this->shm.get_size();
        }

        long unsigned free()
        {
            return this->shm.get_free_memory();
        }
};
