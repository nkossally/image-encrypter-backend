from flask_socketio import SocketIO, emit
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import cloudinary
import cloudinary.uploader

from stable import forward_substitution_v2, backwards_substitution_v2
from shift_rows import forward_shift, backward_shift
from mix_column import  mix_columns, inverse_mix_columns
from key_expansion import handle_key_expansion_round_v2
from utilities import  xor_int_matrices, convert_image_to_matrix, binary_int_array_to_image, binary_int_matrix_to_binary_string_matrices, binary_string_matrices_to_binary_int_matrix, generate_key, convert_hex_key_to_matrix, convert_hex_matrix_to_int_matrix, convert_int_matrix_to_hex_matrix, convert_hex_key_to_matrix, convert_int_matrix_to_hex_matrix, convert_binary_str_matrix_to_int_matrix, convert_int_matrix_to_binary_str_matrix, matrix_contains_empty_string
from consts import matrix_5

app = Flask(__name__)
cors = CORS(app, supports_credentials=True) # allow CORS for all domains on all routes.
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
socketio = SocketIO(app, cors_allowed_origins="http://localhost:3000")

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
        hex_key_matrix = convert_hex_key_to_matrix(hex_key)
        keys = [hex_key_matrix]
        for i in range(10):
            hex_key_matrix = handle_key_expansion_round_v2(hex_key_matrix, i)
            keys.append(hex_key_matrix)

        encrypted_int_matrices = []
        for idx, matrix in enumerate(int_matrices):
            if matrix_contains_empty_string(matrix):
                encrypted_int_matrices.append(matrix)
            else:
                encrypted_int_matrices.append(encrypt_16_bytes_v2(matrix, keys))
            socketio.emit('progress_update', {'progress': 100 * idx / len(int_matrices) })
        
        encrypted_str_matrices = list(map(convert_int_matrix_to_binary_str_matrix,encrypted_int_matrices ))
        binary_int_arr = binary_string_matrices_to_binary_int_matrix(encrypted_str_matrices)
        result = binary_int_array_to_image(binary_int_arr, "encrypted_image.png")
        socketio.emit('progress_update', {'progress': 100})

        return jsonify({"message": "File encrypted successfully", "url": result["url"], "key": hex_key }), 200
    else:
        return jsonify({"error": "Unsupported file type"}), 415


@app.route('/decrypt', methods = ['POST'])
@cross_origin()
def decrypt_v2():
    if 'image' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['image']

    hex_key = request.form.get('key')
    hex_key_matrix = convert_hex_key_to_matrix(hex_key)
    keys = [hex_key_matrix]
    for i in range(10):
        hex_key_matrix = handle_key_expansion_round_v2(hex_key_matrix, i)
        keys.insert(0, hex_key_matrix)
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file and allowed_file(file.filename):
        binary_matrices = convert_image_to_matrix(file)
        str_matrices = binary_int_matrix_to_binary_string_matrices(binary_matrices)
        int_matrices = list(map(convert_binary_str_matrix_to_int_matrix, str_matrices))
        decrypted_int_matrices = []
        for idx, matrix in enumerate(int_matrices):
            if matrix_contains_empty_string(matrix):
                decrypted_int_matrices.append(matrix)
            else:
                decrypted_int_matrices.append(decrypt_16_bytes_v2(matrix, keys))
            socketio.emit('progress_update', {'progress': 100 * idx / len(int_matrices) })

        derypted_str_matrices = list(map(convert_int_matrix_to_binary_str_matrix,decrypted_int_matrices ))
        binary_int_arr = binary_string_matrices_to_binary_int_matrix(derypted_str_matrices)
        result = binary_int_array_to_image(binary_int_arr, "encrypted_image.png")
       
        socketio.emit('progress_update', {'progress': 100})
        return jsonify({"message": "File decrypted successfully", "url": result["url"] }), 200
    else:
        return jsonify({"error": "Unsupported file type"}), 415


def encrypt_16_bytes_v2(curr_int_matrix, keys):

    hex_key_matrix = keys[0]
    curr_int_matrix = xor_int_matrices(
        curr_int_matrix, hex_key_matrix)

    for i in range(10):
        curr_int_matrix = forward_substitution_v2(curr_int_matrix)
        curr_int_matrix = forward_shift(curr_int_matrix)
        if i != 9:
            curr_int_matrix = mix_columns(curr_int_matrix)
        hex_key_matrix = keys[i + 1]
        curr_int_matrix = xor_int_matrices(
            curr_int_matrix, hex_key_matrix)
    return curr_int_matrix


def decrypt_16_bytes_v2(curr_int_matrix, keys):

    hex_key_matrix = keys[0]
    curr_int_matrix = xor_int_matrices(
        curr_int_matrix, hex_key_matrix)

    for i in range(10):
        curr_int_matrix = backward_shift(curr_int_matrix)
        curr_int_matrix = backwards_substitution_v2(curr_int_matrix)
        curr_int_matrix = xor_int_matrices(
            curr_int_matrix, keys[i + 1])

        if i != 9:
            curr_int_matrix = inverse_mix_columns(curr_int_matrix)

    return curr_int_matrix


@app.route('/test', methods = ['POST'])
@cross_origin()
def test():

    # matrixie = convert_hex_matrix_to_int_matrix(matrix_4)
    # print(matrixie)
    # int_result = encrypt_16_bytes_v2(matrixie, hex_key)
    # result = convert_int_matrix_to_hex_matrix(int_result)

    # print(result)
    # int_result = decrypt_16_bytes_v2(int_result, hex_key)
    # result = convert_int_matrix_to_hex_matrix(int_result)
    # print(result)


    matrix = convert_hex_matrix_to_int_matrix(matrix_5)
    forwarded = mix_columns(matrix)
    result = convert_int_matrix_to_hex_matrix(forwarded)
    print(result)

    inversed = inverse_mix_columns(forwarded)
    result = convert_int_matrix_to_hex_matrix(inversed)
    print(result)
    return {}
