'''
File: t4010a1.py
Project: directivity
Created Date: 02/12/2020
Author: Shun Suzuki
-----
Last Modified: 24/02/2021
Modified By: Shun Suzuki (suzuki@hapis.k.u-tokyo.ac.jp)
-----
Copyright (c) 2020 Hapis Lab. All rights reserved.

'''

import numpy as np
import matplotlib.pyplot as plt
import os
from shared import setup_pyplot


# sampled from the datasheet
A = [0, 1.0, 1.0, 1.0, 0.891250938, 0.707945784, 0.501187234, 0.354813389, 0.251188643, 0.199526231]
B = [0, 0, 0, -0.00459648054721, -0.0155520765675, -0.0208114779827, -0.0182211227016, -0.0122437497109, -0.00780345575475, -0.00312857467007]
C = [0, 0, 0, -0.000787968093807, -0.000307591508224, -0.000218348633296, 0.00047738416141, 0.000120353137658, 0.000323676257958, 0.000143850511]
D = [0, 0, 0, 1.60125528528e-05, 2.9747624976e-06, 2.31910931569e-05, -1.1901034125e-05, 6.77743734332e-06, -5.99548024824e-06, -4.79372835035e-06]


def directivity(theta):
    """
    third degree spline interpolation
    """

    theta = theta * 180.0 / np.pi
    theta = abs(theta)
    while theta > 90.0:
        theta = abs(180.0 - theta)

    i = int(np.ceil(theta / 10.0))

    d = 1.0
    if i != 0:
        a = A[i]
        b = B[i]
        c = C[i]
        d = D[i]
        x = theta - (i - 1) * 10.0
        d = a + b * x + c * x**2 + d * x**3

    return d


def plot():
    size = 1000

    x = np.linspace(-np.pi / 2, np.pi / 2, size)
    y = np.array(list(map(lambda x: 20 * np.log10(x), map(directivity, x))))

    fig = plt.figure(figsize=(6, 6), dpi=DPI)
    ax = fig.add_subplot(111, projection='polar', xlim=(-90, 90))
    ax.set_theta_direction(-1)
    ax.set_thetamin(-90)
    ax.set_thetamax(90)
    ax.set_theta_offset(.5 * np.pi)
    ax.set_thetagrids(range(-90, 120, 30))
    ax.xaxis.set_label_coords(0.5, 0.15)

    ax.set_ylim(-25, 5)
    ax.set_rgrids(np.linspace(-25, 5, 7),
                  labels=['', '-20', '', '-10', '', '0', ''],
                  fontsize=16)

    ax.plot(x, y)

    ax.set_xticklabels(['90°', '60°', '30°', '0°', '30°', '60°', '90°'], fontsize=16)
    ax.tick_params(axis='x', which='major', pad=10)
    ax.set_xlabel(r'Directivity $D(\theta)$\ [dB]', fontsize=18)

    plt.tight_layout()
    plt.savefig(os.path.join('plot', 't4010a1_dir' + ext))


if __name__ == '__main__':
    os.makedirs('plot', exist_ok=True)
    setup_pyplot()

    DPI = 300
    ext = '.pdf'
    plot()
