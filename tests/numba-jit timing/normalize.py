
# Representative results obtained with numba 0.53.1 and numpy 1.21.2 (2021-10):
#
# ns = 2*10**5
# nit = 10000
# a = 10
#
# Numba-jit-serial total time (s): 5.130236864089966
# Numba-jit-parallel total time (s): 1.2612504959106445
# Numba-jit-serial-mem-alloc total time (s): 4.855409622192383
# Numba-jit-parallel-mem-alloc total time (s): 1.2957305908203125
# Numpy total time (s): 6.774352788925171
#
#
# ns = 2*10**3
# nit = 100000
# a = 10
#
# Numba-jit-serial total time (s): 0.6369800567626953
# Numba-jit-parallel total time (s): 11.904999256134033
# Numba-jit-serial-mem-alloc total time (s): 0.6759977340698242
# Numba-jit-parallel-mem-alloc total time (s): 10.418000936508179
# Numpy total time (s): 0.47800302505493164

import time

import numpy as np

from numpy.random import random
import numba


@numba.jit(nopython=True)
def _normalize(src, a):
    """A serial version."""
    for i in range(src.shape[0]):
        src[i] = src[i] / a


@numba.jit(nopython=True, parallel=True)
def _normalizep(src, a):
    """A parallel version."""
    for i in numba.prange(src.shape[0]):
        src[i] = src[i] / a


@numba.jit(nopython=True)
def _normalize2(dst, src, a):
    """A serial version with memory pre-allocation."""
    for i in range(dst.shape[0]):
        dst[i] = src[i] / a


@numba.jit(nopython=True, parallel=True)
def _normalize2p(dst, src, a):
    """A parallel version with memory pre-allocation."""
    for i in numba.prange(dst.shape[0]):
        dst[i] = src[i] / a


ns = 2*10**5
nit = 10000
a = 10


src = random(ns)
dst = np.zeros(ns, dtype=np.float64)


# Calls the functions once to trigger their compilation.
_normalize(src, a)
_normalizep(src, a)
_normalize2(dst, src, a)
_normalize2p(dst, src, a)


startt = time.time()
for i in range(nit):
    _normalize(src, a)
endt = time.time()
print(f"Numba-jit-serial total time (s): {endt-startt}")


startt = time.time()
for i in range(nit):
    _normalizep(src, a)
endt = time.time()
print(f"Numba-jit-parallel total time (s): {endt-startt}")


startt = time.time()
for i in range(nit):
    _normalize2(dst, src, a)
endt = time.time()
print(f"Numba-jit-serial-mem-alloc total time (s): {endt-startt}")


startt = time.time()
for i in range(nit):
    _normalize2p(dst, src, a)
endt = time.time()
print(f"Numba-jit-parallel-mem-alloc total time (s): {endt-startt}")


startt = time.time()
for i in range(nit):
    src = src / a
endt = time.time()
print(f"Numpy total time (s): {endt-startt}")