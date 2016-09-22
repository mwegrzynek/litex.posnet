# -*- coding: UTF-8 -*-
from functools import partial
from construct import Struct, Byte, Magic, String, CString, \
    OptionalGreedyRange, Switch, Pointer, Anchor, Sequence, Value

from PyCRC.CRC16 import CRC16

TabTerminated = partial(CString, terminators=b'\x09')

PosnetParameter = Struct('parameter',
    String('name', 2),
    TabTerminated('value')
)

PosnetToken = Struct('token',
    Magic('@'),
    String('value', 4)
)

PosnetFrame = Struct('frame',
    Magic(b'\x02\x09'),
    TabTerminated('instruction'),
    Switch('parameters', lambda ctx: ctx.instruction, {
            'rtcset': Sequence('params', PosnetParameter)
        },
        default=OptionalGreedyRange(PosnetParameter),
    ),
    Magic('#'),
    Value('crc16', lambda ctx: ctx.instruction + ctx.parameters)

    #CRC16().calculate()
)
