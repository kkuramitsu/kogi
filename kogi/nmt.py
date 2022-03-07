import os
from re import M

import sys
from .logger import kogi_print
from .nmt_compose import compose

DEVICE = None
model = None
tokenizer = None

def load_gdown(model_path='./model', model_id='18W8uCn0C4-VXjBNRT543aRSG1YkQfMrh', quiet=False):
    os.system('pip install --upgrade gdown')
    import gdown
    url = f'https://drive.google.com/uc?id={model_id}'
    gdown.download(url, 'model.zip', quiet=quiet)
    os.system(f'unzip model.zip -d {model_path}')


def load_model(model_path='./model', model_id=None):
    global model, tokenizer, DEVICE
    from google_drive_downloader import GoogleDriveDownloader
    if model_id is not None and not os.path.exists(model_path):
        load_gdown(model_path=model_path, model_id=model_id)
    try:
        import sentencepiece
    except ModuleNotFoundError:
        os.system('pip install sentencepiece')
    import torch
    try:
        from transformers import MT5ForConditionalGeneration, MT5Tokenizer
    except ModuleNotFoundError:
        os.system('pip install transformers')
        from transformers import MT5ForConditionalGeneration, MT5Tokenizer

    USE_GPU = torch.cuda.is_available()
    DEVICE = torch.device('cuda:0' if USE_GPU else 'cpu')
    kogi_print('DEVICE :', DEVICE)

    model = MT5ForConditionalGeneration.from_pretrained(model_path)
    model = torch.quantization.quantize_dynamic(
        model, {torch.nn.Linear}, dtype=torch.qint8
    ).to(DEVICE)
    tokenizer = MT5Tokenizer.from_pretrained(model_path, is_fast=True)
    #tokenizer.add_tokens([f'<e{i}>' for i in range(16)])


def greedy_search(s: str, max_length=128, beam=1) -> str:
    input_ids = tokenizer.encode_plus(
        s,
        add_special_tokens=True,
        max_length=max_length,
        padding="do_not_pad",
        truncation=True,
        return_tensors='pt').input_ids.to(DEVICE)
    greedy_output = model.generate(input_ids, max_length=max_length)
    return tokenizer.decode(greedy_output[0], skip_special_tokens=True)


def beam_search(s, max_length=128, beams=5):
    input_ids = tokenizer.encode_plus(
        s,
        add_special_tokens=True,
        max_length=max_length,
        padding="do_not_pad",
        truncation=True,
        return_tensors='pt').input_ids.to(DEVICE)
    beam_outputs = model.generate(
        input_ids,
        max_length=max_length,
        num_beams=beams,
        no_repeat_ngram_size=2,
        num_return_sequences=beams,
        early_stopping=True
    )
    return [tokenizer.decode(beam_output, skip_special_tokens=True) for beam_output in beam_outputs]


def _translate_beam(s: str, beams: int, max_length=64):
    global model, tokenizer, DEVICE
    model.config.update({"num_beams": beams})
    input_ids = tokenizer.encode_plus(s,
                                      add_special_tokens=True,
                                      max_length=max_length,
                                      # padding="max_length",
                                      padding="do_not_pad",
                                      truncation=True,
                                      return_tensors='pt').input_ids.to(DEVICE)
    predict = model.generate(input_ids,
                             return_dict_in_generate=True,
                             output_scores=True,
                             length_penalty=8.0,
                             max_length=max_length,
                             num_return_sequences=beams,
                             early_stopping=True)
    pred_list = sorted([[tokenizer.decode(predict.sequences[i], skip_special_tokens=True),
                         predict.sequences_scores[i].item()] for i in range(len(predict))], key=lambda x: x[1], reverse=True)
    sentences_list = [i[0] for i in pred_list]
    scores_list = [i[1] for i in pred_list]
    return sentences_list, scores_list


cached = {}


def get_nmt2(beams=1):
    global model, cached
    if model is None:
        load_model(model_id='1qZmBK0wHO3OZblH8nabuWrrPXU6JInDc')
    cached = {}
    def generate(s, max_length=128):
        if s in cached:
            return cached[s]
        t = greedy_search(s, max_length=max_length)
        cached[s] = t
        return t
    return compose(generate)


def get_nmt(beams=1):
    return compose()


if __name__ == '__main__':
    nmt = get_nmt()
    for a in sys.argv[1:]:
        print(a, nmt(a))
