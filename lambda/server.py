from flask import Flask, request, jsonify
from lambda_function import lambda_handler

app = Flask(__name__)

@app.route('/alexa', methods=['POST'])
def alexa_skill():
    # Calling the lambda_handler directly avoids the cryptography library issues
    response = lambda_handler(request.get_json(), None)
    return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4997)
