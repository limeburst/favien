""":mod:`favien` --- Favien
~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import platform


if platform.python_implementation() == 'PyPy':
    # Monkey patches for PyPy
    from psycopg2cffi.compat import register
    register()
