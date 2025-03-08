from utilities import xor, xor_binary_arrays, xor_int_arrays, hex_to_eight_bit_binary_string, hex_to_four_bit_binary_string, convert_binary_matrix_to_hex_matrix, convert_binary_arr_to_hex_arr
from stable import transformation_v2, S_BOX, S_BOX_INT, forward_substitution_v2

SIXTEEN = 16
FOUR = 4
EIGHT = 8

S_BOX_INT = [[99, 124, 119, 123, 242, 107, 111, 197, 48, 1, 103, 43, 254, 215, 171, 118], [202, 130, 201, 125, 250, 89, 71, 240, 173, 212, 162, 175, 156, 164, 114, 192], [183, 253, 147, 38, 54, 63, 247, 204, 52, 165, 229, 241, 113, 216, 49, 21], [4, 199, 35, 195, 24, 150, 5, 154, 7, 18, 128, 226, 235, 39, 178, 117], [9, 131, 44, 26, 27, 110, 90, 160, 82, 59, 214, 179, 41, 227, 47, 132], [83, 209, 0, 237, 32, 252, 177, 91, 106, 203, 190, 57, 74, 76, 88, 207], [208, 239, 170, 251, 67, 77, 51, 133, 69, 249, 2, 127, 80, 60, 159, 168], [81, 163, 64, 143, 146, 157, 56, 245, 188, 182, 218, 33, 16, 255, 243, 210], [205, 12, 19, 236, 95, 151, 68, 23, 196, 167, 126, 61, 100, 93, 25, 115], [96, 129, 79, 220, 34, 42, 144, 136, 70, 238, 184, 20, 222, 94, 11, 219], [224, 50, 58, 10, 73, 6, 36, 92, 194, 211, 172, 98, 145, 149, 228, 121], [231, 200, 55, 109, 141, 213, 78, 169, 108, 86, 244, 234, 101, 122, 174, 8], [186, 120, 37, 46, 28, 166, 180, 198, 232, 221, 116, 31, 75, 189, 139, 138], [112, 62, 181, 102, 72, 3, 246, 14, 97, 53, 87, 185, 134, 193, 29, 158], [225, 248, 152, 17, 105, 217, 142, 148, 155, 30, 135, 233, 206, 85, 40, 223], [140, 161, 137, 13, 191, 230, 66, 104, 65, 153, 45, 15, 176, 84, 187, 22]]

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

def handle_key_expansion(key):
    bytes_arr = convert_32_char_hex_text_to_binary_matrix(key)
    # bytes_arr = convert_binary_key_to_arr(key)

    for i in range(10):
        bytes_arr = handle_key_expansion_round(bytes_arr, i)

    return bytes_arr

def convert_binary_key_to_arr(key):
    bytes_arr = []
    for i in range(FOUR):
        row = []
        for j in range(FOUR):
            start_idx = EIGHT * i + EIGHT * FOUR * j
            bytes = key[start_idx: start_idx + EIGHT]
            row.append(bytes)
        bytes_arr.append(row)

    return bytes_arr

def convert_32_char_hex_text_to_binary_matrix(key):
    bytes_arr = []
    for i in range(FOUR):
        row = []
        for j in range(FOUR):
            # start_idx = 2 * i + EIGHT * j
            start_idx = (i * EIGHT + j * 2)
            byte_1 = hex_to_four_bit_binary_string(key[start_idx])
            byte_2 = hex_to_four_bit_binary_string(key[start_idx + 1])
            row.append(byte_1 + byte_2)
        bytes_arr.append(row)

    # hex_arr = convert_binary_matrix_to_hex_matrix(bytes_arr)

    return bytes_arr

def handle_key_expansion_round(matrix, round):
    transformed_matrix = []
    last_bytes_arr = matrix[- 1]
    summand = g_function(last_bytes_arr, round)

    for row in matrix:
        new_row = []
        for j in range(len(row)):

            new_row.append(xor(row[j], summand[j]))
        summand = new_row
        transformed_matrix.append(new_row)

    return transformed_matrix

def g_function(bytes_arr, round):

    new_bytes_arr = bytes_arr[1:] + bytes_arr[0 : 1]
    transformed_bytes = []
    for i in range(len(bytes_arr)):

        binary_str = new_bytes_arr[i]
        byte_1 = binary_str[0: FOUR]
        byte_2 = binary_str[FOUR:]
        lookup_row = int(byte_1, 2)
        lookup_col = int(byte_2, 2)
        hex_str = S_BOX[lookup_row][lookup_col]
        transformed_binary_str = hex_to_eight_bit_binary_string(hex_str)

        transformed_bytes.append(transformed_binary_str)
    
    first_byte = transformed_bytes[0]
    round_constant =  ROUND_CONSTANTS[round]
    round_constant_half_byte_1 = hex_to_four_bit_binary_string( round_constant[0])
    round_constant_half_byte_2 = hex_to_four_bit_binary_string( round_constant[1])
    round_constant_byte = round_constant_half_byte_1 +round_constant_half_byte_2


    transformed_bytes[0] = xor(first_byte, round_constant_byte)
    return transformed_bytes

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