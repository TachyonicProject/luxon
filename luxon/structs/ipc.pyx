# cython: language_level=3, boundscheck=True
import pickle
import marshal
from cpython.ref cimport PyObject
from cython.operator cimport dereference as deref, preincrement as inc
from libcpp.string cimport string
from libcpp.pair cimport pair

def free(name):
    shmfree(name.encode('UTF-8'))

cdef extern from "ipc.h":
    cdef cppclass Bytes:
        Bytes()
        unsigned long int size()
        unsigned char * data()
        void clear()
        void erase(void *)
        void * begin()

    void shmfree(const char *)

    cdef cppclass BoostHashMap:
        BoostHashMap(const char *, long unsigned int, char *) except +
        void set(char *, long unsigned, char *, long unsigned int) except +
        Bytes get(char *, long unsigned) except +
        void erase(char *, long unsigned) except +
        void clear() except +
        Bytes iter(long unsigned) except +
        unsigned long int size()
        unsigned long int free()


cdef class BytesHashMap:
    cdef BoostHashMap *hashmap
    def __cinit__(self, shm_name, size, map_name='default'):
        self.hashmap = new BoostHashMap(shm_name.encode('UTF-8'), size, map_name.encode('UTF-8'))

    def __setitem__(self, key, value):
        key_len = len(key)
        value_len = len(value)
        self.hashmap.set(key, key_len, value, value_len)

    def __getitem__(self, key):
        key_len = len(key)
        try:
            key_value = self.hashmap.get(key, key_len)
        except RuntimeError:
            raise KeyError(key) from None
        return key_value.data()[:key_value.size()]

    def __iter__(self):
        cnt = 0
        while True:
            try:
                key_value = self.hashmap.iter(cnt)
                cnt += 1
                yield key_value.data()[:key_value.size()]
            except RuntimeError:
                break

    def __delitem__(self, key):
        key_len = len(key)
        try:
            self.hashmap.erase(key, key_len)
        except RuntimeError:
            raise KeyError(key) from None

    def clear(self):
        self.hashmap.clear()

    def size(self):
        return self.hashmap.size()

    def free(self):
        return self.hashmap.free()


cdef class BaseSerializedHashMap:
    _CODEC = None 

    cdef BoostHashMap *hashmap

    def __cinit__(self, shm_name, size, map_name='default'):
        self.hashmap = new BoostHashMap(shm_name.encode('UTF-8'), size, map_name.encode('UTF-8'))

    def __setitem__(self, key, value):
        key = self._CODEC.dumps(key)
        key_len = len(key)
        value = self._CODEC.dumps(value)
        value_len = len(value)
        self.hashmap.set(key, key_len, value, value_len)

    def __getitem__(self, key):
        key = self._CODEC.dumps(key)
        key_len = len(key)
        try:
            key_value = self.hashmap.get(key, key_len)
        except RuntimeError:
            raise KeyError(key) from None
        return self._CODEC.loads(key_value.data()[:key_value.size()])

    def __iter__(self):
        cnt = 0
        while True:
            try:
                key_value = self.hashmap.iter(cnt)
                cnt += 1
                yield self._CODEC.loads(key_value.data()[:key_value.size()])
            except RuntimeError:
                break

    def __delitem__(self, key):
        key = self._CODEC.dumps(key)
        key_len = len(key)
        try:
            self.hashmap.erase(key, key_len)
        except RuntimeError:
            raise KeyError(key) from None

    def clear(self):
        self.hashmap.clear()

    def size(self):
        return self.hashmap.size()

    def free(self):
        return self.hashmap.free()

cdef class MarshalHashMap(BaseSerializedHashMap):
    _CODEC = marshal

cdef class PickleHashMap(BaseSerializedHashMap):
    _CODEC = pickle
