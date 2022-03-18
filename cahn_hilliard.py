import argparse
import os


parser = argparse.ArgumentParser(description='Solve a Cahn-Hillard problem')
parser.add_argument('--nx', dest='nx', type=int, default=100,
                    help='number of cells in x direction (default: 100)')
parser.add_argument('--ny', dest='ny', type=int, default=100,
                    help='number of cells in y direction (default: 100)')

args = parser.parse_args()


import fipy as fp

os.environ["FIPY_SOLVERS"] = "petsc"

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

dt = 1e2
for step in range(10):
    for sweep in range(5):
        res = eq.sweep(dt=dt)
