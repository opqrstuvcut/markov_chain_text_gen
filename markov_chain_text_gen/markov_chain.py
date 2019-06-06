#! /usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
from collections import defaultdict
from itertools import islice

import MeCab
import numpy as np
import jaconv


def parse_argument():
    parser = argparse.ArgumentParser("", add_help=True)
    parser.add_argument("--input", "-i")
    parser.add_argument("--ngram", "-n", type=int)
    parser.add_argument("--max_size", "-m", type=int)
    parser.add_argument("--output_path", "-o")
    args = parser.parse_args()
    return args


def read_text(path):
    mecab = MeCab.Tagger("-Owakati")
    with open(path, "r") as f:
        texts = []
        for text in f:
            text = text.replace("「", "").replace("」", "")
            parsed_text = mecab.parse(text).strip().split(" ")
            texts.append(parsed_text)

    return texts


def make_dist(texts, ngrams=3):
    dist_dict = dict()
    for text in texts:
        text = ["" for _ in range(ngrams)] + text
        for word_ind, word in enumerate(text):
            ngram_words = tuple(text[word_ind - ngrams: word_ind])

            if ngram_words not in dist_dict.keys():
                dist_dict[ngram_words] = defaultdict(int)

            dist_dict[ngram_words][word] += 1

    return dist_dict


def generate_text(dist_dict, ngrams=3, max_size=3):
    while True:
        ngram_words = tuple(["" for _ in range(ngrams)])
        generated_text = []
        phrase_point_num = 0
        zero_ind_num = 0
        phrase_word_num = 0
        while ngram_words in dist_dict.keys():
            word_dist = dist_dict[ngram_words]
            keys = list(word_dist.keys())
            counts = np.array(list(word_dist.values()))
            prob = counts / np.sum(counts)
            word_ind = np.where(np.random.multinomial(1, prob) == 1)[0][0]
            word = keys[word_ind]
            generated_text.append(word)
            ngram_words = tuple([ngram_words[1 + i] if i != ngrams - 1 else word for i in range(ngrams)])
            print(word_ind)

            if phrase_word_num >= 20:
                break

            if word == "。":
                phrase_point_num += 1
                phrase_word_num = 0
                if phrase_point_num >= max_size:
                    break
            else:
                phrase_word_num += 1

            if word_ind != 0:
                zero_ind_num += 1

        print("")
        if phrase_word_num >= 20:
            continue

        if zero_ind_num > 4:
            break

    return generated_text


def unify_text(texts):
    unification_dict = {}
    for text in texts:
        for i, word in enumerate(text):
            if jaconv.kata2hira(word) in unification_dict:
                text[i] = jaconv.kata2hira(word)
            elif jaconv.hira2kata(word) in unification_dict:
                text[i] = jaconv.hira2kata(word)
            else:
                unification_dict[word] = True

    return texts


def main():
    args = parse_argument()
    parsed_text = read_text(args.input)
    parsed_text = unify_text(parsed_text)
    dist = make_dist(parsed_text, args.ngram)
    generated_text = generate_text(dist, args.ngram, args.max_size)
    print("".join(generated_text))


if __name__ == '__main__':
    main()
