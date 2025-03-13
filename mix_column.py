import numpy as np
from utilities import convert_binary_string_matrix_to_int_matrix, xor_int_matrices

FOUR = 4
SIXTEEN = 16
EIGHT = 8

FORWARD_MATRIX = [
    [2, 3, 1, 1],
    [1, 2, 3, 1],
    [1, 1, 2, 3],
    [3, 1, 1, 2]
]

BACKWARD_MATRIX = [
    [14, 11, 13, 9],
    [9, 14, 11, 13],
    [13, 9, 14, 11],
    [11, 13, 9, 14]
]


POLYNOMIALS = [
    [0, 0, 0, 1, 1, 0, 1, 1],
    [0, 0, 1, 1, 0, 1, 1, 0],
    [0, 1, 1, 0, 1, 1, 0, 0],
    [1, 1, 0, 1, 1, 0, 0, 0],
]

# Function for multiplying two numbers in GF(2^8)
def gmul(a, b):
    p = 0
    for i in range(8):
        if (b & 1):
            p ^= a
        high_bit = a & 0x80
        a <<= 1
        if high_bit:
            a ^= 0x11B  # AES modulus
        b >>= 1
    return p

# The MixColumns constant matrix
mix_matrix = [
    [0x02, 0x03, 0x01, 0x01],
    [0x01, 0x02, 0x03, 0x01],
    [0x01, 0x01, 0x02, 0x03],
    [0x03, 0x01, 0x01, 0x02]
]

# The Inverse MixColumns constant matrix
inverse_mix_matrix = [
    [0x0E, 0x0B, 0x0D, 0x09],
    [0x09, 0x0E, 0x0B, 0x0D],
    [0x0D, 0x09, 0x0E, 0x0B],
    [0x0B, 0x0D, 0x09, 0x0E]
]

# MixColumns operation
def mix_columns(state):
    state = transpose_matrix(state)
    mixed_state = [[0] * 4 for _ in range(4)]
    
    for i in range(4):
        for j in range(4):
            mixed_state[j][i] = gmul(mix_matrix[j][0], state[0][i]) ^ gmul(mix_matrix[j][1], state[1][i]) ^ gmul(mix_matrix[j][2], state[2][i]) ^ gmul(mix_matrix[j][3], state[3][i])
    
    return transpose_matrix(mixed_state)

# Inverse MixColumns operation
def inverse_mix_columns(state):
    mixed_state = [[0] * 4 for _ in range(4)]
    state = transpose_matrix(state)
    
    for i in range(4):
        for j in range(4):
            mixed_state[j][i] = gmul(inverse_mix_matrix[j][0], state[0][i]) ^ gmul(inverse_mix_matrix[j][1], state[1][i]) ^ gmul(inverse_mix_matrix[j][2], state[2][i]) ^ gmul(inverse_mix_matrix[j][3], state[3][i])
    
    return transpose_matrix(mixed_state)


def transpose_matrix(matrix):
    new_matrix = [[] for _ in range(len(matrix))]
    for i in range(len(matrix)):
        for j in range(len(matrix[0])):
            new_matrix[i].append(matrix[j][i])
    return new_matrix