from PIL import Image
import numpy as np
import math
import io
from io import BytesIO
import cloudinary
import cloudinary.uploader
import secrets

# Configuration       
cloudinary.config(
    cloud_name = "dhumr9ajv", 
    api_key = "897897225992447", 
    api_secret = "kzphOSXDte8CvQLQ5m6-YFyhQvo", # Click 'View API Keys' above to copy your API secret
    secure=True
)


SIXTEEN = 16
FOUR = 4
EIGHT = 8

def xor_binary_arrays(arr_1, arr_2):
    transformed_matrix = []
    for i in range(len(arr_1)):
        new_row = []
        for j in range(len(arr_1[0])):
            binary_str_1 = arr_1[i][j]
            binary_str_2 = arr_2[i][j]
            sum = xor(binary_str_1, binary_str_2)
            new_row.append(sum)
        
        transformed_matrix.append(new_row)
    
    return transformed_matrix

def xor_int_matrices(arr_1, arr_2):
    transformed_matrix = []
    for i in range(len(arr_1)):
        if "" in arr_1[i] or "" in arr_2[i]:
            return [["", "", "", ""], ["", "", "", ""], ["", "", "", ""], ["", "", "", ""]]

        new_row = []
        for j in range(len(arr_1[0])):
     
            sum = arr_1[i][j] ^ arr_2[i][j] 
            new_row.append(sum)
        
        transformed_matrix.append(new_row)
    
    return transformed_matrix

def xor(binary_str_1, binary_str_2):
    sum = ""
    for i in range(len(binary_str_1)):
        if binary_str_1[i] != binary_str_2[i]:
            sum += "1"
        else:
            sum += "0"
    return sum


def hex_to_eight_bit_binary_string( hex_string ):
    int_value = int(hex_string, SIXTEEN)

    binary_string = format((int_value), '08b')
    
    return binary_string

def hex_to_four_bit_binary_string( hex_string ):
    int_value = int(hex_string, SIXTEEN)

    binary_string = format((int_value), '04b')
    
    return binary_string

def convert_binary_arr_to_hex_arr(binary_arr):
    transformed_arr= []

    for binary_str in binary_arr:
        half_byte_1 = binary_str[0: FOUR]
        half_byte_2 = binary_str[FOUR :]
        hex_str = binary_to_hex_string(half_byte_1) + binary_to_hex_string(half_byte_2)
        if len(hex_str) == 4:
            hex_str = hex_str[1] + hex_str[3]
        transformed_arr.append(hex_str)

    return transformed_arr

def convert_binary_matrix_to_hex_matrix(matrix):
    transformed_matrix = []

    for i in range(len(matrix)):
        new_row = []
        for binary_string in matrix[i]:
            byte_1 = binary_string[0: FOUR]
            byte_2 = binary_string[FOUR :]
            hex_str = binary_to_hex_string(byte_1) + binary_to_hex_string(byte_2)
            if len(hex_str) == 4:
                hex_str = hex_str[1] + hex_str[3]

            new_row.append(hex_str)
        transformed_matrix.append(new_row)

    return transformed_matrix

def binary_to_hex_string( binary_string ):
    int_value = int(binary_string, 2)

    hex_string = hex(int_value)[2:]
    
    return hex_string


def convert_image_to_matrix(file):
    # Load the image
    image = Image.open(file)

    # Convert to grayscale (this step makes the image easier to threshold)
    gray_image = image.convert('L')

    # Convert the grayscale image to a NumPy array
    gray_array = np.array(gray_image)

    # Apply a threshold to convert the grayscale image to binary
    # You can adjust the threshold value (here, it's 128) to get the desired result
    threshold = 128
    binary_matrix = (gray_array > threshold).astype(int)

    return binary_matrix


def binary_int_array_to_image(binary_matrix, file_save_path):
    numpy_binary_matrix = np.array(binary_matrix)  # Ensure it's a NumPy array

    numpy_binary_matrix = numpy_binary_matrix.astype(np.uint8)  # Convert to unsigned 8-bit integers

    # Convert binary matrix to an 8-bit image (0=black, 255=white)
    image_data = numpy_binary_matrix * 255  # Multiply by 255 to make it a grayscale image

    # Convert the image data to a PIL Image
    image = Image.fromarray(image_data.astype(np.uint8))

    buffered = io.BytesIO()
    image.save(buffered, format="PNG")  # You can change format if needed
    buffered.seek(0)

    upload_result = cloudinary.uploader.upload(buffered, public_id="897897225992447")

    # # Save or display the image
    # image.show()  # To display the image
    # image.save(file_save_path)  # Save the image to a file
    return {"url": upload_result["secure_url"]}


def binary_int_matrix_to_binary_string_matrices(binary_int_matrix):
    result = []
    for row in binary_int_matrix:
        for i in range(EIGHT):
            binary_str_matrix = []
            for j in range(FOUR):
                str_row = []
                for k in range(FOUR):
                    idx = i * FOUR * FOUR * EIGHT + j * EIGHT * FOUR + k * EIGHT
                    sub_arr = list(map(str, row[idx: idx + EIGHT]))
                    sub_arr_str = "".join(sub_arr)
                    str_row.append(sub_arr_str)
                binary_str_matrix.append(str_row)
            result.append(binary_str_matrix)

    return result
 

def binary_string_matrices_to_binary_int_matrix(binary_str_matrices):
    result = []
    for i in range(0, len(binary_str_matrices), EIGHT):
        string = ""
        for j in range(EIGHT):
            if i + j < len(binary_str_matrices):
                string += convert_binary_str_matrix_to_str(binary_str_matrices[i + j])
        arr = list(map(int, list(string)))
        result.append(arr)
    return result


def image_to_byte_array(image_path):
    img = Image.open(image_path)
    img_array = np.array(img)
    height, width, channels = img_array.shape
    binary_strings = []
    for row in img_array:
        for pixel in row:
            for channel_value in pixel:
                binary_string = bin(channel_value)[2:].zfill(8)  # Ensure 8 bits
                binary_strings.append(binary_string)
    return binary_strings, (width, height)


def convert_binary_str_matrix_to_str(binary_str_matrix):
    def flatten_arr(arr):
        return "".join(arr)

    joined_matrix = list(map(flatten_arr, binary_str_matrix))
    joined_string = flatten_arr(joined_matrix)
    return joined_string


def generate_key():
    hex_string = secrets.token_hex(16)  
    return hex_string
  

def convert_hex_key_to_matrix(hex_str):
    chunks = [hex_str[i:i+2] for i in range(0, len(hex_str), 2)]

    def connvert_to_byte(hex_str):
        return int(hex_str, SIXTEEN)
    
    chunks = list(map(connvert_to_byte, chunks))

    chunks = [chunks[i: i+ FOUR] for i in range(0, len(chunks), FOUR)]

    return chunks


def convert_hex_matrix_to_int_matrix(matrix):
    new_matrix = []

    def connvert_to_byte(hex_str):
        return int(hex_str, SIXTEEN)

    for arr in matrix:
        new_matrix.append(  list(map(connvert_to_byte, arr)))

    return new_matrix

def convert_int_matrix_to_hex_matrix(matrix):
    new_matrix = []

    def convert_to_hex_str(num):
        return format(num, '02X')


    for arr in matrix:
        new_matrix.append(  list(map(convert_to_hex_str, arr)))

    return new_matrix


def convert_binary_string_matrix_to_int_matrix(matrix):
    transformed_matrix = []

    def get_int(binary_str):
        return int(binary_str, 2)

    for row in matrix:
        transformed_matrix.append(list(map(get_int, row)))

    return transformed_matrix


def convert_binary_str_matrix_to_int_matrix(binary_str_matrix):
    matrix = []
    for row in binary_str_matrix:
        new_row = []
        for elem in row:
            if elem != "":
                new_row.append(int(elem, 2))
            else:
                new_row.append("")
        matrix.append(new_row)
    return matrix

def convert_int_matrix_to_binary_str_matrix(matrix):
    if matrix_contains_empty_string(matrix):
        return [[],[],[],[]]
    binary_str_matrix = []
    for row in matrix:
        new_row = []
        for elem in row:
            new_row.append(format(elem, '08b'))
        binary_str_matrix.append(new_row)
    return binary_str_matrix

def matrix_contains_empty_string(matrix):
    for row in matrix:
        if "" in row:
            return True
    return False