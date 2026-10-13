import time

import gurobipy as gp
from gurobipy import GRB


def solve_nqueens(n):
    if n < 1:
        raise ValueError("n must be >= 1")

    build_start = time.perf_counter()
    model = gp.Model("nqueens")
    model.Params.OutputFlag = 0

    # x[row, col] = 1 if a queen is placed at (row, col)
    x = model.addVars(n, n, vtype=GRB.BINARY, name="x")

    # Exactly one queen in each row
    for row in range(n):
        model.addConstr(
            gp.quicksum(x[row, col] for col in range(n)) == 1
        )

    # Exactly one queen in each column
    for col in range(n):
        model.addConstr(
            gp.quicksum(x[row, col] for row in range(n)) == 1
        )

    # At most one queen on each diagonal
    for row in range(n):
        for col in range(n):
            for other_row in range(row + 1, n):
                other_col = col + (other_row - row)
                if other_col < n:
                    model.addConstr(
                        x[row, col] + x[other_row, other_col] <= 1
                    )

                other_col = col - (other_row - row)
                if other_col >= 0:
                    model.addConstr(
                        x[row, col] + x[other_row, other_col] <= 1
                    )

    model.setObjective(0, GRB.MINIMIZE)

    build_time = time.perf_counter() - build_start
    solve_start = time.perf_counter()

    try:
        model.optimize()
    except gp.GurobiError as exc:
        solve_time = time.perf_counter() - solve_start
        error_message = str(exc)

        model.dispose()

        if "size-limited license" in error_message.lower():
            return {
                "n": n,
                "status": "LICENSE_LIMIT",
                "solution": None,
                "build_time_seconds": build_time,
                "solve_time_seconds": solve_time,
                "time_seconds": build_time + solve_time,
            }

        raise

    solve_time = time.perf_counter() - solve_start

    if model.Status == GRB.OPTIMAL:
        solution = [
            next(col for col in range(n) if x[row, col].X > 0.5)
            for row in range(n)
        ]
        status = "OPTIMAL"
    elif model.Status == GRB.INFEASIBLE:
        solution = None
        status = "INFEASIBLE"
    elif model.Status == GRB.INF_OR_UNBD:
        solution = None
        status = "INF_OR_UNBD"
    elif model.Status == GRB.UNBOUNDED:
        solution = None
        status = "UNBOUNDED"
    else:
        solution = None
        status = "NO_SOLUTION"

    model.dispose()

    return {
        "n": n,
        "status": status,
        "solution": solution,
        "build_time_seconds": build_time,
        "solve_time_seconds": solve_time,
        "time_seconds": build_time + solve_time,
    }


if __name__ == "__main__":
    for n in [1, 2, 3, 4, 8]:
        result = solve_nqueens(n)
        print(
            f"N={n:2d} | status={result['status']:10s} | "
            f"time={result['time_seconds']:.6f}s | "
            f"solution={result['solution']}"
        )
