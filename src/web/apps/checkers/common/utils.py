import numpy as np


# map 2d array 8x8 of field statuses to string with length 32 (only playable fields)
def map_board_to_playable_fields_str(board: np.ndarray):
    if not isinstance(board, np.ndarray) or board.shape != (8, 8):
        return None

    str_board_status = ""
    for y in range(8):
        for x in range(8):
            if (x + y) % 2 != 0:
                str_board_status += str(board[x, y])
    return str_board_status
