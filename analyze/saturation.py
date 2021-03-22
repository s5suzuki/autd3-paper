'''
File: saturation.py
Project: analyze
Created Date: 19/02/2021
Author: Shun Suzuki
-----
Last Modified: 26/02/2021
Modified By: Shun Suzuki (suzuki@hapis.k.u-tokyo.ac.jp)
-----
Copyright (c) 2021 Hapis Lab. All rights reserved.

'''


import glob
import re
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from shared import setup_pyplot, get_40kHz_amp, print_progress


def get_amp_data(data_path):
    p = re.compile(r'duty(\d+).csv')

    cond = pd.read_csv(filepath_or_buffer=os.path.join(data_path, 'cond.txt'), sep=",", header=None)
    sample_rate = cond.at[0, 1]
    mV_per_Pa = cond.at[2, 1]
    dt = 1.0 / sample_rate

    duties = []
    total = 0
    for filepath in glob.glob(os.path.join(data_path, '*')):
        m = p.match(filepath.split(os.path.sep)[-1])
        if m is None:
            continue

        duty = int(m.group(1))
        duties.append(duty)
        total += 1

    duties = np.array(sorted(duties))
    results_sound = pd.DataFrame(index=duties, columns=['rms'])
    c = 0
    for filepath in glob.glob(os.path.join(data_path, '*')):
        m = p.match(filepath.split(os.path.sep)[-1])
        if m is None:
            continue

        df = pd.read_csv(filepath_or_buffer=filepath, sep=",")
        sound = df['  A Max [mV]']

        duty = int(m.group(1))
        results_sound.at[duty, 'rms'] = get_40kHz_amp(sound, dt) / mV_per_Pa / np.sqrt(2)
        c += 1
        print_progress(c, total)

    print()

    return results_sound


def get_calib_ratio(data, data_covered):
    ratio = 0.0
    fit_range = range(10, 25, 1)
    for i in fit_range:
        ratio += data.at[i, 'rms'] / data_covered.at[i, 'rms']
    ratio /= len(fit_range)
    return ratio


def sin_fit(v, r, a):
    res = (r * np.sin(v)) ** a
    return res


def duty(satiration_path, plot_z):
    fig = plt.figure(figsize=(8, 8), dpi=DPI)
    ax = fig.add_subplot(111)

    p = re.compile(r'saturation_cover_(\d)x(\d)_z(\d+)')

    for_plots = []
    for folder_path in glob.glob(os.path.join(satiration_path, '*')):
        folder_name = folder_path.split(os.path.sep)[-1]
        m = p.match(folder_name)
        if m is None:
            continue

        cond = pd.read_csv(filepath_or_buffer=os.path.join(folder_path, 'cond.txt'), sep=",", header=None)
        z = int(float(cond.at[8, 1]))
        if z != plot_z:
            continue

        d1 = int(m.group(1))
        d2 = int(m.group(2))

        for_plots.append((d1, d2, z, folder_path))

    for_plots = sorted(for_plots, key=lambda x: x[0] * x[1], reverse=True)

    max_pa = 0
    mc = 0
    markers = ['o', '^', 'v']
    for d1, d2, z, folder_path in for_plots:
        data = get_amp_data(folder_path.replace('saturation_cover_', 'saturation_'))
        data_covered = get_amp_data(folder_path)

        ratio = get_calib_ratio(data, data_covered)

        max_pa = max(ratio * data_covered['rms'].max(), max_pa)

        label = fr'${d1}\times {d2}\,$ modules' if (d1 * d2) != 1 else '1 module'
        ax.plot(data_covered.index, ratio * data_covered['rms'],
                marker=markers[mc], markersize=4, linestyle='None', label=label)
        mc += 1

    plt.ylabel('RMS of acoustic pressure [Pa]', fontname='Arial', fontsize=24)
    plt.xlabel(r'Duty ratio $D$ [-]', fontname='Arial', fontsize=24)
    plt.xticks([0, 127, 255], ['0', '127', '255'], fontname='Arial', fontsize=20)
    plt.yticks(fontname='Arial', fontsize=20)
    plt.legend(bbox_to_anchor=(-0.05, 1), loc='upper left', borderaxespad=1, fontsize=20, frameon=False, markerscale=2)

    # delete right up frame
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.get_xaxis().tick_bottom()
    ax.get_yaxis().tick_left()

    ax.set_xlim(0, 255)
    ax.set_ylim(0, np.floor(max_pa // 1000) * 1000 + 1000)

    plt.tight_layout()
    plt.savefig(os.path.join('plot', f'saturation_z{plot_z}' + ext), bbox_inches='tight', pad_inches=0)


if __name__ == '__main__':
    os.makedirs('plot', exist_ok=True)
    setup_pyplot()

    DPI = 300
    ext = '.pdf'
    duty('./raw_data/saturation', 150, False)
    duty('./raw_data/saturation', 300, False)
    duty('./raw_data/saturation', 500, False)
