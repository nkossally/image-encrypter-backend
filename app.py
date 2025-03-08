import time
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os

from stable import forward_substitution, forward_substitution_v2,  backwards_substitution, S_BOX, INVERSE_MATRIX, S_BOX_INT
from shift_rows import forward_shift, backward_shift
from mix_column import forward_mix, backward_mix
from key_expansion import convert_32_char_hex_text_to_binary_matrix, handle_key_expansion_round, handle_key_expansion_round_v2
from utilities import xor_binary_arrays, convert_binary_matrix_to_hex_matrix, convert_image_to_matrix, binary_int_array_to_image, binary_int_matrix_to_binary_string_matrices, binary_string_matrices_to_binary_int_matrix, generate_key, convert_image_to_byte_array, convert_hex_string_to_bytes, convert_byte_arr_to_byte_matrices, convert_hex_key_to_matrix, convert_hex_matrix_to_int_matrix, convert_int_matrix_to_hex_matrix, convert_hex_key_to_matrix
import cloudinary
import cloudinary.uploader
from flask_cors import CORS, cross_origin

app = Flask(__name__)
cors = CORS(app) # allow CORS for all domains on all routes.
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Configuration       
cloudinary.config(
    cloud_name = "dhumr9ajv", 
    api_key = "897897225992447", 
    api_secret = "kzphOSXDte8CvQLQ5m6-YFyhQvo", # Click 'View API Keys' above to copy your API secret
    secure=True
)


key = "00001010101000011000101100000011001111000000111110110011001011011111101110011111100010110101010100110001100011011010100101110100"
hex_key = "0f1571c947d9e8590cb7add6af7f6798"
text = "0123456789abcdeffedcba9876543210"

decryption_key = [['b4', '8e', 'f3', '52'], ['ba', '98', '13', '4e'], [
    '7f', '4d', '59', '20'], ['86', '26', '18', '76']]

matrix = [
    ["EA", "04", "65", "85"],
    ["83", "45", "5D", "96"],
    ["5C", "33", "98", "B0"],
    ["F0", "2D", "AD", "C5"]
]

@app.route('/encrypt', methods = ['POST'])
@cross_origin()
def encrypt():
    if 'image' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['image']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file and allowed_file(file.filename):
        binary_matrices = convert_image_to_matrix(file)
        str_matrices = binary_int_matrix_to_binary_string_matrices(binary_matrices)
        hex_key = generate_key()
        encrypted_str_matrices = []
        for matrix in str_matrices:
            encrypted_str_matrices.append(encrypt_16_bytes(matrix, hex_key))
        binary_int_arr = binary_string_matrices_to_binary_int_matrix(encrypted_str_matrices)
        result = binary_int_array_to_image(binary_int_arr, "encrypted_image.png")

        print("result", result)

        return jsonify({"message": "File uploaded successfully", "url": result, "hex_key": hex_key }), 200
    else:
        return jsonify({"error": "Unsupported file type"}), 415


@app.route('/decrypt', methods = ['POST'])
@cross_origin()
def decrypt():
    if 'image' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['image']

    hex_key = request.form.get('key')

    print("key", key)
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file and allowed_file(file.filename):
        binary_matrices = convert_image_to_matrix(file)
        str_matrices = binary_int_matrix_to_binary_string_matrices(binary_matrices)
        decrypted_str_matrices = []
        for matrix in str_matrices:
            decrypted_str_matrices.append(decrypt_16_bytes(matrix, hex_key))       
        binary_int_arr = binary_string_matrices_to_binary_int_matrix(decrypted_str_matrices)
        result = binary_int_array_to_image(binary_int_arr, "decrypted_image.png")

        print("result", result)

        return jsonify({"message": "File uploaded successfully", "url": result }), 200
    else:
        return jsonify({"error": "Unsupported file type"}), 415

def encrypt_16_bytes(curr_text_binary_arr, hex_key):
    key_binary_arr = convert_32_char_hex_text_to_binary_matrix(hex_key)
    curr_text_binary_arr = xor_binary_arrays(
        curr_text_binary_arr, key_binary_arr)

    for i in range(10):
        curr_text_binary_arr = forward_substitution(curr_text_binary_arr)
        curr_text_binary_arr = forward_shift(curr_text_binary_arr)
        if i != 9:
            curr_text_binary_arr = forward_mix(curr_text_binary_arr)
        key_binary_arr = handle_key_expansion_round(key_binary_arr, i)
        key_hex_arr = convert_binary_matrix_to_hex_matrix(key_binary_arr)
        curr_text_binary_arr = xor_binary_arrays(
            curr_text_binary_arr, key_binary_arr)
    return curr_text_binary_arr


def decrypt_16_bytes(curr_text_binary_arr, hex_key):

    round_keys = []
    key_binary_arr = convert_32_char_hex_text_to_binary_matrix(hex_key)

    # round_keys.insert(0, key_binary_arr)

    for i in range(10):
        round_keys.insert(0, key_binary_arr)
        key_binary_arr = handle_key_expansion_round(key_binary_arr, i)
        # key_hex_arr = convert_binary_matrix_to_hex_matrix(round_key

    curr_text_binary_arr = xor_binary_arrays(
        curr_text_binary_arr, key_binary_arr)

    for i in range(10):
        curr_text_binary_arr = backward_shift(curr_text_binary_arr)
        curr_text_binary_arr = backwards_substitution(curr_text_binary_arr)
        curr_text_binary_arr = xor_binary_arrays(
            curr_text_binary_arr, round_keys[i])

        if i != 9:
            curr_text_binary_arr = backward_mix(curr_text_binary_arr)

    return curr_text_binary_arr


def blarg(hex_key):
    # binary_matrices = convert_image_to_matrix()
    # str_matrices = binary_int_matrix_to_binary_string_matrices(binary_matrices)
    # encrypted_str_matrices = []
    # for matrix in str_matrices:
    #     encrypted_str_matrices.append(encrypt_16_bytes(matrix, hex_key))
    # binary_int_arr = binary_string_matrices_to_binary_int_matrix(encrypted_str_matrices)
    # binary_int_array_to_image(binary_int_arr, "encrypted_image.png")
    # decrypted_str_matrices = []
    # for matrix in str_matrices:
    #     decrypted_str_matrices.append(decrypt_16_bytes(matrix, hex_key))
    
    # binary_int_arr = binary_string_matrices_to_binary_int_matrix(decrypted_str_matrices)
    # binary_int_array_to_image(binary_int_arr, "decrypted_image.png")


    # byte_arr = convert_image_to_byte_array()
    # matrices = convert_byte_arr_to_byte_matrices(byte_arr)

    # conversion = int("g", 16)
    # print(conversion)

    def connvert_to_byte(hex_str):
        return int(hex_str, 16)

    # int_matrix = convert_hex_matrix_to_int_matrix(matrix)
    # poo = forward_substitution_v2(int_matrix)
    # poo = convert_int_matrix_to_hex_matrix(poo)
    hex_key = "0f1571c947d9e8590cb7add6af7f6798"

    hex_matrix = convert_hex_key_to_matrix(hex_key)
    print("hex_matrix", hex_matrix)
    keys = [hex_matrix]
    curr = hex_matrix
    for i in range(10):
        curr = handle_key_expansion_round_v2(curr, i)
        keys.append(curr)

    keys = list(map(convert_int_matrix_to_hex_matrix, keys))
    print(keys)


blarg("")
