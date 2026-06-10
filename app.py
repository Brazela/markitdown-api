from flask import Flask, request, jsonify
from markitdown import MarkItDown
import os
import traceback

app = Flask(__name__)
md = MarkItDown()

@app.route("/convert", methods=["POST"])
def convert():
    try:
        file = request.files["file"]

        path = f"/tmp/{file.filename}"
        file.save(path)

        result = md.convert(path)

        return jsonify({
            "markdown": result.text_content
        })

    except Exception as e:
        print(traceback.format_exc())
        return jsonify({
            "error": str(e)
        }), 500
