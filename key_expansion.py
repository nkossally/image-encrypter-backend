from stable import S_BOX_INT

SIXTEEN = 16
FOUR = 4
EIGHT = 8

ROUND_CONSTANTS = [
    "01000000",
    "02000000",
    "04000000",
    "08000000",
    "10000000",
    "20000000",
    "40000000",
    "80000000",
    "1B000000",
    "36000000"
]

ROUND_CONSTANTS_INT = [1, 2, 4, 8, 16, 32, 64, 128, 27, 54]

text = "0123456789abcdeffedcba9876543210"


def handle_key_expansion_round_v2(matrix, round):
    last_bytes_arr = matrix[- 1]
    summand= g_function_v2(last_bytes_arr, round)

    transformed_matrix = []

    for row in matrix:
        new_row = [ row[i] ^ summand[i] for i in range(4)]
        summand = new_row
        transformed_matrix.append(new_row)

    return transformed_matrix

def g_function_v2(bytes_arr, round):

    new_bytes_arr = bytes_arr[1:] + bytes_arr[0 : 1]
    transformed_bytes = []

    for i in range(len(bytes_arr)):

        num = new_bytes_arr[i]

        binary_str = format(num, '08b')
        lookup_row = int(binary_str[0 : 4], 2)
        lookup_col = int(binary_str[4 :], 2)
        new_num = S_BOX_INT[lookup_row][lookup_col]

        transformed_bytes.append(new_num)
    
    first_byte = transformed_bytes[0]
    round_constant =  ROUND_CONSTANTS_INT[round]

    transformed_bytes[0] = first_byte ^ round_constant
    return transformed_bytes