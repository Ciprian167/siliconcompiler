from siliconcompiler.tools._common import get_tool_task


def setup(chip):
    tool = 'echo'
    step = chip.get('arg', 'step')
    index = chip.get('arg', 'index')
    _, task = get_tool_task(chip, step, index)

    chip.set('tool', tool, 'exe', tool)
    chip.set('tool', tool, 'task', task, 'option', step + index,
             step=step, index=index, clobber=False)


def parse_version(stdout):
    '''
    Version check based on stdout
    Depends on tool reported string
    '''
    return '0'
