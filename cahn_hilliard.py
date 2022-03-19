import argparse
import os
import time

start = time.time()

times = []

parser = argparse.ArgumentParser(description='Solve a Cahn-Hillard problem')
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
parser.add_argument('--output', dest='output', type=str, default="output.tsv",
                    help='file in which to append output statistics (default: "output.tsv")')

args = parser.parse_args()

os.environ["FIPY_SOLVERS"] = args.solver

import fipy as fp

mesh = fp.GmshGrid2D(nx=args.nx, ny=args.ny, dx=0.25, dy=0.25)
phi = fp.CellVariable(name=r"$\phi$", mesh=mesh)
psi = fp.CellVariable(name=r"$\psi$", mesh=mesh)

fp.tools.numerix.random.seed(12345)

noise = fp.GaussianNoiseVariable(mesh=mesh,
                                 mean=0.5,
                                 variance=0.01).value
phi[:] = noise

D = a = epsilon = 1.
dfdphi = a**2 * phi * (1 - phi) * (1 - 2 * phi)
dfdphi_ = a**2 * (1 - phi) * (1 - 2 * phi)
d2fdphi2 = a**2 * (1 - 6 * phi * (1 - phi))
eq1 = (fp.TransientTerm(var=phi) == fp.DiffusionTerm(coeff=D, var=psi))
eq2 = (fp.ImplicitSourceTerm(coeff=1., var=psi)
       == fp.ImplicitSourceTerm(coeff=d2fdphi2, var=phi) - d2fdphi2 * phi + dfdphi
       - fp.DiffusionTerm(coeff=epsilon**2, var=phi))
eq3 = (fp.ImplicitSourceTerm(coeff=1., var=psi)
       == fp.ImplicitSourceTerm(coeff=dfdphi_, var=phi)
       - fp.DiffusionTerm(coeff=epsilon**2, var=phi))
eq = eq1 & eq2

times.append(time.time() - start)

dt = 1e2
for step in range(args.steps):
    for sweep in range(args.sweeps):
        res = eq.sweep(dt=dt)
    times.append(time.time() - start)

if fp.parallel.procID == 0:
    # write headers if new file
    if not os.path.exists(args.output):
        with open(args.output, 'w') as f:
            headers = ["nproc", "nx", "ny", "steps", "sweeps", "solver"]
            headers += ["elapsed{}".format(n) for n in range(args.steps)]
            f.write("\t".join(headers) + "\n")

    # write run info
    with open(args.output, 'a') as f:
        stats = [fp.parallel.Nproc, args.nx, args.ny, args.steps, args.sweeps, args.solver]
        f.write("\t".join([str(v) for v in stats + times]) + "\n")
