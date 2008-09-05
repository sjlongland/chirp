#!/usr/bin/python
#
# Copyright 2008 Dan Smith <dsmith@danplanet.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import time

from chirp import chirp_common, errors, memmap, ic9x_ll

class IC9xRadio(chirp_common.IcomRadio):
    BAUD_RATE = 38400
    vfo = 0
    __last = 0
    mem_upper_limit = 300

    def get_memory(self, number):
        if number < 0 or number > 999:
            raise errors.InvalidValueError("Number must be between 0 and 999")

        if (time.time() - self.__last) > 0.5:
            ic9x_ll.send_magic(self.pipe)
        self.__last = time.time()

        mframe = ic9x_ll.get_memory(self.pipe, self.vfo, number)

        return mframe.get_memory()

    def erase_memory(self, number):
        eframe = ic9x_ll.IC92MemClearFrame(self.vfo, number)

        ic9x_ll.send_magic(self.pipe)

        result = eframe.send(self.pipe)

        if len(result) == 0:
            raise errors.InvalidDataError("No response from radio")

        if result[0].get_data() != "\xfb":
            raise errors.InvalidDataError("Radio reported error")

    def get_raw_memory(self, number):
        ic9x_ll.send_magic(self.pipe)
        mframe = ic9x_ll.get_memory(self.pipe, self.vfo, number)

        return memmap.MemoryMap(mframe.get_data()[2:])

    def get_memories(self, lo=0, hi=None):
        if hi is None:
            hi = self.mem_upper_limit            

        memories = []

        for i in range(lo, hi+1):
            try:
                print "Getting %i" % i
                mem = self.get_memory(i)
                if mem:
                    memories.append(mem)
                print "Done: %s" % mem
            except errors.InvalidMemoryLocation:
                pass
            except errors.InvalidDataError, e:
                print "Error talking to radio: %s" % e
                break

        return memories
        
    def set_memory(self, memory):
        mframe = ic9x_ll.IC92MemoryFrame()
        ic9x_ll.send_magic(self.pipe)
        mframe.set_memory(memory, self.vfo)
        
        result = mframe.send(self.pipe)

        if len(result) == 0:
            raise errors.InvalidDataError("No response from radio")

        if result[0].get_data() != "\xfb":
            raise errors.InvalidDataError("Radio reported error")

class IC9xRadioA(IC9xRadio):
    vfo = 1
    mem_upper_limit = 849

class IC9xRadioB(IC9xRadio):
    vfo = 2
    mem_upper_limit = 399
