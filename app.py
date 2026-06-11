from flask import Flask, request, jsonify
from markitdown import MarkItDown
from dotenv import load_dotenv
from openai import OpenAI
import os
import mimetypes
import traceback
import base64
import tempfile

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Limit uploads to 10 MB
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

md = MarkItDown()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("BASE_URL"),
    timeout=120
)

IMAGE_MODEL = os.getenv("IMAGE_MODEL")


def is_image(file_path):
    mime, _ = mimetypes.guess_type(file_path)
    return mime is not None and mime.startswith("image/")


@app.route("/")
def home():
    return "Document text/image text extractor is running"


@app.route("/convert", methods=["POST"])
def convert():
    temp_path = None

    try:
        if "file" not in request.files:
            return jsonify({
                "error": "No file uploaded"
            }), 400

        file = request.files["file"]

        if file.filename == "":
            return jsonify({
                "error": "No file selected"
            }), 400

        # Save to temp file
        suffix = os.path.splitext(file.filename)[1]

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp:
            file.save(temp.name)
            temp_path = temp.name

        # -----------------------------
        # IMAGE HANDLING
        # -----------------------------
        if is_image(temp_path):

            mime, _ = mimetypes.guess_type(temp_path)

            with open(temp_path, "rb") as img:
                image_bytes = img.read()

            b64 = base64.b64encode(image_bytes).decode("utf-8")

            result = client.chat.completions.create(
                model=IMAGE_MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Extract all visible text and convert it into clean Markdown. Preserve headings, tables, lists, and formatting where possible."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime};base64,{b64}"
                                }
                            }
                        ]
                    }
                ]
            )

            return jsonify({
                "markdown": result.choices[0].message.content
            })

        # -----------------------------
        # DOCUMENT HANDLING
        # -----------------------------
        result = md.convert(temp_path)

        return jsonify({
            "markdown": result.text_content
        })

    except Exception as e:
        print(traceback.format_exc())

        return jsonify({
            "error": str(e)
        }), 500

    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
