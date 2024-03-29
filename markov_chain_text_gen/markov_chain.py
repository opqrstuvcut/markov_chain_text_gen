#! /usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
from collections import defaultdict
from itertools import islice

import numpy as np
import jaconv

from . import mecab


def parse_argument():
    parser = argparse.ArgumentParser("", add_help=True)
    parser.add_argument("--input", "-i")
    parser.add_argument("--ngram", "-n", type=int)
    parser.add_argument("--max_size", "-m", type=int)
    args = parser.parse_args()
    return args


def read_text(path):
    mecab_parser = mecab.get_mecab_ins()
    with open(path, "r") as f:
        texts = []
        for text in f:
            text = text.replace("「", "").replace("」", "")
            parsed_text = mecab_parser.parse(text).strip().split(" ")
            texts.append(parsed_text)

    return texts


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


class Generator(object):
    def __init__(self, ngrams=3, max_size=3, max_words=20, text_complex=4):
        self._dist_dict = None
        self._ngrams = ngrams
        self._max_size = max_size
        self._max_words = max_words
        self._text_complex = text_complex

    def make_dist(self, texts):
        dist_dict = dict()
        for text in texts:
            text = ["" for _ in range(self._ngrams)] + text
            for word_ind, word in enumerate(text):
                ngram_words = tuple(text[word_ind - self._ngrams: word_ind])

                if ngram_words not in dist_dict.keys():
                    dist_dict[ngram_words] = defaultdict(int)

                dist_dict[ngram_words][word] += 1

        self._dist_dict = dist_dict

    def generate_text(self, init=None):
        while True:
            if init:
                ngram_words = tuple([init[i - self._ngrams]
                                     if i >= self._ngrams - len(init) else ""
                                     for i in range(self._ngrams)])
                generated_text = init.copy()
            else:
                ngram_words = tuple(["" for _ in range(self._ngrams)])
                generated_text = []

            text_complex = self._text_complex
            phrase_point_num = 0
            zero_ind_num = 0
            phrase_word_num = 0
            while ngram_words in self._dist_dict.keys():
                word_dist = self._dist_dict[ngram_words]
                keys = list(word_dist.keys())
                counts = np.array(list(word_dist.values()))
                prob = counts / np.sum(counts)
                word_ind = np.where(np.random.multinomial(1, prob) == 1)[0][0]
                word = keys[word_ind]
                generated_text.append(word)
                ngram_words = tuple([ngram_words[1 + i] if i != self._ngrams -
                                     1 else word for i in range(self._ngrams)])

                if phrase_word_num > self._max_words:
                    break

                if word == "。":
                    phrase_point_num += 1
                    phrase_word_num = 0
                    if phrase_point_num >= self._max_size:
                        break
                else:
                    phrase_word_num += 1

                if word_ind != 0:
                    zero_ind_num += 1

            if phrase_word_num > self._max_words:
                continue

            if zero_ind_num > text_complex:
                break

            if init:
                text_complex -= 1

        return generated_text


def main():
    args = parse_argument()
    parsed_text = read_text(args.input)
    parsed_text = unify_text(parsed_text)

    gen = Generator(args.ngram, args.max_size, 20, 4)
    gen.make_dist(parsed_text)
    generated_text = gen.generate_text(init=["美しい"])

    print("".join(generated_text))


if __name__ == '__main__':
    main()
