from flask import Flask, request, jsonify
import os

from stable import forward_substitution_v2, backwards_substitution_v2
from shift_rows import forward_shift, backward_shift
from mix_column import  forward_mix_v2, backward_mix_v2
from key_expansion import handle_key_expansion_round_v2
from utilities import  xor_int_matrices, convert_image_to_matrix, binary_int_array_to_image, binary_int_matrix_to_binary_string_matrices, binary_string_matrices_to_binary_int_matrix, generate_key, convert_hex_key_to_matrix, convert_hex_matrix_to_int_matrix, convert_int_matrix_to_hex_matrix, convert_hex_key_to_matrix, convert_int_matrix_to_hex_matrix, convert_binary_str_matrix_to_int_matrix, convert_int_matrix_to_binary_str_matrix, matrix_contains_empty_string
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

matrix_2 = [
    ["87", "6E", "46", "A6"],
    ["F2", "4C", "E7", "8C"],
    ["4D", "90", "4A", "D8"],
    ["97", "EC", "C3", "95"]
]

matrix_4 = [
["01", "23", "45", "67"],
["89", "ab", "cd", "ef"],
["fe", "dc", "ba", "98"],
["76", "54", "32", "10"]
]


@app.route('/encrypt', methods = ['POST'])
@cross_origin()
def encrypt_v2():
    if 'image' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['image']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file and allowed_file(file.filename):
        binary_matrices = convert_image_to_matrix(file)
        str_matrices = binary_int_matrix_to_binary_string_matrices(binary_matrices)
        int_matrices = list(map(convert_binary_str_matrix_to_int_matrix, str_matrices))
        hex_key = generate_key()
        encrypted_int_matrices = []
        for matrix in int_matrices:
            if matrix_contains_empty_string(matrix):
                encrypted_int_matrices.append(matrix)
            else:
                encrypted_int_matrices.append(encrypt_16_bytes_v2(matrix, hex_key))
        
        encrypted_str_matrices = list(map(convert_int_matrix_to_binary_str_matrix,encrypted_int_matrices ))
        binary_int_arr = binary_string_matrices_to_binary_int_matrix(encrypted_str_matrices)
        result = binary_int_array_to_image(binary_int_arr, "encrypted_image.png")

        return jsonify({"message": "File uploaded successfully", "url": result["url"], "hex_key": hex_key }), 200
    else:
        return jsonify({"error": "Unsupported file type"}), 415


@app.route('/decrypt', methods = ['POST'])
@cross_origin()
def decrypt_v2():
    if 'image' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['image']

    hex_key = request.form.get('key')
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file and allowed_file(file.filename):
        binary_matrices = convert_image_to_matrix(file)
        str_matrices = binary_int_matrix_to_binary_string_matrices(binary_matrices)
        int_matrices = list(map(convert_binary_str_matrix_to_int_matrix, str_matrices))
        decrypted_int_matrices = []
        for matrix in int_matrices:
            if matrix_contains_empty_string(matrix):
                decrypted_int_matrices.append(matrix)
            else:
                decrypted_int_matrices.append(decrypt_16_bytes_v2(matrix, hex_key))
    
        derypted_str_matrices = list(map(convert_int_matrix_to_binary_str_matrix,decrypted_int_matrices ))
        binary_int_arr = binary_string_matrices_to_binary_int_matrix(derypted_str_matrices)
        result = binary_int_array_to_image(binary_int_arr, "encrypted_image.png")
       

        return jsonify({"message": "File uploaded successfully", "url": result }), 200
    else:
        return jsonify({"error": "Unsupported file type"}), 415


def encrypt_16_bytes_v2(curr_int_matrix, hex_key):

    hex_key_matrix = convert_hex_key_to_matrix(hex_key)
    curr_int_matrix = xor_int_matrices(
        curr_int_matrix, hex_key_matrix)

    for i in range(10):
        curr_int_matrix = forward_substitution_v2(curr_int_matrix)
        curr_int_matrix = forward_shift(curr_int_matrix)
        if i != 9:
            curr_int_matrix = forward_mix_v2(curr_int_matrix)
        hex_key_matrix = handle_key_expansion_round_v2(hex_key_matrix, i)
        key_hex_arr = convert_int_matrix_to_hex_matrix(hex_key_matrix)
        curr_int_matrix = xor_int_matrices(
            curr_int_matrix, hex_key_matrix)
    return curr_int_matrix


def decrypt_16_bytes_v2(curr_int_matrix, hex_key):

    hex_key_matrix = convert_hex_key_to_matrix(hex_key)

    round_keys = []

    # round_keys.insert(0, key_binary_arr)

    for i in range(10):
        round_keys.insert(0, hex_key_matrix)
        hex_key_matrix = handle_key_expansion_round_v2(hex_key_matrix, i)
        # key_hex_arr = convert_binary_matrix_to_hex_matrix(round_key

    curr_int_matrix = xor_int_matrices(
        curr_int_matrix, hex_key_matrix)

    for i in range(10):
        curr_int_matrix = backward_shift(curr_int_matrix)
        curr_int_matrix = backwards_substitution_v2(curr_int_matrix)
        curr_int_matrix = xor_int_matrices(
            curr_int_matrix, round_keys[i])

        if i != 9:
            curr_int_matrix = backward_mix_v2(curr_int_matrix)

    return curr_int_matrix


@app.route('/test', methods = ['POST'])
@cross_origin()
def test():

    matrixie = convert_hex_matrix_to_int_matrix(matrix_4)
    print(matrixie)
    int_result = encrypt_16_bytes_v2(matrixie, hex_key)
    result = convert_int_matrix_to_hex_matrix(int_result)

    print(result)
    int_result = decrypt_16_bytes_v2(int_result, hex_key)
    result = convert_int_matrix_to_hex_matrix(int_result)
    print(result)
    
    return {}


# blarg("")



if __name__ == "__main__":
    app.run(port=8000, debug=True)