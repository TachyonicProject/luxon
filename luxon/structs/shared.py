from luxon.structs import c_shared


class Shared(object):
    def __init__(self):
        self._capsule = c_shared.construct()

    def set(self, key, value):
        return c_shared.set(self._capsule, key, value)

    def get(self, key):
        return c_shared.get(self._capsule, key)


#shared = Shared()
#shared.set('kief', b'123')
#print(shared.get('kief'))
