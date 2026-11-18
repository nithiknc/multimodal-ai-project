
from flask import Flask, render_template, request, jsonify
from PIL import Image
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

qa_pipeline = None


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


def get_qa_pipeline():
    global qa_pipeline

    if qa_pipeline is None:
        from transformers import pipeline

        qa_pipeline = pipeline(
            "visual-question-answering",
            model="Salesforce/blip-vqa-base"
        )

    return qa_pipeline


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/health")
def health():
    return jsonify({"status": "running"})


@app.route("/ask", methods=["POST"])
def ask_question():
    if "image" not in request.files:
        return jsonify({"error": "Please upload an image."}), 400

    image_file = request.files["image"]
    question = request.form.get("question", "").strip()

    if not image_file or image_file.filename == "":
        return jsonify({"error": "No image selected."}), 400

    if not allowed_file(image_file.filename):
        return jsonify({"error": "Only JPG and PNG images are supported."}), 400

    if not question:
        return jsonify({"error": "Please enter a question."}), 400

    try:
        image = Image.open(image_file.stream).convert("RGB")
        model = get_qa_pipeline()

        result = model(image, question=question)

        answer = result[0]["answer"]

        return jsonify({
            "question": question,
            "answer": answer
        })

    except Exception as error:
        app.logger.exception("Image question answering failed")
        return jsonify({
            "error": "Unable to process the image. Please try again."
        }), 500


@app.errorhandler(413)
def file_too_large(error):
    return jsonify({"error": "Image must be smaller than 10 MB."}), 413


if __name__ == "__main__":
    app.run(debug=True)
