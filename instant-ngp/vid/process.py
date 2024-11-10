import sys
pyngp_path = '../build'
sys.path.append(pyngp_path)
import pyngp as ngp
import numpy as np
from plyfile import PlyData, PlyElement

mode = ngp.TestbedMode.Nerf
testbed = ngp.Testbed(mode)
testbed.load_snapshot("../vid/base.msgpack")
mc = testbed.compute_marching_cubes_mesh()

vertex = np.array(list(zip(*mc["V"].T)), dtype=[('x', 'f4'), ('y', 'f4'), ('z', 'f4')])
vertex_color = np.array(list(zip(*((mc["C"] * 255).T))), dtype=[('red', 'u1'), ('green', 'u1'), ('blue', 'u1')])

n = len(vertex)
assert len(vertex_color) == n

vertex_all = np.empty(n, vertex.dtype.descr + vertex_color.dtype.descr)

for prop in vertex.dtype.names:
    vertex_all[prop] = vertex[prop]

for prop in vertex_color.dtype.names:
    vertex_all[prop] = vertex_color[prop]

ply = PlyData([PlyElement.describe(vertex_all, 'vertex')], text=False)

ply.write('nerf_pc.ply')