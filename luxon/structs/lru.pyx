# cython: language_level=3, boundscheck=True
import pickle
import marshal
from cpython.ref cimport PyObject
from libcpp.string cimport string
from cython.operator cimport dereference as deref, preincrement as inc
from libcpp.string cimport string
from libcpp.pair cimport pair

cdef extern from "lru.h":
    cdef cppclass LRUCache:
        LRUCache(int capacity) except +
        void put(string, string) except +
        string get(string) except +


cdef class LRU:
    cdef LRUCache *_lru
    def __cinit__(self, size):
        self._lru = new LRUCache(size)

    def __setitem__(self, key, value):
        self._lru.put(key, value)

    def __getitem__(self, key):
        try:
            key_value = self._lru.get(key)
        except RuntimeError:
            raise KeyError(key) from None
        return key_value

    def get(self, key, default=None):
        try:
            return self._lru.get(key)
        except RuntimeError:
            return default
