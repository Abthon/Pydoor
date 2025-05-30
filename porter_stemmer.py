# backend/api/news/porter_stemmer.py

import re
import joblib
from pathlib import Path
from django.conf import settings
from sklearn.feature_extraction.text import TfidfVectorizer, ENGLISH_STOP_WORDS

# ———————————————
# 1) Your PorterStemmer
# ———————————————
class PorterStemmer:
    vowel = re.compile(r'[aeiou]')
    double_consonant = re.compile(r'([^aeiou])\1$')
    cvc = re.compile(r'([^aeiou][aeiou][^aeiouwxy])$')

    def measure(self, stem):
        form = re.sub(r'[^aeiou]+', 'C', stem)
        form = re.sub(r'[aeiou]+', 'V', form)
        return form.count('VC')

    def contains_vowel(self, word):
        return bool(self.vowel.search(word))

    def ends_double_consonant(self, word):
        return bool(self.double_consonant.search(word))

    def ends_cvc(self, word):
        return bool(self.cvc.search(word))

    def replace_suffix(self, word, suffix, replacement, min_m):
        if word.endswith(suffix):
            stem = word[:-len(suffix)]
            if self.measure(stem) > min_m:
                return stem + replacement
        return word

    def step1a(self, word):
        if word.endswith('sses'):
            return word[:-2]
        if word.endswith('ies'):
            return word[:-2]
        if word.endswith('ss'):
            return word
        if word.endswith('s'):
            return word[:-1]
        return word

    def step1b(self, word):
        if word.endswith('eed'):
            stem = word[:-3]
            if self.measure(stem) > 0:
                return stem + 'ee'
            return word
        for suf in ('ed', 'ing'):
            if word.endswith(suf):
                stem = word[:-len(suf)]
                if self.contains_vowel(stem):
                    word = stem
                    if word.endswith(('at','bl','iz')):
                        return word + 'e'
                    if self.ends_double_consonant(word) and not word.endswith(('l','s','z')):
                        return word[:-1]
                    if self.measure(word) == 1 and self.ends_cvc(word):
                        return word + 'e'
                    return word
        return word

    def step1c(self, word):
        if word.endswith('y') and self.contains_vowel(word[:-1]):
            return word[:-1] + 'i'
        return word

    def step2(self, word):
        suffixes = {
            'ational':'ate','tional':'tion','enci':'ence','anci':'ance',
            'izer':'ize','abli':'able','alli':'al','entli':'ent',
            'eli':'e','ousli':'ous','ization':'ize','ation':'ate',
            'ator':'ate','alism':'al','iveness':'ive','fulness':'ful',
            'ousness':'ous','aliti':'al','iviti':'ive','biliti':'ble',
            'logi':'log'
        }
        for suf, rep in suffixes.items():
            word2 = self.replace_suffix(word, suf, rep, 0)
            if word2 != word:
                return word2
        return word

    def step3(self, word):
        suffixes = {
            'icate':'ic','ative':'','alize':'al','iciti':'ic',
            'ical':'ic','ful':'','ness':''
        }
        for suf, rep in suffixes.items():
            word2 = self.replace_suffix(word, suf, rep, 0)
            if word2 != word:
                return word2
        return word

    def step4(self, word):
        suffixes = (
            'al','ance','ence','er','ic','able','ible','ant','ement',
            'ment','ent','ion','ou','ism','ate','iti','ous','ive','ize'
        )
        for suf in suffixes:
            if word.endswith(suf):
                stem = word[:-len(suf)]
                if self.measure(stem) > 1:
                    if suf == 'ion' and stem[-1] not in ('s','t'):
                        return word
                    return stem
        return word

    def step5a(self, word):
        if word.endswith('e'):
            stem = word[:-1]
            m = self.measure(stem)
            if m > 1 or (m == 1 and not self.ends_cvc(stem)):
                return stem
        return word

    def step5b(self, word):
        if self.measure(word) > 1 and self.ends_double_consonant(word) and word.endswith('l'):
            return word[:-1]
        return word

    def stem(self, word):
        word = word.lower()
        if len(word) <= 2:
            return word
        for step in (
            self.step1a, self.step1b, self.step1c,
            self.step2, self.step3, self.step4,
            self.step5a, self.step5b
        ):
            word = step(word)
        return word

# ———————————————
# 2) TF–IDF Indexing Helpers
# ———————————————

# where we dump/load our index
INDEX_PATH = Path(settings.BASE_DIR) / 'news_index.joblib'

# single shared stemmer instance
_porter = PorterStemmer()

def porter_analyzer(text: str) -> list[str]:
    """
    Tokenizes on word chars, lowercases, then stems each token,
    and filters out English stop-words.
    """
    tokens = re.findall(r'\w+', text.lower())
    stems  = [ _porter.stem(tok) for tok in tokens ]
    # drop any stems that are known English stop words
    return [ s for s in stems if s not in ENGLISH_STOP_WORDS ]


def build_index():
    from api.models import News

    qs   = News.objects.all().order_by('id')
    docs = [n.content or '' for n in qs]
    ids  = [n.id for n in qs]

    print(f"Building News index on {len(ids)} docs…")        # ← add this line

    vec = TfidfVectorizer(analyzer=porter_analyzer, lowercase=False)
    mat = vec.fit_transform(docs)

    joblib.dump({'ids': ids, 'vec': vec, 'mat': mat}, INDEX_PATH)
    print(f"  → indices written to {INDEX_PATH}")

def load_index():
    """
    Load the dict {'ids','vec','mat'} from disk.
    """
    return joblib.load(INDEX_PATH)
