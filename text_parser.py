""" 텍스트를 문장 단위로 분리하는 파서 """

BOUNDRY_CHARS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ \n"'


class SentenceParser:
    def __init__(self):
        self.i = 0
        self.text = None
        self.abbreviations = ["Mr.", "Ms.", "Mrs.", "Dr.", "Prof.", "Ph.", "etc.", "e.g.", "i.e.", "a.m.", "p.m.",
                              "vs.", "No.", "St.", "Ave.", "Dept.", "Inc.", "Ltd.", "Gov."]
        self.max_len = 255
        self.sentences = []

    def _next_char_(self, inc=1):
        if self.i + inc <= len(self.text) - 1:
            return self.text[self.i + inc]
        else:
            return None

    def _skip_(self):
        if self.i < len(self.text) - 1:
            self.i += 1
        else:
            raise IndexError

    def _is_abbr_(self, word):
        is_abbreviation = False
        for abbr in self.abbreviations:
            if word.endswith(abbr):
                is_abbreviation = True
                continue
        return is_abbreviation

    def _append_(self, sent):
        sent = sent.replace('\n', ' ').strip()
        self.sentences.append(sent)

    def parse(self, text):
        self.text = text
        self.sentences = []
        text_len = len(text)
        self.i = 0
        i_prev = 0
        while self.i < text_len:
            char = text[self.i]
            if char in ['?', '!']:
                sent = str(text[i_prev: self.i + 1])
                self.sentences.append(sent)
                i_prev = self.i + 1
            elif char == '.':
                if self.i < text_len - 1:
                    next_c = self._next_char_()
                    if next_c not in BOUNDRY_CHARS:  # . 문자 뒤에 문장 경계 후보에 해당하지 않는 문자가 오는 경우
                        self.i += 1
                        continue
                    else:
                        if next_c == ' ':
                            # self._skip_()
                            if self._next_char_(2) in BOUNDRY_CHARS:  # . 문자 뒤 공백이 오고 그 다음에 문장경계 후보 문자가 오는 경우
                                sent = str(text[i_prev: self.i + 1])
                                if self._is_abbr_(sent):
                                    self.i += 1
                                else:
                                    self._append_(sent)
                                    i_prev = self.i + 1
                        elif next_c.isupper():
                            if text[self.i - 1].islower():
                                sent = str(text[i_prev: self.i + 1])
                                if not self._is_abbr_(sent):
                                    self._append_(sent)
                                    i_prev = self.i + 1
                            else:
                                w_i = self.i - 1
                                # U.S.A.와 같은 등록되지 않은 약어인지 확인하기 위해 대문자와 . 문자를 스킵
                                while (self.i < text_len - 1) and (self._next_char_() in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ.'):
                                    self._skip_()
                                word = str(text[w_i: self.i + 1])
                                sent = str(text[i_prev: self.i + 1])
                                # word가 U.S.A와 같은 약어이거나 문장이 등록된 약어로 끝나는 경우
                                if word.isupper() or self._is_abbr_(sent):
                                    self.i += 1
                                else:
                                    self._append_(sent)
                                    i_prev = self.i + 1
                        else:
                            if next_c == '\n':
                                self._skip_()
                            sent = str(text[i_prev: self.i + 1])
                            if self._is_abbr_(sent):
                                self.i += 1
                            else:
                                self._append_(sent)
                                i_prev = self.i + 1
                else:
                    sent = str(text[i_prev: self.i + 1])
                    self._append_(sent)
                    i_prev = self.i + 1
            elif char == '"':
                if self.i < len(self.text) - 1:
                    self._skip_()
                while (text[self.i] != '"') and (self.i < text_len):
                    try:
                        self._skip_()
                    except IndexError:
                        break
            elif char == '\n':
                if (self.i + 1) < text_len - 1 and self._next_char_().isupper():
                    sent = str(text[i_prev: self.i + 1])
                    self._append_(sent)
                    i_prev = self.i + 1
                elif self.i - i_prev > self.max_len:
                    sent = str(text[i_prev: self.i + 1])
                    self._append_(sent)
                    i_prev = self.i + 1

            self.i += 1

        if self.i > i_prev:
            self._append_(str(text[i_prev: self.i + 1]))
        return self.sentences




