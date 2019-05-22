#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <iostream> 
#include <unordered_map> 
#include <boost/interprocess/managed_shared_memory.hpp>
#include <boost/interprocess/allocators/allocator.hpp>
#include <boost/unordered_map.hpp>     //boost::unordered_map
#include <functional>                  //std::equal_to
#include <boost/functional/hash.hpp>   //boost::hash

using namespace std; 

static PyObject *SpamError;

class Shared
{ 
    // Access specifier 
    public: 

    //Note that unordered_map<Key, MappedType>'s value_type is std::pair<const Key, MappedType>,
    //so the allocator must allocate that pair.
    typedef char * KeyType;
    typedef std::vector<unsigned char> MappedType;
    typedef std::pair<char *, std::vector<unsigned char>> ValueType;

    //Typedef the allocator
    typedef boost::interprocess::allocator<ValueType, boost::interprocess::managed_shared_memory::segment_manager> ShmemAllocator;

    //Alias an unordered_map of ints that uses the previous STL-like allocator.
    typedef boost::unordered_map
      < KeyType               , MappedType
      , boost::hash<KeyType>  ,std::equal_to<KeyType>
      , ShmemAllocator>
    MyHashMap;

    MyHashMap *myhashmap;

    Shared()
    {
        boost::interprocess::shared_memory_object::remove("kakas"); 
        boost::interprocess::managed_shared_memory segment(boost::interprocess::open_or_create, "kakas", 65535);

        //Construct a shared memory hash map.
        //Note that the first parameter is the initial bucket count and
        //after that, the hash function, the equality function and the allocator
        myhashmap = segment.construct<MyHashMap>("MyHashMap")  //object name
            ( 3, boost::hash<char *>(), std::equal_to<char *>()                  //
            , segment.get_allocator<ValueType>());                         //allocator instance
    }

    // Member Functions() 
    void set(char * key, std::vector<unsigned char> value) 
    {
        boost::interprocess::managed_shared_memory segment(boost::interprocess::open_only, "kakas");
        myhashmap->insert(ValueType(key, value));
    }

    std::vector<unsigned char> get(char * key)
    {
        boost::interprocess::managed_shared_memory segment(boost::interprocess::open_only, "kakas");
        MyHashMap::iterator f = myhashmap->find(key);
        if (f != myhashmap->end()) {
            return f->second;
        }
        return std::vector<unsigned char>(0);
    }
}; 

PyObject* construct(PyObject* self, PyObject* args)
{
    Shared* shared = new Shared();

    // Create a Python capsule with a pointer to `Shared` object
    PyObject* sharedCapsule = PyCapsule_New((void *)shared, "SharedPtr", NULL);
    PyCapsule_SetPointer(sharedCapsule, (void *)shared);

    return Py_BuildValue("O", sharedCapsule);   // "O" means "Python object"
}

PyObject* py_set(PyObject* self, PyObject* args)
{
    // Arguments passed from Python
    PyObject* Capsule_;   // Capsule with the pointer to `Car` object
    char * key_;
    const char * value_;

    // Process arguments
    PyArg_ParseTuple(args, "Osy",
                     &Capsule_,
                     &key_,
                     &value_);

    std::vector<unsigned char> vec(value_, value_+128);

    // Get the pointer to `Car` object
    Shared* shared = (Shared*)PyCapsule_GetPointer(Capsule_, "SharedPtr");
    shared->set(key_, vec);

    // Return nothing
    return Py_BuildValue("");
}

PyObject* py_get(PyObject* self, PyObject* args)
{
    // Arguments passed from Python
    PyObject* Capsule_;
    char * key_;

    // Process arguments
    PyArg_ParseTuple(args, "Os",
                     &Capsule_,
                     &key_);


    Shared* shared = (Shared*)PyCapsule_GetPointer(Capsule_, "SharedPtr");

    std::vector<unsigned char> value = shared->get(key_);
    const char * blah = reinterpret_cast<const char*>(value.data());
    return Py_BuildValue("y", blah);
}

static PyMethodDef SharedMethods[] = {
    {"construct",                   // C++/Py Constructor
      construct, METH_VARARGS,
     "Create `Shared` object"},

    {"set",                     // C++/Py wrapper for `set`
      py_set, METH_VARARGS,
     "Set Item on 'Shared' object."},

    {"get",                       // C++/Py wrapper for `get`
      py_get, METH_VARARGS,
     "get Item on 'Shared' object."},

    {NULL, NULL, 0, NULL} // Sentinel 
};



static struct PyModuleDef c_shared = {
    PyModuleDef_HEAD_INIT,
    "c_shared",   // name of module
    NULL, // module documentation, may be NULL
    -1,   // size of per-interpreter state of the module,
          //  or -1 if the module keeps state in global variables.
    SharedMethods
};

PyMODINIT_FUNC PyInit_c_shared(void)
{
    PyObject *m;

    m = PyModule_Create(&c_shared);
    if (m == NULL)
        return NULL;

    SpamError = PyErr_NewException("c_shared.error", NULL, NULL);
    Py_INCREF(SpamError);
    PyModule_AddObject(m, "error", SpamError);
    return m;
}

int main(int argc, char *argv[])
{
    wchar_t *program = Py_DecodeLocale(argv[0], NULL);
    if (program == NULL) {
        fprintf(stderr, "Fatal error: cannot decode argv[0]\n");
        exit(1);
    }

    // Add a built-in module, before Py_Initialize
    PyImport_AppendInittab("shared", PyInit_c_shared);

    // Pass argv[0] to the Python interpreter 
    Py_SetProgramName(program);

    // Initialize the Python interpreter.  Required. 
    Py_Initialize();

    // Optionally import the module; alternatively,
    //   import can be deferred until the embedded script
    //   imports it. 
    PyImport_ImportModule("c_shared");

    PyMem_RawFree(program);
    return 0;
}
