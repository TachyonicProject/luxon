==================
Decorator
==================

.. autofunction:: luxon.utils.decorator.decorator


Example Usage

.. code:: python 

	def memoize(expiry_time=3600):
    		def _memoize(func, *args, **kw):
        		return cache(expiry_time, func, *args, **kw)[0]
    		return decorator(_memoize)
