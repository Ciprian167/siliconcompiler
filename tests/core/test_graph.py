import siliconcompiler

from siliconcompiler.tools.surelog import parse
from siliconcompiler.tools.yosys import syn_asic
from siliconcompiler.tools.openroad import init_floorplan
from siliconcompiler.tools.openroad import global_placement
from siliconcompiler.tools.openroad import clock_tree_synthesis
from siliconcompiler.tools.openroad import global_route
from siliconcompiler.tools.openroad import fillmetal_insertion
from siliconcompiler.tools.klayout import export

from siliconcompiler.tools.magic import extspice
from siliconcompiler.tools.magic import drc
from siliconcompiler.tools.netgen import lvs

from siliconcompiler.tools.builtin import nop
from siliconcompiler.tools.builtin import join
from siliconcompiler.tools.builtin import minimum

from core.tools.fake import fake_in
from core.tools.fake import fake_out

from siliconcompiler.flowgraph import _get_flowgraph_exit_nodes, \
    _get_flowgraph_entry_nodes, _get_flowgraph_nodes
from siliconcompiler.targets import freepdk45_demo


def test_graph():

    chip = siliconcompiler.Chip('test')

    # RTL
    rtl_flow = siliconcompiler.Flow('rtl')
    prevstep = None
    for step, task in [('import', parse),
                       ('syn', syn_asic),
                       ('export', nop)]:
        rtl_flow.node('rtl', step, task)
        if prevstep:
            rtl_flow.edge('rtl', prevstep, step)
        prevstep = step
    chip.use(rtl_flow)

    # APR
    apr_flow = siliconcompiler.Flow('apr')
    prevstep = None
    for step, task in [('import', nop),
                       ('floorplan', init_floorplan),
                       ('place', global_placement),
                       ('cts', clock_tree_synthesis),
                       ('route', global_route),
                       ('dfm', fillmetal_insertion),
                       ('export', export)]:
        apr_flow.node('apr', step, task)
        if prevstep:
            apr_flow.edge('apr', prevstep, step)
        prevstep = step
    chip.use(apr_flow)

    # SIGNOFF
    chip.node('signoff', 'import', nop)
    chip.node('signoff', 'extspice', extspice)
    chip.node('signoff', 'drc', drc)
    chip.node('signoff', 'lvs', lvs)
    chip.node('signoff', 'export', join)

    chip.edge('signoff', 'import', 'drc')
    chip.edge('signoff', 'import', 'extspice')
    chip.edge('signoff', 'extspice', 'lvs')
    chip.edge('signoff', 'lvs', 'export')
    chip.edge('signoff', 'drc', 'export')

    # TOP
    chip.graph("top", "rtl", name="rtl")
    chip.graph("top", "apr", name="apr")
    chip.graph("top", "signoff", name="dv")
    chip.edge("top", "rtl.export", "apr.import")
    chip.edge("top", "apr.export", "dv.import")

    chip.write_flowgraph("top.png", flow="top")


def test_graph_nodes():

    chip = siliconcompiler.Chip('foo')

    flow = 'test'
    chip.set('option', 'flow', flow)
    chip.node(flow, 'premin', fake_out, index=0)
    chip.node(flow, 'premin', fake_out, index=1)
    chip.node(flow, 'domin', minimum)
    chip.node(flow, 'postmin', fake_in)

    chip.edge(flow, 'premin', 'domin', tail_index=0)
    chip.edge(flow, 'premin', 'domin', tail_index=1)
    chip.edge(flow, 'domin', 'postmin')

    assert _get_flowgraph_nodes(chip, flow) == \
        [('premin', '0'), ('premin', '1'), ('domin', '0'), ('postmin', '0')]


def test_graph_entry():

    chip = siliconcompiler.Chip('foo')

    flow = 'test'
    chip.set('option', 'flow', flow)
    chip.node(flow, 'premin', fake_out, index=0)
    chip.node(flow, 'premin', fake_out, index=1)
    chip.node(flow, 'domin', minimum)
    chip.node(flow, 'postmin', fake_in)

    chip.edge(flow, 'premin', 'domin', tail_index=0)
    chip.edge(flow, 'premin', 'domin', tail_index=1)
    chip.edge(flow, 'domin', 'postmin')

    assert _get_flowgraph_entry_nodes(chip, flow) == [('premin', '0'), ('premin', '1')]


def test_graph_exit():

    chip = siliconcompiler.Chip('foo')
    chip.use(freepdk45_demo)

    flow = chip.get('option', 'flow')
    assert _get_flowgraph_exit_nodes(chip, flow) == [('write.gds', '0'), ('write.views', '0')]


def test_graph_exit_with_steps():

    chip = siliconcompiler.Chip('foo')
    chip.use(freepdk45_demo)

    steps = ['import', 'syn', 'floorplan.init']

    flow = chip.get('option', 'flow')
    assert _get_flowgraph_exit_nodes(chip, flow, steps=steps) == [('floorplan.init', '0')]


#########################
if __name__ == "__main__":
    test_graph()
