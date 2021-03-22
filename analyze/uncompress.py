'''
File: uncompress.py
Project: analyze
Created Date: 17/02/2021
Author: Shun Suzuki
-----
Last Modified: 21/02/2021
Modified By: Shun Suzuki (suzuki@hapis.k.u-tokyo.ac.jp)
-----
Copyright (c) 2021 Hapis Lab. All rights reserved.

'''

import zipfile
import os


def uncompress(src_path, dst_path):
    with zipfile.ZipFile(src_path) as f:
        f.extractall(dst_path)


if __name__ == '__main__':
    os.makedirs('raw_data', exist_ok=True)
    data_path = '../data/data.zip'
    if os.path.isfile(data_path):
        uncompress(data_path, 'raw_data')
    else:
        dst_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
        dst_path = os.path.normpath(dst_path)
        print(f'Please download zipped data file from https://osf.io/sqdg4/ and place it in {dst_path} folder.')
