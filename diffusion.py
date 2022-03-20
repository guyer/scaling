import argparse
import os
import time

start = time.time()

times = []

parser = argparse.ArgumentParser(description='Solve a diffusion problem')
parser.add_argument('--nx', dest='nx', type=int, default=100,
                    help='number of cells in x direction (default: 100)')
parser.add_argument('--ny', dest='ny', type=int, default=100,
                    help='number of cells in y direction (default: 100)')
parser.add_argument('--steps', dest='steps', type=int, default=10,
                    help='number of time steps (default: 10)')
parser.add_argument('--sweeps', dest='sweeps', type=int, default=5,
                    help='number of sweeps (default: 5)')
parser.add_argument('--solver', dest='solver', type=str, default="petsc",
                    help='solver suite (default: "petsc")')

args = parser.parse_args()

os.environ["FIPY_SOLVERS"] = args.solver

import fipy as fp

mesh = fp.GmshGrid2D(nx=args.nx, ny=args.ny)
phi = fp.CellVariable(name=r"$\phi$", mesh=mesh, value=0.)

fp.tools.numerix.random.seed(12345)

for seed in range(10):
    x0, y0, r0 = fp.tools.numerix.random.random(3)
    x0 *= args.nx
    y0 *= args.ny
    r0 *= args.nx / 4

    phi.setValue(1., where=(mesh.x - x0)**2 + (mesh.y - y0)**2 < r0**2)

viewer = fp.Viewer(vars=phi, datamin=0., datamax=1.)
viewer.plot()

D = 1.
eq = fp.TransientTerm(var=phi) == fp.DiffusionTerm(coeff=D, var=phi)

times.append(time.time() - start)

dt = 1.
for step in range(args.steps):
    for sweep in range(args.sweeps):
        res = eq.sweep(dt=dt)
    viewer.plot()
    times.append(time.time() - start)

print(args.nx, args.ny, args.steps, args.sweeps, args.solver, sep="\t", end="\t")
print("\t".join([str(t) for t in times]))
