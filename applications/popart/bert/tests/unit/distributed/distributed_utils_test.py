# Copyright (c) 2021 Graphcore Ltd. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import subprocess
from collections import deque
from pathlib import Path
import popart
import numpy as np
from utils.distributed import setup_comm, average_distributed_deques


def test_average_distributed_deques():
    subprocess.run(f"mpirun -np 2 python {Path(__file__).absolute()}", check=True, shell=True)


def gather_and_check():
    from mpi4py import MPI
    comm = MPI.COMM_WORLD
    setup_comm(comm)
    size = comm.Get_size()
    rank = comm.Get_rank()

    data = np.array([1.5, 2.5, 3.5]) + 3*rank
    stats = deque(data, maxlen=4)

    N = 2
    gathered = average_distributed_deques(data, N=N)
    if rank == 0:
        mock = np.empty([size, N])
        for i in range(size):
            mock[i] = np.array([2.5, 3.5]) + 3*i
        mock_reduced = np.average(mock, axis=0)
        gathered = np.array(gathered)
        assert np.all(mock_reduced == gathered[3-N:])


if __name__ == "__main__":
    gather_and_check()
