import logging
import traceback
from flask import Flask, request, jsonify, Response
import json
from lambda_function import lambda_handler

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/alexa', methods=['POST'])
def alexa_skill():
    try:
        request_json = request.get_json()
        logger.info(f"Request: {json.dumps(request_json)}")
        
        # Calling the lambda_handler
        response_dict = lambda_handler(request_json, None)
        
        logger.info(f"Response: {json.dumps(response_dict)}")
        
        # Manually create JSON response to ensure correct formatting and Content-Type
        return Response(
            response=json.dumps(response_dict),
            status=200,
            mimetype='application/json'
        )
        
    except Exception as e:
        logger.error(f"Error handling request: {e}")
        logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@app.errorhandler(500)
def server_error(e):
    # Ensure even 500 errors return JSON, not HTML
    return jsonify({"error": "Internal Server Error"}), 500

if __name__ == '__main__':
    logger.info("Starting server on port 4997")
    app.run(host='0.0.0.0', port=4997)
