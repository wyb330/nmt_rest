import os.path

from fastapi import FastAPI
from pydantic import BaseModel
from transformers import pipeline, T5TokenizerFast
from transformers.pipelines.pt_utils import KeyDataset
from datasets import Dataset
from argparse import ArgumentParser
import torch
from text_parser import SentenceParser
from subtitle_utils import *
import logging

MAX_TEXT_LEN = 1000000  # 클라이언트 요청 당 가능한 텍스트 길이
MAX_INPUT_LEN = 255  # 한 라인당 최대 토큰 수

tokenizer_name = "paust/pko-t5-base"
tokenizer = T5TokenizerFast.from_pretrained(tokenizer_name)

app = FastAPI()


# 로거 생성
def setting_log(log_level='info'):
    logger = logging.getLogger('nmt')
    if log_level == 'debug':
        level = logging.DEBUG
    elif log_level == 'info':
        level = logging.INFO
    elif log_level == 'warning':
        level = logging.WARNING
    else:
        level = logging.ERROR
    logger.setLevel(level)  # 로거 레벨 설정

    # 파일 핸들러 생성
    log_path = './logs'
    os.makedirs(log_path, exist_ok=True)
    file_handler = logging.FileHandler(os.path.join(log_path, 'nmt.log'), mode='a', encoding='utf8')
    file_handler.setLevel(level)  # 핸들러 레벨 설정

    # 핸들러 생성 및 설정
    console_handler = logging.StreamHandler()  # 콘솔 출력용
    console_handler.setLevel(level)

    # 포맷터 생성 및 핸들러에 연결
    formatter = logging.Formatter('%(asctime)s \n%(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # 로거에 핸들러 추가
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


class TranslationInput(BaseModel):
    sl: str  # source 언어
    tl: str  # target 언어
    hn: str  # 높임말 여부
    q: str  # 번역할 텍스트


class TranslatedText(BaseModel):
    translated_text: str


class SubtitleInput(BaseModel):
    sl: str  # source 언어
    tl: str  # target 언어
    filename: str


class SubtitleOutput(BaseModel):
    output: str
    error: str


def split_text_by_words(text):
    words = text.split()
    substrings = []
    current_substring = ""

    for word in words:
        if len(current_substring) + len(word) + 1 <= 255:
            current_substring += word + " "
        else:
            substrings.append(current_substring.strip())
            current_substring = word + " "

    if current_substring:
        substrings.append(current_substring.strip())

    return substrings


def load_data(g):
    dataset = Dataset.from_generator(g)
    return dataset


def translate_sents(prompt, sents):
    sources = []

    def generator():
        for source in sources:
            yield {'src': source.strip()}

    for sent in sents:
        sources.append(prompt + sent.strip())
    if len(sources) > 1:
        dataset = load_data(generator)
        targets = translator(KeyDataset(dataset, 'src'), batch_size=len(sents))
        targets = [t[0] for t in targets]
    else:
        targets = translator(sources, batch_size=len(sents))

    for src, tgt in zip(sources, targets):
        logger.debug(src.replace(prompt, '') + '\n' + tgt["translation_text"] + '\n')
    return targets


@app.post("/translate", response_model=TranslatedText)
async def translate_text(input_data: TranslationInput):

    def add_result(inputs):
        ts = translate_sents(prompt, inputs)
        result.extend([t["translation_text"] for t in ts])

    if input_data.tl == "ko":
        if input_data.hn in ['Y', 'y']:
            prompt = "E2K, FRM: "  # 영어->한국어, 존댓말
        else:
            prompt = "E2K: "
    else:
        prompt = "K2E: "

    text = input_data.q
    if not text.strip():
        return TranslatedText(translated_text=input_data.q)
    if len(text) > MAX_TEXT_LEN:
        text = text[:MAX_TEXT_LEN]
    lines = text.splitlines()
    result = []
    batch = []
    sent_parser = SentenceParser()
    for line in lines:
        if len(line) > MAX_INPUT_LEN:
            if len(batch) > 0:
                add_result(batch)
                batch = []
            # sents = split_text(line, input_data.tl)
            sents = sent_parser.parse(line)
            targets = translate_sents(prompt, sents)
            sents = [target["translation_text"] for target in targets]
            result.append(' '.join(sents))
        else:
            if line.strip():
                batch.append(line)
                if len(batch) == args.batch:
                    add_result(batch)
                    batch = []
            else:
                if len(batch) > 0:
                    add_result(batch)
                    batch = []
                result.append(line)

    if len(batch) > 0:
        add_result(batch)
    result = '\n'.join(result)
    return TranslatedText(translated_text=result)


@app.post("/pdf", response_model=TranslatedText)
async def translate_pdf(input_data: TranslationInput):

    def add_result(inputs):
        ts = translate_sents(prompt, inputs)
        result.extend([t["translation_text"] for t in ts])

    if input_data.tl == "ko":
        if input_data.hn in ['Y', 'y']:
            prompt = "E2K, FRM: "  # 영어->한국어, 존댓말
        else:
            prompt = "E2K: "
    else:
        prompt = "K2E: "

    text = input_data.q
    if not text.strip():
        return TranslatedText(translated_text=input_data.q)

    pdf_parser = SentenceParser()
    lines = text.splitlines()
    result = []
    batch = []
    for line in lines:
        if len(line) > MAX_INPUT_LEN:
            if len(batch) > 0:
                add_result(batch)
                batch = []
            # sents = split_text(line, input_data.tl)
            sents = pdf_parser.parse(line)
            targets = translate_sents(prompt, sents)
            sents = [target["translation_text"] for target in targets]
            result.append(' '.join(sents))
        else:
            if line.strip():
                batch.append(line)
                if len(batch) == args.batch:
                    add_result(batch)
                    batch = []
            else:
                if len(batch) > 0:
                    add_result(batch)
                    batch = []
                result.append(line)

    if len(batch) > 0:
        add_result(batch)
    result = [line.replace('\n', '') for line in result]
    result = '\n'.join(result).strip()
    return TranslatedText(translated_text=result)


@app.post("/subtitle", response_model=SubtitleOutput)
async def translate_subtitle(input_data: SubtitleInput):
    filename = input_data.filename
    if not os.path.exists(filename):
        return SubtitleOutput(output='', error='자막 파일이 존재하지 않습니다.')
    sources, times = subtitle_captions(filename)
    if sources is None:
        return SubtitleOutput(output='', error='자막 읽기 실패')
    if input_data.tl == 'en':
        prompt = "K2E: "
    else:
        prompt = "E2K, NRM: "
    targets = []
    for i in range(0, len(sources), args.batch):
        batch = sources[i:i + args.batch]
        target = translate_sents(prompt, batch)
        target = [t["translation_text"] for t in target]
        targets.extend(target)

    assert len(sources) == len(targets)
    ext = file_ext(filename)
    output = filename.replace(ext, '_' + input_data.tl + ext)
    if ext == '.srt':
        save_to_srt(output, targets, times)
    else:
        save_to_smi(output, times, sources, targets, 'False')
    return SubtitleOutput(output=output, error='')


if __name__ == "__main__":
    from uvicorn import run

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', type=int, default=5000)
    parser.add_argument('-m', '--model', type=str, default='./models/BlueT')
    parser.add_argument('-b', '--batch', type=int, default=8)
    parser.add_argument('-l', '--log_level', type=str, default='info')
    args = parser.parse_args()
    model_path = args.model
    logger = setting_log(args.log_level)
    if not os.path.exists(model_path):
        logger.error(f"{model_path}가 존재하지 않습니다.")
        raise ValueError(f"{model_path}가 존재하지 않습니다.")
    if torch.cuda.is_available():
        translator = pipeline("translation", model=model_path, tokenizer=tokenizer, max_length=MAX_INPUT_LEN, device="cuda")
        # logger.info("NVIDIA GPU를 이용해 번역엔진 구동...")
    else:
        translator = pipeline("translation", model=model_path, tokenizer=tokenizer, max_length=MAX_INPUT_LEN)
        # logger.info("CPU를 이용해 번역엔진 구동...")
    run(app, host="127.0.0.1", port=args.port)
