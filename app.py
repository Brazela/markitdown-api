from flask import Flask, request, jsonify
from markitdown import MarkItDown
from dotenv import load_dotenv
from openai import OpenAI
import os
import mimetypes
import traceback

app = Flask(__name__)

md = MarkItDown()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("BASE_URL")
)

IMAGE_MODEL = os.getenv("IMAGE_MODEL")

def is_image(file_path):
    mime, _ = mimetypes.guess_type(file_path)
    return mime and mime.startswith("image")


@app.route("/convert", methods=["POST"])
def convert():
    try:
        file = request.files["file"]

        path = f"/tmp/{file.filename}"
        file.save(path)

        # -----------------------------
        # IMAGE HANDLING (AI VISION)
        # -----------------------------
        if is_image(path):
            with open(path, "rb") as f:
                result = client.chat.completions.create(
                    model=IMAGE_MODEL,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "Convert this image into clean markdown text."
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": "data:image/png;base64," + 
                                               f.read().hex()
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
        # PDF / DOCUMENT HANDLING
        # -----------------------------
        result = md.convert(path)

        return jsonify({
            "markdown": result.text_content
        })

    except Exception as e:
        print(traceback.format_exc())
        return jsonify({
            "error": str(e)
        }), 500


@app.route("/")
def home():
    return "Document text/image text extractor is running"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
