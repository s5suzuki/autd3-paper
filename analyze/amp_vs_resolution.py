'''
File: amp_vs_resolution.py
Project: python
Created Date: 04/06/2020
Author: Shun Suzuki
-----
Last Modified: 22/02/2021
Modified By: Shun Suzuki (suzuki@hapis.k.u-tokyo.ac.jp)
-----
Copyright (c) 2020 Hapis Lab. All rights reserved.

'''

import math
import matplotlib.pyplot as plt
import numpy as np
import os

from afc.python.afc import UniformSystem
from afc.python.afc import SphereWaveSource, T4010A1  # NOQA
from afc.python.afc import CpuCalculator, GpuCalculator, GridAreaBuilder, PressureFieldBuffer, PowerFieldBuffer  # NOQA
from afc.python.afc import Optimizer

from shared import setup_pyplot


def to_digital(system, digit):
    for source in system.get_wave_sources():
        phase = source.phase / (2.0 * math.pi)
        phase = (math.floor(phase * digit + 0.5) % digit) / digit
        source.phase = 2.0 * math.pi * phase


def plot():
    NUM_TRANS_X = 18 * 3
    NUM_TRANS_Y = 14 * 3
    TRANS_SIZE = 10.16
    FREQUENCY = 40e3
    TEMPERATURE = 287.6843037730883
    Z_DIR = np.array([0., 0., 1.])  # sound source direction
    R = 0
    Z = 500.0

    # array center
    focal_pos = np.array([TRANS_SIZE * (NUM_TRANS_X - 1) / 2, TRANS_SIZE * (NUM_TRANS_Y - 1) / 2, Z])

    # Observe properties, units are mm
    X_RANGE = (focal_pos[0] - R / 2, focal_pos[0] + R / 2)
    Y_RANGE = (focal_pos[1] - R / 2, focal_pos[1] + R / 2)
    RESOLUTION = 1.0

    # Initialize calculator
    calculator = CpuCalculator()

    # initialize position, direction, amplitude and phase of each sound source
    system = UniformSystem(TEMPERATURE)
    for y in range(NUM_TRANS_Y):
        for x in range(NUM_TRANS_X):
            pos = np.array([TRANS_SIZE * x, TRANS_SIZE * y, 0.])
            source = T4010A1(pos, Z_DIR, 1.0, 0.0, FREQUENCY)
            system.add_wave_source(source)

    system.info()
    system.info_of_source(0)

    # Generate observe area, units are mm
    observe_area = GridAreaBuilder()\
        .x_range(X_RANGE)\
        .y_range(Y_RANGE)\
        .z_at(Z)\
        .resolution(RESOLUTION)\
        .generate()

    # Generate target field buffer
    field = PressureFieldBuffer()

    N = 256
    results = np.zeros(N - 1)
    for i in range(2, N + 1):
        Optimizer.focus(system, focal_pos)
        to_digital(system, i)
        result = calculator.calculate(system, observe_area, field)
        results[i - 2] = result[0]

    results /= results[-1]

    fig = plt.figure(figsize=(6, 6), dpi=DPI)
    axes = fig.add_subplot()
    axes.plot(np.linspace(2, N, N - 1), results)
    plt.xticks([2, 16, 128, 256], ['2', '16', '128', '256'], fontname='Arial', fontsize=18)
    plt.yticks(fontname='Arial', fontsize=18)
    plt.hlines([1.0], 2, 256, 'gray', linestyles='dashed')

    inner = axes.inset_axes([0.3, 0.1, 0.6, 0.6])
    inner.plot(np.linspace(2, 32, 31), results[0:31])
    inner.set_xticks([2, 16, 32])
    inner.set_xticklabels(['2', '16', '32'])
    inner.hlines([1.0], 2, 32, 'gray', linestyles='dashed')

    # delete right up frame
    axes.spines['top'].set_visible(False)
    axes.spines['right'].set_visible(False)
    axes.get_xaxis().tick_bottom()
    axes.get_yaxis().tick_left()
    inner.spines['top'].set_visible(False)
    inner.spines['right'].set_visible(False)
    inner.get_xaxis().tick_bottom()
    inner.get_yaxis().tick_left()

    axes.set_xlim(0, 256)
    axes.set_ylim(0, 1.1)
    inner.set_xlim(0, 32)
    inner.set_ylim(0, 1.1)

    plt.ylabel('Normalized amplitude [-]', fontname='Arial', fontsize=24)
    plt.xlabel(r'Phase resolution $x\,(2\pi/x)$', fontname='Arial', fontsize=24)

    plt.tight_layout()
    plt.savefig(os.path.join('plot', 'amp_vs_resolution' + ext), bbox_inches='tight', pad_inches=0)


if __name__ == '__main__':
    os.makedirs('plot', exist_ok=True)
    setup_pyplot()

    DPI = 300
    ext = '.pdf'
    plot()
