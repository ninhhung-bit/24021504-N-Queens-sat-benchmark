
from src.nqueens_sat import build_cnf
from pysat.solvers import Solver

for n in [1, 2, 3, 4, 8]:
    clauses, _ = build_cnf(n, "seqcounter")

    with Solver(name="g4", bootstrap_with=clauses) as solver:
        is_sat = solver.solve()

    print(f"N={n}, SAT={is_sat}")
