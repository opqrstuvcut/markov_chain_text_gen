import os
import MeCab
from flask import Flask, render_template, jsonify, request
from markov_chain_text_gen import markov_chain, mecab

parsed_text = markov_chain.read_text("./data/pokemon.txt")
parsed_text = markov_chain.unify_text(parsed_text)
gen = markov_chain.Generator(ngrams=3, max_size=2, max_words=20, text_complex=4)
gen.make_dist(parsed_text)


mecab_parser = mecab.get_mecab_ins()

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/generate", methods=["POST"])
def generate():
    input_text = mecab_parser.parse(request.json['input']).strip().split(" ")
    text = "".join(gen.generate_text(input_text))

    return jsonify({"res": text})


if __name__ == '__main__':
    app.run()
