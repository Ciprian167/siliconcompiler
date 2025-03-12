#!/usr/bin/env python3

from siliconcompiler import Chip
from siliconcompiler.targets import freepdk45_demo

try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None


def main():
    # datawidths to check
    datawidths = [8, 16, 32, 64]

    # Gather Data
    area = []
    for n in datawidths:
        chip = Chip("oh_add")
        chip.register_source('oh',
                             'git+https://github.com/aolofsson/oh',
                             '23b26c4a938d4885a2a340967ae9f63c3c7a3527')
        chip.use(freepdk45_demo)
        chip.input('mathlib/hdl/oh_add.v', package='oh')
        chip.set('option', 'quiet', True)
        chip.set('option', 'to', ['syn'])
        chip.set('option', 'param', 'N', str(n))
        chip.run()

        area.append(chip.get('metric', 'cellarea', step='syn', index='0'))

    if plt:
        # Plot Data
        plt.subplots(1, 1)
        plt.plot(datawidths, area)
        plt.show()
    else:
        print('areas:', area)
        print('Install matplotlib to automatically plot this data!')
        return area


if __name__ == '__main__':
    main()
