'''
File: xy_field.py
Project: analyze
Created Date: 17/02/2021
Author: Shun Suzuki
-----
Last Modified: 24/02/2021
Modified By: Shun Suzuki (suzuki@hapis.k.u-tokyo.ac.jp)
-----
Copyright (c) 2021 Hapis Lab. All rights reserved.

'''

from shared import setup_pyplot, get_40kHz_amp, print_progress
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import mpl_toolkits.axes_grid1
import os
import glob
import re


def plot_acoustic_field_2d(axes, acoustic_pressures_2d, observe_x, observe_y, resolution, ticks_step, cmap='jet'):
    heatmap = axes.pcolor(acoustic_pressures_2d, cmap=cmap)
    x_label_num = int(math.floor((observe_x[1] - observe_x[0]) / ticks_step)) + 1
    y_label_num = int(math.floor((observe_y[1] - observe_y[0]) / ticks_step)) + 1
    x_labels = [observe_x[0] + ticks_step * i for i in range(x_label_num)]
    y_labels = [observe_y[0] + ticks_step * i for i in range(y_label_num)]
    x_ticks = [ticks_step / resolution * i for i in range(x_label_num)]
    y_ticks = [ticks_step / resolution * i for i in range(y_label_num)]
    axes.set_xticks(np.array(x_ticks) + 0.5, minor=False)
    axes.set_yticks(np.array(y_ticks) + 0.5, minor=False)
    axes.set_xticklabels(x_labels, minor=False)
    axes.set_yticklabels(y_labels, minor=False)

    return heatmap


def calc(data_path):
    cond = pd.read_csv(filepath_or_buffer=os.path.join(data_path, 'cond.txt'), sep=",", header=None)
    sample_rate = cond.at[0, 1]
    mV_per_Pa = cond.at[2, 1]
    dt = 1.0 / sample_rate

    p = re.compile(r'x([+-]?\d+\.?\d+?)y([+-]?\d+\.?\d+?)z([+-]?\d+\.?\d+?).csv')

    x_axis = []
    y_axis = []

    total = 0
    for filepath in glob.glob(os.path.join(data_path, '*')):
        m = p.match(filepath.split(os.path.sep)[-1])
        if m is None:
            continue

        x = float(m.group(1))
        y = float(m.group(2))

        x_axis.append(x)
        y_axis.append(y)
        total += 1

    x_axis = sorted(set(x_axis))
    y_axis = sorted(set(y_axis))

    rms = pd.DataFrame(index=y_axis, columns=x_axis)

    c = 0
    for filepath in glob.glob(os.path.join(data_path, '*')):
        m = p.match(filepath.split(os.path.sep)[-1])
        if m is None:
            continue

        x = float(m.group(1))
        y = float(m.group(2))

        df = pd.read_csv(filepath_or_buffer=filepath, sep=",")
        sound = df['  A Max [mV]']

        rms.at[y, x] = get_40kHz_amp(sound, dt) / mV_per_Pa / np.sqrt(2)
        c += 1
        print_progress(c, total)

    print()
    rms.to_csv('xy.csv')


def plot(plot_r):
    rms = pd.read_csv('xy.csv', index_col=0)
    resolution = float(rms.columns[1]) - float(rms.columns[0])

    nx = len(rms.columns)
    ny = len(rms.index)
    nx_min = int((nx - 1) / 2 - plot_r / resolution / 2)
    nx_max = int((nx - 1) / 2 + plot_r / resolution / 2) + 1
    ny_min = int((ny - 1) / 2 - plot_r / resolution / 2)
    ny_max = int((ny - 1) / 2 + plot_r / resolution / 2) + 1

    rms = rms.to_numpy().transpose().astype(np.float32)
    rms = rms[nx_min:nx_max, ny_min:ny_max]
    plot_xr = (-plot_r / 2, plot_r / 2)
    plot_yr = (-plot_r / 2, plot_r / 2)

    print('max [Pa]: ', rms.max())
    fig = plt.figure(figsize=(7, 6), dpi=DPI)
    axes = fig.add_subplot(111, aspect='equal')
    heat_map = plot_acoustic_field_2d(axes, rms, plot_xr, plot_yr, resolution, ticks_step=10.0)
    divider = mpl_toolkits.axes_grid1.make_axes_locatable(axes)
    plt.ylabel(r'$y\,[\mathrm{mm}]$', fontname='Arial', fontsize=18)
    plt.xlabel(r'$x\,[\mathrm{mm}]$', fontname='Arial', fontsize=18)
    cax = divider.append_axes('right', size='5%', pad='3%')
    cax.tick_params(labelsize=16)
    fig.colorbar(heat_map, cax=cax)
    cax.set_ylabel(r'$\mathrm{RMS\ of\ acoustic\ pressure}\,[\mathrm{Pa}]$', fontsize=18)

    plt.tight_layout()
    plt.savefig(os.path.join('plot', 'xy' + ext), bbox_inches='tight', pad_inches=0)


if __name__ == '__main__':
    os.makedirs('plot', exist_ok=True)
    setup_pyplot()

    DPI = 300
    ext = '.pdf'
    calc('./raw_data/xy')
    plot(80)
