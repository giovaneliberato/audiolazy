#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Testing module for the lazy_synth module

Copyright (C) 2012 Danilo de Jesus da Silva Bellini

This file is part of AudioLazy, the signal processing Python package.

AudioLazy is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.

Created on Tue Jul 31 2012
danilo [dot] bellini [at] gmail [dot] com
"""

#import pytest
import itertools as it

# Audiolazy internal imports
from ..lazy_synth import modulo_counter, line
from ..lazy_stream import Stream
from ..lazy_misc import almost_eq, sHz


class TestLine(object):

  def test_line(self):
    s, Hz = sHz(rate=2)
    L = line(4 * s, .1, .9)
    assert almost_eq(L, (.1 * x for x in xrange(1, 9)))

  def test_line_append(self):
    s, Hz = sHz(rate=3)
    L1 = line(2 * s, 2, 8)
    L1_should = [2, 3, 4, 5, 6, 7]
    L2 = line(1 * s, 8, -1)
    L2_should = [8, 5, 2]
    L3 = line(2 * s, -1, 9, finish=True)
    L3_should = [-1, 1, 3, 5, 7, 9]
    env = L1.append(L2).append(L3)
    env = env.map(int)
    env_should = L1_should + L2_should + L3_should
    assert list(env) == env_should


class TestModuloCounter(object):

  def test_ints(self):
    assert modulo_counter(0, 3, 2).take(8) == [0, 2, 1, 0, 2, 1, 0, 2]

  def test_floats(self):
    assert almost_eq(modulo_counter(1., 5., 3.3).take(10),
                     [1., 4.3, 2.6, .9, 4.2, 2.5, .8, 4.1, 2.4, .7])

  def test_ints_modulo_one(self):
    assert modulo_counter(0, 1, 7).take(3) == [0, 0, 0]
    assert modulo_counter(0, 1, -1).take(4) == [0, 0, 0, 0]
    assert modulo_counter(0, 1, 0).take(5) == [0, 0, 0, 0, 0]

  def test_step_zero(self):
    assert modulo_counter(7, 5, 0).take(2) == [2] * 2
    assert modulo_counter(1, -2, 0).take(4) == [-1] * 4
    assert modulo_counter(0, 3.141592653589793, 0).take(7) == [0] * 7

  def test_streamed_step(self):
    mc = modulo_counter(5, 15, modulo_counter(0, 3, 2))
    assert mc.take(18) == [5, 5, 7, 8, 8, 10, 11, 11, 13, 14, 14, 1, 2, 2, 4,
                           5, 5, 7]

  def test_streamed_start(self):
    mc = modulo_counter(modulo_counter(2, 5, 3), 7, 1)
       # start = [2,0,3,1,4,  2,0,3,1,4,  ...]
    should_mc = (Stream(2, 0, 3, 1, 4) + Stream(it.count())) % 7
    assert mc.take(29) == should_mc.take(29)

  def test_streamed_start_and_step(self):
    mc = modulo_counter(Stream(3, 3, 2), 17, it.count())
    should_step =  [0, 0, 1, 3, 6, 10, 15-17, 21-17, 28-17, 36-34, 45-34,
                    55-51, 66-68]
    should_start = [3, 3, 2, 3, 3, 2, 3, 3, 2, 3, 3, 2, 3, 3, 2, 3]
    should_mc = [a+b for a,b in it.izip(should_start, should_step)]
    assert mc.take(len(should_mc)) == should_mc