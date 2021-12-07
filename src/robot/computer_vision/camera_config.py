board_size    = (24, 24)    # [cm]
gamearea_size = (40, 34)

pawns_colors_code = {
    # order means priority if two pawns are detected on the same field
    # white has highest priority, black lowest one
    'black': 3,
    'blue' : 2,
    'red'  : 4,
    'white': 1
}

pawns_code_colors = {
    1: 'white',
    2: 'blue',
    3: 'black',
    4: 'red'
}