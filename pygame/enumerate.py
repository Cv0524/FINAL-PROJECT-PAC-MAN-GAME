maze_layout = [
    "################",
    "#..............#",
    "#.####..####...#",
    "................",
    "....#.#..#.#..#.",
    "#.###.####.####.",
    "#...#......#....#",
    "#...#.#.#..#..#.",
    "#.#####.####..#.",
    "#...............",
    "#.####..####...#",
    "................",
    "....#.#..#.#..#.",
    "#.#.#.####.####.",
    "#...#......#....#",
    "#################"
]


cell = [] 

for index, symbol in enumerate(maze_layout):
    #print(f"index number: {index} symbol row: {symbol}")
    for index_cell, cell_item in enumerate(symbol):
        print(f"index cell: {index_cell} cell item: {cell_item}")


