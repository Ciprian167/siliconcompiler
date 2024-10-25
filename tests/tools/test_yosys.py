import siliconcompiler
import os
import pytest

from siliconcompiler.tools.yosys import lec

from siliconcompiler.tools.builtin import nop
from siliconcompiler.targets import freepdk45_demo


@pytest.mark.eda
@pytest.mark.quick
def test_yosys_lec(datadir):
    lec_dir = os.path.join(datadir, 'lec')

    chip = siliconcompiler.Chip('foo')
    chip.use(freepdk45_demo)

    flow = 'lec'
    chip.node(flow, 'import', nop)
    chip.node(flow, 'lec', lec)
    chip.edge(flow, 'import', 'lec')
    chip.set('option', 'flow', flow)

    chip.input(os.path.join(lec_dir, 'foo.v'))
    chip.input(os.path.join(lec_dir, 'foo.vg'))

    chip.run()

    errors = chip.get('metric', 'drvs', step='lec', index='0')

    assert errors == 0


@pytest.mark.eda
@pytest.mark.quick
def test_yosys_lec_broken(datadir):
    lec_dir = os.path.join(datadir, 'lec')

    chip = siliconcompiler.Chip('foo')
    chip.use(freepdk45_demo)

    flow = 'lec'
    chip.node(flow, 'import', nop)
    chip.node(flow, 'lec', lec)
    chip.edge(flow, 'import', 'lec')
    chip.set('option', 'flow', flow)

    chip.input(os.path.join(lec_dir, 'foo_broken.v'))
    chip.input(os.path.join(lec_dir, 'foo_broken.vg'))

    chip.run()

    errors = chip.get('metric', 'drvs', step='lec', index='0')

    assert errors == 2


@pytest.mark.eda
@pytest.mark.quick
@pytest.mark.parametrize("ext", ('v', 'vg'))
def test_screenshot(datadir, ext):
    lec_dir = os.path.join(datadir, 'lec')

    chip = siliconcompiler.Chip('foo')
    chip.use(freepdk45_demo)
    path = chip.show(os.path.join(lec_dir, f'foo_broken.{ext}'), screenshot=True)

    assert path
    assert os.path.exists(path)


if __name__ == "__main__":
    from tests.fixtures import datadir
    test_yosys_lec(datadir(__file__))
