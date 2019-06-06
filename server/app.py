from flask import Flask, render_template, jsonify
from markov_chain_text_gen import markov_chain

gen = markov_chain.Generator(ngrams=3, max_size=2, max_words=20, text_complex=4)
app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/generate", methods=["GET"])
def generate():
    text = gen.generate_text()

    return jsonify({"res": text})


if __name__ == '__main__':
    app.run()
