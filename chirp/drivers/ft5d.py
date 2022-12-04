# Copyright 2010 Dan Smith <dsmith@danplanet.com>
# Copyright 2014 Angus Ainslie <angus@akkea.ca>
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

from .. import bitwise


MEM_FORMAT = """
#seekto 0x12C0;
struct {
  u8 nosubvfo:1,
     unknown:3,
     pskip:1,
     skip:1,
     used:1,
     valid:1;
} flag[999];

#seekto 0x1800;
struct {
  u8 u0:6,
     band:2;      // Band select: 0x02 = 2m; 0x03 = 70cm
  u8 u1:2,
     shift:2,
     u2:4;
  bbcd freq[3];
  u8 u3:2,  // always 0b11???
     mode:3,      // 0b000 = FM, 0b010 = AMS C4FM, 0b100 = C4FM
     sqltype:3;   // SQL Type: off/tone/tone sql/dcs/rev tone/pr freq/pager
  u8 u4;
  u8 u5;
  char label[16];
  u8 u6;
  bbcd offset;
  u8 u7;
  u8 tone;
  u8 u8;
  u8 u9;
  u8 u10;
  u8 u11;
} memory[999];
"""

SHIFT = [
        "SIMPLEX", "-ve", "+ve"
]
MODE = [
        "FM",
        "??? 0b001",
        "AMS C4FM",
        "??? 0b011",
        "C4FM",
        "??? 0b101",
        "??? 0b110",
        "??? 0b111",
]
SQL_TYPE = [
        "OFF", "Tone", "ToneSql", "DCS", "RevTone", "PrFreq", "Pager"
]
TONE_FREQ = [
        67.0, 69.3, 71.9, 74.4, 77.0, 79.7, 82.5, 85.4, 88.5, 91.5, 94.8,
        97.4, 100.0, 103.5, 107.2, 110.9, 114.8, 118.8, 123.0, 127.3, 131.8,
        136.5, 141.3, 146.2, 151.4, 156.7, 159.8, 162.2, 165.5, 167.9, 171.3,
        173.8, 177.3, 179.9, 183.5, 186.2, 189.9, 192.8, 196.6, 199.5, 203.5,
        206.5, 210.7, 218.1, 225.7, 229.1, 233.6, 241.8, 250.3, 254.1,
]


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("memory", help="MEMORY.dat file")

    args = ap.parse_args()
    with open(args.memory, "rb") as memfile:
        tree = bitwise.parse(MEM_FORMAT, memfile.read())
        #print(repr(tree))

        for ch in range(0, 999):
            flag = tree.flag[ch]
            mem = tree.memory[ch]

            if flag.used and flag.valid:
                print("======= channel %3d =======" % (ch+1))
                print(repr(flag))
                print(repr(mem))

                freq = int(mem.freq)

                # Frequency is truncated to integer kHz
                # We can figure out the missing bit from the last digit
                freq_leastsig = freq % 10
                if freq_leastsig == 6:
                    freq += 0.25
                elif freq_leastsig in (2, 7):
                    freq += 0.5
                elif freq_leastsig == 8:
                    freq += 0.75

                offset = int(mem.offset) * 100

                print("Freq:     %8.1f kHz" % freq)
                print("Offset:       %4d kHz %s" % (offset, SHIFT[mem.shift]))
                print("Mode:     %12s" % MODE[mem.mode])
                print("SQL Type: %12s" % SQL_TYPE[mem.sqltype])
                print("CTCSS:        %5.1f Hz" % TONE_FREQ[mem.tone])

                # We don't know what these mean yet
                assert mem.u0 in (0x00, 0x10)
                assert mem.u1 == 0x00
                assert mem.u2 in (0x00, 0x04, 0x07)
                assert mem.u3 == 0x03
                assert mem.u4 == 0x00
                assert mem.u5 == 0x00
                assert mem.u6 == 0x00
                assert mem.u7 == 0x00
                assert mem.u8 in (0x00, 0x01)
                assert mem.u9 == 0x0d
                assert mem.u10 in (0x00, 0x80)
                assert mem.u11 in (0x08, 0x18)
