from __future__ import annotations

import typing as typ

import numpy as np
if typ.TYPE_CHECKING:
    import numpy.typing as npt


def octave_read(path: str) -> npt.NDArray:
    with open(path, 'r') as f:
        data = [[float(f) for f in line.strip().split()]
                for line in f.readlines() if not line.startswith('#')]

    return np.asarray(data).squeeze()


def octave_write(path: str, data: npt.NDArray, name: str):
    if data.ndim == 1:
        data = data.view().reshape((1, len(data)))

    with open(path, 'w') as f:
        f.write('\n'.join([
                '# Created by refresh_matrices.py', f'# name: {name}',
                '# type: matrix', f'# rows: {data.shape[0]}',
                f'# columns: {data.shape[1]}'
        ]))
        f.write('\n')

        for ii in range(data.shape[0]):
            f.write(' '.join([str(fl) for fl in data[ii]]))
            if ii < data.shape[0] - 1:
                f.write('\n')
