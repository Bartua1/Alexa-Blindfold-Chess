import logging
import traceback
from flask import Flask, request, jsonify, Response
import json
import io
from PIL import Image, ImageDraw
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

@app.route('/chessboard', methods=['GET'])
def get_chessboard():
    """Generates a chessboard image with optional highlighting."""
    highlight = request.args.get('highlight', '').lower()
    size = 600
    square_size = size // 8
    
    # Colors for the premium light chess style
    color_light = (240, 217, 181)  # Wood-ish light
    color_dark = (181, 136, 99)    # Wood-ish dark
    color_highlight = (100, 200, 100, 180) # Semi-transparent green
    
    img = Image.new('RGB', (size, size), color_light)
    draw = ImageDraw.Draw(img, 'RGBA')
    
    # Draw squares
    for row in range(8):
        for col in range(8):
            if (row + col) % 2 == 1:
                x0 = col * square_size
                y0 = row * square_size
                x1 = x0 + square_size
                y1 = y0 + square_size
                draw.rectangle([x0, y0, x1, y1], fill=color_dark)
    
    # Highlight square if requested
    if len(highlight) == 2 and highlight[0] in 'abcdefgh' and highlight[1] in '12345678':
        col = ord(highlight[0]) - ord('a')
        row = 8 - int(highlight[1])
        x0 = col * square_size
        y0 = row * square_size
        x1 = x0 + square_size
        y1 = y0 + square_size
        draw.rectangle([x0, y0, x1, y1], fill=color_highlight, outline="green", width=3)
        
    # Serve as PNG
    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    return Response(img_io.read(), mimetype='image/png')

@app.errorhandler(500)
def server_error(e):
    # Ensure even 500 errors return JSON, not HTML
    return jsonify({"error": "Internal Server Error"}), 500

if __name__ == '__main__':
    logger.info("Starting server on port 4997")
    app.run(host='0.0.0.0', port=4997)
