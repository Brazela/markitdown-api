from flask import Flask, request, jsonify
from markitdown import MarkItDown
import os

app = Flask(__name__)
md = MarkItDown()

@app.route("/convert", methods=["POST"])
def convert():
    file = request.files["file"]
    path = "temp.pdf"
    file.save(path)

    result = md.convert(path)

    return jsonify({"markdown": result.text_content})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)