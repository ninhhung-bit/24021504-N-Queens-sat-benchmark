from docplex.mp.utils import DOcplexLimitsExceeded
from time import perf_counter

from docplex.mp.model import Model


def validate_board(board):
    if board is None:
        return False

    n = len(board)

    if len(set(board)) != n:
        return False

    for row1 in range(n):
        for row2 in range(row1 + 1, n):
            if abs(board[row1] - board[row2]) == abs(row1 - row2):
                return False

    return True


def solve_nqueens(n):
    model = Model(name=f"nqueens_mip_{n}")

    # x[row, col] = 1 nếu đặt hậu tại ô đó
    x = {
        (row, col): model.binary_var(name=f"x_{row}_{col}")
        for row in range(n)
        for col in range(n)
    }

    # Mỗi hàng có đúng một quân hậu
    for row in range(n):
        model.add_constraint(
            model.sum(x[row, col] for col in range(n)) == 1
        )

    # Mỗi cột có đúng một quân hậu
    for col in range(n):
        model.add_constraint(
            model.sum(x[row, col] for row in range(n)) == 1
        )

    # Mỗi đường chéo có tối đa một quân hậu
    for row in range(n):
        for col in range(n):
            for other_row in range(row + 1, n):
                other_col = col + (other_row - row)
                if other_col < n:
                    model.add_constraint(
                        x[row, col] + x[other_row, other_col] <= 1
                    )

                other_col = col - (other_row - row)
                if other_col >= 0:
                    model.add_constraint(
                        x[row, col] + x[other_row, other_col] <= 1
                    )

    model.minimize(0)

    print(
        f"Model N={n}: "
        f"variables={model.number_of_variables}, "
        f"constraints={model.number_of_constraints}"
    )

    start = perf_counter()

    try:
        solution = model.solve(log_output=False)
        status = "FEASIBLE" if solution is not None else "NO_SOLUTION"
    except DOcplexLimitsExceeded:
        solution = None
        status = "LIMIT_EXCEEDED"

    solve_time = perf_counter() - start

    if status == "LIMIT_EXCEEDED":
        board = None
        valid = False
    elif solution is not None:
        board = []
        for row in range(n):
            queen_col = next(
                col for col in range(n)
                if solution.get_value(x[row, col]) > 0.5
            )
            board.append(queen_col)

        valid = validate_board(board)
        status = "FEASIBLE" if valid else "INVALID"
    else:
        board = None
        valid = False
        status = "NO_SOLUTION"

    model.end()

    return {
        "n": n,
        "status": status,
        "valid": valid,
        "solve_time": solve_time,
        "board": board,
    }


if __name__ == "__main__":
    for n in [9, 10, 11, 12]:
        result = solve_nqueens(n)

        print(
            f"N={result['n']:2} | "
            f"status={result['status']:12} | "
            f"valid={result['valid']} | "
            f"solve_time={result['solve_time']:.6f}s"
        )