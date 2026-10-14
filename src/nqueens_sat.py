from itertools import combinations
from time import perf_counter

from pysat.card import CardEnc, EncType
from pysat.solvers import Solver


def var(i, j, n):
    """Map cell (i, j) to a positive SAT variable ID."""
    return i * n + j + 1



def commander_amo(variables, next_var, group_size=3):
    """Encode at-most-one using a recursive Commander encoding.

    Returns (clauses, next_var), where next_var is the next unused
    auxiliary variable ID.
    """
    if len(variables) <= 1:
        return [], next_var

    if len(variables) <= group_size:
        return [
            [-variables[i], -variables[j]]
            for i in range(len(variables))
            for j in range(i + 1, len(variables))
        ], next_var

    clauses = []
    commanders = []

    for start in range(0, len(variables), group_size):
        group = variables[start:start + group_size]
        commander = next_var
        next_var += 1
        commanders.append(commander)

        # At most one original variable in this group.
        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                clauses.append([-group[i], -group[j]])

        # If an original variable is true, its commander must be true.
        for variable in group:
            clauses.append([-variable, commander])

        # A true commander implies at least one variable in its group.
        clauses.append([-commander] + group)

    # At most one commander can be true.
    subclauses, next_var = commander_amo(
        commanders, next_var, group_size
    )
    clauses.extend(subclauses)

    return clauses, next_var



def product_amo(variables, next_var):
    """Encode at-most-one using a row-column Product encoding."""
    n = len(variables)

    if n <= 1:
        return [], next_var

    # Arrange variables in a roughly square grid.
    num_rows = int(n ** 0.5)
    if num_rows * num_rows < n:
        num_rows += 1
    num_cols = (n + num_rows - 1) // num_rows

    row_selectors = list(
        range(next_var, next_var + num_rows)
    )
    next_var += num_rows

    col_selectors = list(
        range(next_var, next_var + num_cols)
    )
    next_var += num_cols

    clauses = []

    # Each original variable implies its row and column selectors.
    for index, variable in enumerate(variables):
        row = index // num_cols
        col = index % num_cols

        clauses.append([-variable, row_selectors[row]])
        clauses.append([-variable, col_selectors[col]])

    # At most one row selector can be true.
    for i in range(num_rows):
        for j in range(i + 1, num_rows):
            clauses.append([
                -row_selectors[i],
                -row_selectors[j],
            ])

    # At most one column selector can be true.
    for i in range(num_cols):
        for j in range(i + 1, num_cols):
            clauses.append([
                -col_selectors[i],
                -col_selectors[j],
            ])

    return clauses, next_var




def build_cnf(n, encoding="pairwise"):
    """Build the CNF formula using the selected AMO encoding."""
    if n < 1:
        raise ValueError("N must be at least 1")

    encodings = {
        "pairwise": EncType.pairwise,
        "seqcounter": EncType.seqcounter,
        "commander": None,
        "product": None,
    }

    if encoding not in encodings:
        raise ValueError(
            f"Unsupported encoding: {encoding}. "
            f"Choose from {list(encodings)}"
        )

    start = perf_counter()
    clauses = []
    next_var = n * n + 1

    def add_at_most_one(variables):
        nonlocal next_var

        if encoding == "commander":
            amo_clauses, next_var = commander_amo(
                variables, next_var
            )
        elif encoding == "product":
            amo_clauses, next_var = product_amo(
                variables, next_var
            )
        else:
            amo = CardEnc.atmost(
                lits=variables,
                bound=1,
                top_id=next_var - 1,
                encoding=encodings[encoding],
            )
            amo_clauses = amo.clauses
            next_var = max(next_var, amo.nv + 1)

        clauses.extend(amo_clauses)

    def add_exactly_one(variables):
        # At least one (ALO).
        clauses.append(list(variables))

        # At most one (AMO).
        add_at_most_one(variables)

    # Exactly one queen in each row.
    for i in range(n):
        add_exactly_one([var(i, j, n) for j in range(n)])

    # Exactly one queen in each column.
    for j in range(n):
        add_exactly_one([var(i, j, n) for i in range(n)])

    # At most one queen on each diagonal.
    diagonals = {}

    for i in range(n):
        for j in range(n):
            diagonals.setdefault(
                ("diff", i - j), []
            ).append(var(i, j, n))
            diagonals.setdefault(
                ("sum", i + j), []
            ).append(var(i, j, n))

    for cells in diagonals.values():
        add_at_most_one(cells)

    build_time = perf_counter() - start
    return clauses, build_time



def validate_board(board):
    """Independently validate a board."""
    if board is None:
        return False

    n = len(board)

    if any(len(row) != n for row in board):
        return False

    if any(sum(row) != 1 for row in board):
        return False

    if any(sum(board[i][j] for i in range(n)) != 1 for j in range(n)):
        return False

    queens = [
        (i, j)
        for i in range(n)
        for j in range(n)
        if board[i][j] == 1
    ]

    for (i, j), (k, l) in combinations(queens, 2):
        if abs(i - k) == abs(j - l):
            return False

    return True


def solve_nqueens(n):
    clauses, build_time = build_cnf(n)
    solve_start = perf_counter()

    with Solver(name="g4", bootstrap_with=clauses) as solver:
        is_sat = solver.solve()
        solve_time = perf_counter() - solve_start

        num_variables = solver.nof_vars()

        if not is_sat:
            board = None
        else:
            model = {
                lit for lit in solver.get_model()
                if lit > 0
            }

            board = [
                [
                    int(var(i, j, n) in model)
                    for j in range(n)
                ]
                for i in range(n)
            ]

    return {
        "n": n,
        "status": "SAT" if board is not None else "UNSAT",
        "valid": validate_board(board),
        "variables": num_variables,
        "clauses": len(clauses),
        "build_time": build_time,
        "solve_time": solve_time,
        "total_time": build_time + solve_time,
        "board": board,
    }


def main():
    test_sizes = [1, 2, 3, 4, 8, 16]

    print(
        f"{'N':>3} | {'Status':>5} | {'Valid':>5} | "
        f"{'Vars':>5} | {'Clauses':>7} | "
        f"{'Build(s)':>10} | {'Solve(s)':>10} | {'Total(s)':>10}"
    )
    print("-" * 85)

    for n in test_sizes:
        result = solve_nqueens(n)

        print(
            f"{n:3} | {result['status']:>5} | "
            f"{str(result['valid']):>5} | "
            f"{result['variables']:5} | "
            f"{result['clauses']:7} | "
            f"{result['build_time']:10.6f} | "
            f"{result['solve_time']:10.6f} | "
            f"{result['total_time']:10.6f}"
        )


if __name__ == "__main__":
    main()