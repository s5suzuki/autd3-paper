'''
File: pos_vs_resolution.py
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
import pandas as pd
import os

from afc.python.afc import UniformSystem
from afc.python.afc import SphereWaveSource, T4010A1  # NOQA
from afc.python.afc import CpuCalculator, GpuCalculator, GridAreaBuilder, PressureFieldBuffer, PowerFieldBuffer  # NOQA
from afc.python.afc import Optimizer

from shared import setup_pyplot, print_progress

RESOLUTION = 0.1


def to_digital(system, digit):
    for source in system.get_wave_sources():
        phase = source.phase / (2.0 * math.pi)
        phase = (math.floor(phase * digit + 0.5) % digit) / digit
        source.phase = 2.0 * math.pi * phase


def calc():
    NUM_TRANS_X = 18 * 3
    NUM_TRANS_Y = 14 * 3
    TRANS_SIZE = 10.16
    FREQUENCY = 40e3
    TEMPERATURE = 287.6843037730883
    Z_DIR = np.array([0., 0., 1.])  # sound source direction
    R = 8.5
    Z = 500.0

    array_center = np.array([TRANS_SIZE * (NUM_TRANS_X - 1) / 2, TRANS_SIZE * (NUM_TRANS_Y - 1) / 2, Z])

    # Observe properties, units are mm
    X_RANGE = (array_center[0], array_center[0] + 2 * R)

    # Initialize calculator
    calculator = CpuCalculator()

    # initialize position, direction, amplitude and phase of each sound source
    system = UniformSystem(TEMPERATURE)
    for y in range(NUM_TRANS_Y):
        for x in range(NUM_TRANS_X):
            pos = np.array([TRANS_SIZE * x, TRANS_SIZE * y, 0.])
            source = T4010A1(pos, Z_DIR, 1.0, 0.0, FREQUENCY)
            system.add_wave_source(source)

    # Generate observe area, units are mm
    observe_area = GridAreaBuilder()\
        .x_range(X_RANGE)\
        .y_at(array_center[1])\
        .z_at(Z)\
        .resolution(RESOLUTION)\
        .generate()
    field = PressureFieldBuffer()

    foci_x = np.array([x * RESOLUTION for x in range(85 + 1)])
    phase_div = range(2, 256)
    df = pd.DataFrame(columns=['x'].extend(phase_div))
    df['x'] = foci_x
    c = 0
    total = len(foci_x) * len(phase_div)
    for i in phase_div:
        N = 85 + 1
        results = np.zeros(N)
        d = 0
        for focus_x in foci_x:
            focal_pos = array_center + np.array([focus_x, 0, 0])
            Optimizer.focus(system, focal_pos)
            to_digital(system, i)

            result = calculator.calculate(system, observe_area, field)
            max_index = np.argmax(result)
            results[d] = max_index
            d += 1
            c += 1
            print_progress(c, total)

        df[i] = results

    df.to_csv('pos_vs_argmax.csv')


def plot():
    df = pd.read_csv('pos_vs_argmax.csv')
    results = np.zeros(255)  # 2 - 256
    results_max = np.zeros(255)  # 2 - 256
    for i in df.columns[2:]:
        diff_mean = 0
        diff_max = 0
        for (focus_x, argmax_x) in zip(df['x'], df[i]):
            max_x = argmax_x * RESOLUTION
            diff = abs(max_x - focus_x)
            diff_mean += diff
            diff_max = max(diff_max, diff)
        diff_mean /= len(df['x'])

        i = int(i)
        results[i - 2] = diff_mean
        results_max[i - 2] = diff_max

    setup_pyplot()
    DPI = 300
    fig = plt.figure(figsize=(6, 6), dpi=DPI)

    axes = fig.add_subplot()
    axes.plot(np.linspace(2, 256, 255), results)
    plt.xticks([2, 16, 128, 256], ['2', '16', '128', '256'], fontname='Arial', fontsize=18)
    plt.yticks(fontname='Arial', fontsize=18)
    plt.fill_between(np.linspace(2, 256, 255), 0, results_max, facecolor='y', alpha=0.5)

    inner = axes.inset_axes([0.3, 0.1, 0.6, 0.6])
    inner.plot(np.linspace(2, 32, 31), results[0:31])
    inner.set_xticks([2, 16, 32])
    inner.set_xticklabels(['2', '16', '32'])
    inner.fill_between(np.linspace(2, 32, 31), 0, results_max[0:31], facecolor='y', alpha=0.5)

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
    axes.set_ylim(0, 0.4)
    inner.set_xlim(0, 32)
    inner.set_ylim(0, 0.4)

    plt.ylabel('Focus position deviation [mm]', fontname='Arial', fontsize=24)
    plt.xlabel(r'Phase resolution $x\,(2\pi/x)$', fontname='Arial', fontsize=24)

    plt.tight_layout()
    plt.savefig(os.path.join('plot', 'pos_vs_resolution' + ext), bbox_inches='tight', pad_inches=0)


if __name__ == '__main__':
    os.makedirs('plot', exist_ok=True)
    setup_pyplot()

    DPI = 300
    ext = '.pdf'
    calc()
    plot()
