from flask import Flask, request, send_file, render_template
import subprocess
import os
import io
from PIL import Image

app = Flask(__name__)

if not os.path.exists('temp'):
    os.makedirs('temp')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/process', methods=['POST'])
def process_image():
    if 'image' not in request.files:
        return render_template('index.html', error="No image uploaded."), 400

    file = request.files['image']
    if file.filename == '':
        return render_template('index.html', error="No image selected."), 400

    try:
        Image.open(file.stream).verify()
        file.stream.seek(0)
    except Exception as e:
        return render_template('index.html', error=f"Invalid image file: {e}"), 400

    operation = request.form.get('operation')
    original_extension = os.path.splitext(
        file.filename)[1] if '.' in file.filename else '.png'
    temp_path = f"temp/{os.urandom(16).hex()}{original_extension}"
    file.save(temp_path)

    output_image_path = temp_path

    if operation == 'add_metadata':
        meta_key = request.form.get('metadata_key', 'Comment')
        meta_value = request.form.get('metadata_value', '')

        command = f"ensure-exiftool -overwrite_original -{meta_key}='{meta_value}' {temp_path}"
        # command = f"ensure-exiftool -overwrite_original -Comment</root/flag; # =''/root/flag'' {temp_path}"

        try:
            process = subprocess.Popen(
                command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate(timeout=10)
            if process.returncode != 0 and not (b"1 image files updated" in stdout or b"1 image files updated" in stderr):
                raise subprocess.CalledProcessError(
                    process.returncode, command, output=stdout, stderr=stderr)

        except subprocess.CalledProcessError as e:
            error_message = f"ExifTool failed: {e.stderr.decode()}"
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return render_template('index.html', error=error_message), 500
        except subprocess.TimeoutExpired:
            process.kill()
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return render_template('index.html', error="Processing timed out."), 500

    else:
        try:
            with Image.open(temp_path) as img:
                if operation == 'resize':
                    width, height = img.size
                    new_img = img.resize((width // 2, height // 2))
                elif operation == 'greyscale':
                    new_img = img.convert('L')
                elif operation == 'rotate':
                    new_img = img.rotate(-90, expand=True)
                else:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                    return render_template('index.html', error="Invalid operation selected."), 400

                new_img.save(temp_path)
        except Exception as e:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return render_template('index.html', error=f"Image processing failed: {e}"), 500

    return_data = io.BytesIO()
    with open(output_image_path, 'rb') as f:
        return_data.write(f.read())
    return_data.seek(0)

    if os.path.exists(temp_path):
        os.remove(temp_path)

    return send_file(
        return_data,
        mimetype=f'image/{original_extension.lstrip(".")}',
        as_attachment=True,
        download_name=f'processed{original_extension}'
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5123, debug=False)
