FOUR = 4

def forward_shift(matrix):
    transformed_matrix = []
    
    for i in range(len(matrix)):
        row = []
        for j in range(FOUR):
            shifted_i = shift(i, j)

            row.append(matrix[shifted_i][j])
        transformed_matrix.append(row)

    return transformed_matrix

def backward_shift(matrix):
    transformed_matrix = []
    
    for i in range(len(matrix)):
        row = []
        for j in range(FOUR):
            shifted_i = shift(i, -j)

            row.append(matrix[shifted_i][j])
        transformed_matrix.append(row)

    return transformed_matrix

def shift(val, diff):
    return ((val + diff) + FOUR) % FOUR




