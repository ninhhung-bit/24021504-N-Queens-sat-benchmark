
from src.nqueens_sat import build_cnf
from pysat.solvers import Solver

encodings = [
    "pairwise",
    "seqcounter",
    "commander",
    "product",
]

for encoding in encodings:
    print(f"\nTesting {encoding}:")

    for n in [1, 2, 3, 4, 8]:
        clauses, _ = build_cnf(n, encoding)

        with Solver(
            name="g4",
            bootstrap_with=clauses
        ) as solver:
            is_sat = solver.solve()

        expected = n not in [2, 3]

        print(
            f"  N={n}, SAT={is_sat}, "
            f"expected={expected}, "
            f"PASS={is_sat == expected}"
        )

        assert is_sat == expected, (
            f"Failed: encoding={encoding}, N={n}"
        )

print("\nAll encoding tests passed.")
