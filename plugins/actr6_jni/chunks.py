# -*- coding:	utf-8 -*-
#===============================================================================
# This file is part of ACTR6_JNI.
# Copyright (C) 2012-2013 Ryan Hope <rmh3093@gmail.com>
#
# ACTR6_JNI is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ACTR6_JNI is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ACTR6_JNI.  If not, see <http://www.gnu.org/licenses/>.
#===============================================================================

from itertools import count

class Chunk(object):

	_ids = count(0)

	def __init__(self, name, **slots):
		self._id = self._ids.next()
		if name == None:
			self.name = "vc%d" % self._id
		else:
			self.name = name
		self.slots = slots

	def get_chunk(self, name=None, empty=False):
		if name == None:
			name = str(self.name)
		chunk = {"name": name, "slots": {}}
		if not empty:
			for s, v in self.slots.iteritems():
				chunk["slots"][s] = v
		return chunk

class VisualChunk(Chunk):

	def __init__(self, name, screenx, screeny, width = None, height = None, color = None, size = None, value = None, **slots):
		super(VisualChunk, self).__init__(name, **slots)
		self.screenx = screenx
		self.screeny = screeny
		self.width = width
		self.height = height
		self.color = color
		self.size = size
		self.value = value

	def add_base_slots(self, chunk):
		chunk["slots"]["screen-x"] = self.screenx
		chunk["slots"]["screen-y"] = self.screeny
		if self.width:
			chunk["slots"]["width"] = self.width
		if self.height:
			chunk["slots"]["height"] = self.height
		if self.color:
			chunk["slots"]["color"] = self.color
		if self.size:
			chunk["slots"]["size"] = self.size
		if self.value:
			chunk["slots"]["value"] =  self.value
		return chunk

	def get_visual_object(self):
		chunk = super(VisualChunk, self).get_chunk(name="%s-obj" % str(self.name))
		chunk = self.add_base_slots(chunk)
		return chunk

	def get_visual_location(self):
		chunk = super(VisualChunk, self).get_chunk(name="%s-loc" % str(self.name), empty=True)
		chunk = self.add_base_slots(chunk)
		if "kind" in self.slots.keys():
			chunk["slots"]["kind"] =  self.slots["kind"]
		return chunk
