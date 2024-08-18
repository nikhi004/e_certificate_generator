from flask import Flask, request, send_file, render_template_string
from PIL import Image, ImageDraw, ImageFont
import io
import logging
import os

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Constants
MM_TO_PIXELS = 96 / 25.4  # Conversion factor for mm to pixels

# Convert given dimensions from mm to pixels
name_width_px = int(117.36 * MM_TO_PIXELS)
name_height_px = int(40.59 * MM_TO_PIXELS)
name_x_px = int(220 * MM_TO_PIXELS)
name_y_px = int(263 * MM_TO_PIXELS)
font_size_px = 150  # Font size remains the same

@app.route('/')
def home():
    return render_template_string('''
    <!doctype html>
    <html lang="en">
      <head>
        <!-- Required meta tags -->
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
        <title>Generate Your Badge</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 100vh;
                background-color: #f4f4f4;
            }
            .container {
                text-align: center;
                padding: 20px;
                background-color: #fff;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                border-radius: 8px;
            }
            h1 {
                font-size: 24px;
                margin-bottom: 20px;
            }
            label {
                display: block;
                margin-bottom: 8px;
                font-size: 16px;
            }
            input[type="text"] {
                padding: 10px;
                width: 80%;
                margin-bottom: 20px;
                border: 1px solid #ccc;
                border-radius: 4px;
                font-size: 16px;
            }
            button {
                padding: 10px 20px;
                background-color: #007bff;
                color: #fff;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 16px;
            }
            button:hover {
                background-color: #0056b3;
            }
        </style>
      </head>
      <body>
        <div class="container">
            <h1>Generate Your Badge</h1>
            <form id="badgeForm" enctype="multipart/form-data" method="post" action="/generate_badge">
                <label for="name">Enter Your Name:</label>
                <input type="text" id="name" name="name" required>
                <br>
                <button type="submit">Generate Badge</button>
            </form>
        </div>
        <script>
            document.getElementById('badgeForm').onsubmit = function(event) {
                event.preventDefault();
                var formData = new FormData(this);
                
                fetch('/generate_badge', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.blob())
                .then(blob => {
                    var link = document.createElement('a');
                    link.href = URL.createObjectURL(blob);
                    link.download = 'badge.png';
                    link.click();
                });
            };
        </script>
      </body>
    </html>
    ''')

@app.route('/generate_badge', methods=['POST'])
def generate_badge():
    try:
        name = request.form['name']

        # Open the badge template
        template_path = 'img.png'
        if not os.path.exists(template_path):
            logging.error(f"Template image not found at path: {template_path}")
            return "Template image not found", 500

        badge_template = Image.open(template_path)

        # Draw the name on the badge
        draw = ImageDraw.Draw(badge_template)
        font_path = 'Allura-Regular.ttf'
        if not os.path.exists(font_path):
            logging.error(f"Font file not found at path: {font_path}")
            return "Font file not found", 500

        font = ImageFont.truetype(font_path, font_size_px)  # Use the Allura font
        text_position = (name_x_px, name_y_px)  # Position for the name in pixels
        draw.text(text_position, name, fill="white", font=font)
        
        # Save the badge to a bytes buffer
        buffer = io.BytesIO()
        badge_template.save(buffer, format="PNG")
        buffer.seek(0)
        
        logging.info("Badge generated successfully")
        return send_file(buffer, mimetype='image/png')
    except Exception as e:
        logging.error(f"Error generating badge: {e}")
        return "An error occurred", 500

if __name__ == '__main__':
    app.run(debug=True)
