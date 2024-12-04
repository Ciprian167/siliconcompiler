import pathlib
import os

import pytest

from siliconcompiler.schema import Schema
from siliconcompiler.schema.schema_cfg import scparam
from siliconcompiler import Chip
from siliconcompiler.targets import asic_demo


def test_list_of_lists():
    cfg = {}
    scparam(cfg, ['test'], sctype='[[str]]', shorthelp='Test')

    schema = Schema(cfg=cfg)
    schema.set('test', [['foo']])

    assert schema.get('test') == [['foo']]


def test_list_of_bools():
    cfg = {}
    scparam(cfg, ['test'], sctype='[bool]', shorthelp='Test')

    schema = Schema(cfg=cfg)
    schema.set('test', [True, False])

    assert schema.get('test') == [True, False]


def test_pernode_mandatory():
    cfg = {}
    scparam(cfg, ['test'], sctype='str', shorthelp='Test', pernode='required')

    schema = Schema(cfg=cfg)

    # Should fail
    with pytest.raises(ValueError):
        schema.set('test', 'foo')

    # Should succeed
    assert schema.set('test', 'foo', step='syn', index=0)


def test_empty():
    schema = Schema()
    assert schema.is_empty('package', 'version')

    schema.set('package', 'version', '1.0')
    assert not schema.is_empty('package', 'version')


def test_add_keypath_error():
    schema = Schema()
    with pytest.raises(ValueError):
        schema.add('input', 'verilog', 'foo.v')


def test_pathlib():
    schema = Schema()

    file_path = pathlib.Path('path/to/file.txt')
    schema.set('option', 'file', 'test', file_path)
    assert schema.get('option', 'file', 'test') == [str(file_path)]

    dir_path = pathlib.Path('a/directory/')
    schema.set('option', 'dir', 'test', dir_path)
    assert schema.get('option', 'dir', 'test') == [str(dir_path)]


def test_allkeys():
    schema = Schema()

    assert len(schema.allkeys()) > 0

    partial = schema.allkeys('option')
    partial.sort()

    assert len(partial) > 0
    assert partial[0] == ('breakpoint',)

    complete = schema.allkeys('option', 'breakpoint')
    assert complete == []


def test_list_of_tuples():
    schema = Schema()
    keypath = ['flowgraph', 'asicflow', 'syn', '0', 'input']
    expected = [('import', '0')]

    schema.set(*keypath, ('import', '0'))
    assert schema.get(*keypath) == expected

    schema.set(*keypath, [['import', '0']])
    assert schema.get(*keypath) == expected

    # should be legal, since the list can be normalized to a tuple, and it's legal to set a scalar
    # for a list type
    schema.set(*keypath, ['import', '0'])
    assert schema.get(*keypath) == expected


def test_merge_with_init_old_has_values():
    old_schema = Schema().cfg

    scparam(old_schema, ['test'], sctype='[[str]]', shorthelp='Test')

    new_schema = Schema(cfg=old_schema)
    assert new_schema.getdict('test')

    new_schema._merge_with_init_schema()

    with pytest.raises(ValueError):
        new_schema.getdict('test')


def test_merge_with_init_new_has_values():
    old_schema = Schema().cfg

    del old_schema['package']

    new_schema = Schema(cfg=old_schema)
    with pytest.raises(ValueError):
        new_schema.getdict('package')

    new_schema._merge_with_init_schema()

    assert new_schema.getdict('package')


def test_merge_with_init_with_lib():
    chip = Chip('')
    chip.use(asic_demo)

    chip.schema._merge_with_init_schema()

    assert 'sky130hd' in chip.getkeys('library')


def test_copy_key_param():
    schema = Schema()

    schema.set('option', 'pdk', 'test')
    schema.set('option', 'pdk', 'test', field='help')

    assert schema.get('option', 'stackup', field='help') != 'test'

    schema.copy_key(src=('option', 'pdk'), dst=('option', 'stackup'))

    assert schema.get('option', 'stackup') == 'test'
    assert schema.get('option', 'stackup', field='help') == 'test'


def test_copy_key_file():
    chip = Chip('')

    os.makedirs("testingdir")
    chip.register_source('test', os.path.abspath("testingdir"))
    with open('testingdir/test.v', 'w') as f:
        f.write('test')

    file_path = os.path.join(os.path.abspath("testingdir"), "test.v")
    chip.set('option', 'file', 'test', 'test.v', package='test')
    assert chip.find_files('option', 'file', 'test') == [file_path]

    assert 'test1' not in chip.getkeys('option', 'file')
    chip.schema.copy_key(src=('option', 'file', 'test'), dst=('option', 'file', 'test1'))
    assert chip.find_files('option', 'file', 'test1') == [file_path]
