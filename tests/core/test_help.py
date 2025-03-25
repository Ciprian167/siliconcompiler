# Copyright 2020 Silicon Compiler Authors. All Rights Reserved.
import siliconcompiler


def test_help():
    '''API test for help method
    '''

    chip = siliconcompiler.Chip('test')
    allkeys = chip.allkeys()
    for key in allkeys:
        h = chip.help(*key)
        assert h
        print(h)
