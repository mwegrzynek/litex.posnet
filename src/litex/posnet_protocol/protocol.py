# -*- coding: UTF-8 -*-
from functools import partial
from binascii import hexlify
from construct import Struct, Byte, Bytes, Const, String, CString, \
    Switch, Pointer, Anchor, Sequence, GreedyRange, Computed, this, \
    RawCopy, Checksum

from PyCRC.CRCCCITT import CRCCCITT

crc16 = lambda val: '{:04x}'.format(CRCCCITT().calculate(val)).upper()

TabTerminated = CString(terminators=b'\x09')

PosnetParameter = Struct(
    'name' / String(length=2),
    'value' / TabTerminated
)

PosnetToken = Struct(
    Const('@'),
    'value' / String(length=4)
)

PosnetFrame = Struct(
     Const(b'\x02'),
     'summed' / RawCopy(
         Struct(
             'instruction' / TabTerminated,
             'parameters' /
                Switch(this.instruction, dict(
                     rtcset=Sequence(PosnetParameter)
                ),
                default=GreedyRange(PosnetParameter)
              ),
         )
      ),
      Const('#'),
      'crc' / Checksum(Bytes(4), crc16, 'summed'),
      Const('\x03')
)
