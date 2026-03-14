import os
import logging
import traceback
from flask import Flask, request, jsonify, Response
import json
import io
from PIL import Image, ImageDraw
from lambda_function import lambda_handler

import chess
from PIL import Image, ImageDraw, ImageFont

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
    """Generates a chessboard image with optional highlighting and pieces from FEN."""
    try:
        highlight = request.args.get('highlight', '').lower()
        fen = request.args.get('fen', '')
        logger.info(f"Generating chessboard image. Highlight: {highlight}, FEN: {fen}")
        
        size = 600
        square_size = size // 8
        
        # Colors for the premium light chess style
        color_light = (240, 217, 181, 255)  # Wood-ish light
        color_dark = (181, 136, 99, 255)    # Wood-ish dark
        color_highlight = (100, 200, 100, 180) # Semi-transparent green
        
        # Use RGBA to support transparency for the highlight
        img = Image.new('RGBA', (size, size), color_light)
        draw = ImageDraw.Draw(img)
        
        # Draw squares
        for row in range(8):
            for col in range(8):
                if (row + col) % 2 == 1:
                    x0 = col * square_size
                    y0 = row * square_size
                    x1 = x0 + square_size
                    y1 = y0 + square_size
                    draw.rectangle([x0, y0, x1, y1], fill=color_dark)
        
        # Draw pieces if FEN is provided
        if fen:
            try:
                # Load font - using common fonts on macOS
                # Fallback list for cross-platform robustness
                font_paths = [
                    "/Users/bartua1/Library/Fonts/JetBrainsMonoNerdFont-Regular.ttf",
                    "/System/Library/Fonts/Supplemental/Arial.ttf",
                    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" 
                ]
                font = None
                for path in font_paths:
                    if os.path.exists(path):
                        try:
                            font = ImageFont.truetype(path, int(square_size * 0.7))
                            logger.info(f"Using font: {path}")
                            break
                        except Exception as e:
                            logger.error(f"Failed to load font {path}: {e}")
                
                if not font:
                    logger.info("Falling back to default scalable font")
                    font = ImageFont.load_default(size=int(square_size * 0.7))

                board = chess.Board(fen)
                piece_count = 0
                for square in chess.SQUARES:
                    piece = board.piece_at(square)
                    if piece:
                        piece_count += 1
                        col = chess.square_file(square)
                        row = 7 - chess.square_rank(square)
                        
                        # Center of the square
                        x = col * square_size + square_size // 2
                        y = row * square_size + square_size // 2
                        
                        symbol = piece.symbol().upper()
                        # Color: White pieces white with black outline, Black pieces black with white outline
                        if piece.color == chess.WHITE:
                            fill_color = (255, 255, 255, 255)
                            stroke_color = (0, 0, 0, 255)
                        else:
                            fill_color = (0, 0, 0, 255)
                            stroke_color = (255, 255, 255, 255)
                        
                        draw.text((x, y), symbol, fill=fill_color, font=font, anchor="mm", 
                                  stroke_width=2, stroke_fill=stroke_color)
                
                logger.info(f"Rendered {piece_count} pieces on the board.")
            except Exception as e:
                logger.error(f"Error drawing pieces: {e}")

        # Highlight square if requested
        if len(highlight) == 2 and highlight[0] in 'abcdefgh' and highlight[1] in '12345678':
            col = ord(highlight[0]) - ord('a')
            row = 8 - int(highlight[1])
            x0 = col * square_size
            y0 = row * square_size
            x1 = x0 + square_size
            y1 = y0 + square_size
            # Highlight with semi-transparent green
            draw.rectangle([x0, y0, x1, y1], fill=color_highlight, outline=(0, 100, 0, 255), width=4)
            
        # Convert to RGB before saving as PNG if necessary, but PNG supports RGBA
        img_io = io.BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        return Response(img_io.read(), mimetype='image/png')
    except Exception as e:
        logger.error(f"Error generating chessboard: {e}")
        logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@app.errorhandler(500)
def server_error(e):
    # Ensure even 500 errors return JSON, not HTML
    return jsonify({"error": "Internal Server Error"}), 500

@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({"status": "ok", "message": "Chess server is running"}), 200

if __name__ == '__main__':
    logger.info("Starting server on port 4997")
    app.run(host='0.0.0.0', port=4997)
