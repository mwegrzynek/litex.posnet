# -*- coding: UTF-8 -*-
from nose.tools import eq_

def test_rtcget():
    from construct import Container
    from ..protocol import PosnetFrame

    get_clock_instr = Container(
        instruction='rtcset',
        parameters=[
            Container(name='da', value='20160101')
        ]
    )

    frame = PosnetFrame.build(get_clock_instr)
    eq_(frame, 'ble')
