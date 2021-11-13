import numpy as np
from numpy import ndarray

from src.common.enums.FieldStatus import FieldStatus


class BoardStatus:
    _fields: ndarray

    def __init__(self, board_size):
        self._fields = np.full((board_size, board_size), FieldStatus.EMPTY_FIELD, dtype=FieldStatus)

    def indexes_in_range(self,x:int,y:int) ->bool:
        max_y, max_x = self._fields.shape
        return 0 <= x < max_x and 0 <= y < max_y

    def get_field(self, x: int, y: int) -> FieldStatus:
        if self.indexes_in_range(x, y):
            return self._fields[y, x]
        return None

    def set_field(self, x: int, y: int, field_status: FieldStatus):
        if self.indexes_in_range(x, y):
            self._fields[y, x] = field_status
