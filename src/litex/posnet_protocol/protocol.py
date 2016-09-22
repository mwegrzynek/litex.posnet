# -*- coding: UTF-8 -*-
from functools import partial
from binascii import hexlify
from construct import Struct, Byte, Bytes, Const, String, CString, \
    Switch, Pointer, Anchor, Sequence, GreedyRange, Computed, this, \
    RawCopy, Checksum, Probe, Container

from PyCRC.CRCCCITT import CRCCCITT

crc16 = lambda val: '{:04x}'.format(CRCCCITT().calculate(val)).upper()

TabTerminated = CString(terminators=b'\x09')

PosnetParameter = Struct(
    'name' / String(length=2),
    'value' / TabTerminated
)

PosnetToken = Struct(
    'name' / Const('@'),
    'value' / String(length=4)
)

PosnetErrorCode = Struct(
    'name' / Const('?'),
    'value' / TabTerminated
)

PosnetFrame = Struct(
     Const(b'\x02'),
     'summed' / RawCopy(
         Struct(
             'instruction' / TabTerminated,
             'parameters' /
                Switch(this.instruction, dict(
                     rtcset=Sequence(PosnetParameter),
                     ERR=Sequence(PosnetErrorCode)
                ),
                default=GreedyRange(PosnetParameter)
              ),
         )
      ),
      Const('#'),
      'crc' / Checksum(Bytes(4), crc16, 'summed'),
      Const('\x03'),
      'instruction' / Computed(this.summed.value.instruction),
      'parameters' / Computed(this.summed.value.parameters)
)

def build_frame(instruction, *params):
    data = Container(
        summed=Container(
            value=Container(
                instruction=instruction,
                parameters=[Container(name=name, value=value) for name, value in params]
            )
        )
    )

    return PosnetFrame.build(data)

def parse_frame(frame):
    result = PosnetFrame.parse(frame)
    return Container(
        instruction=result.instruction,
        parameters=[(param.name, param.value) for param in result.parameters]
    )
