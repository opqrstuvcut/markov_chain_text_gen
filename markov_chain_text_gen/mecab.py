import MeCab


def get_mecab_ins():
    return MeCab.Tagger("-Owakati")
