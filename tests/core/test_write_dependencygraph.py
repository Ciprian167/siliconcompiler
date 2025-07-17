from siliconcompiler import Chip, Library
import pytest
import os


@pytest.mark.nostrict
def test_auto_enable_sublibrary_no_main(has_graphviz):
    chip = Chip('<test>')

    lib = Library('main_lib')
    sub_lib = Library('sub_lib', auto_enable=True)
    lib.use(sub_lib)

    chip.use(lib)

    chip.write_dependencygraph('dep.png')
    assert os.path.isfile('dep.png')


@pytest.mark.nostrict
def test_auto_enable_sublibrary_with_main(has_graphviz):
    chip = Chip('<test>')

    lib = Library('main_lib', auto_enable=True)
    sub_lib = Library('sub_lib', auto_enable=True)
    lib.use(sub_lib)

    chip.use(lib)

    chip.write_dependencygraph('dep.png')
    assert os.path.isfile('dep.png')


@pytest.mark.nostrict
def test_auto_enable(has_graphviz):
    chip = Chip('<test>')

    lib = Library('main_lib', auto_enable=True)
    chip.use(lib)

    chip.write_dependencygraph('dep.png')
    assert os.path.isfile('dep.png')


def test_recursive_import_lib_only(has_graphviz):
    chip = Chip('<test>')

    lib = Library('main_lib')
    sub_lib = Library('sub_lib')
    lib.use(sub_lib)

    chip.use(lib)

    chip.write_dependencygraph('dep.png')
    assert os.path.isfile('dep.png')
