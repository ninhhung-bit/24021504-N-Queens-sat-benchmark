from time import perf_counter

from docplex.cp.model import CpoModel


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
    model = CpoModel()

    # queen[row] là cột đặt hậu tại hàng row
    queen = [
        model.integer_var(min=0, max=n - 1, name=f"queen_{row}")
        for row in range(n)
    ]

    # Mỗi cột chỉ có một quân hậu
    model.add(model.all_diff(queen))

    # Không có hai quân hậu cùng đường chéo
    for row1 in range(n):
        for row2 in range(row1 + 1, n):
            model.add(
                queen[row1] - queen[row2] != row1 - row2
            )
            model.add(
                queen[row1] - queen[row2] != row2 - row1
            )

    start = perf_counter()
    solution = model.solve(TimeLimit=30, LogVerbosity="Quiet")
    solve_time = perf_counter() - start

    if solution is not None:
        board = [solution.get_value(variable) for variable in queen]
        valid = validate_board(board)
        status = "FEASIBLE" if valid else "INVALID"
    else:
        board = None
        valid = False
        status = "NO_SOLUTION"


    return {
        "n": n,
        "status": status,
        "valid": valid,
        "solve_time": solve_time,
        "board": board,
    }


if __name__ == "__main__":
    for n in [1, 2, 3, 4, 8, 16, 32, 64]:
        result = solve_nqueens(n)

        print(
            f"N={result['n']:2} | "
            f"status={result['status']:12} | "
            f"valid={result['valid']} | "
            f"solve_time={result['solve_time']:.6f}s"
        )