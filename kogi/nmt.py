import os
from re import M

import sys
from .logger import kogi_print
from .nmt_compose import compose

DEVICE = None
model = None
tokenizer = None
cached = {}


def _load_gdown(model_path, model_id, quiet=True):
    kogi_print('Downloading Kogi Programming AI Model...')
    os.system('pip install --upgrade gdown')
    import gdown
    url = f'https://drive.google.com/uc?id={model_id}'

    gdown.download(url, 'model.zip', quiet=quiet)
    os.system(f'rm -rf {model_path}')
    os.system(f'unzip -d {model_path} -j model.zip')


def load_model(model_id, model_path='./kogi_model'):
    global model, tokenizer, cached, DEVICE
    if not os.path.exists(model_path):
        _load_gdown(model_path=model_path, model_id=model_id)

    if os.path.exists(model_path):
        kogi_print('Initializing Transormers and T5 ...')
        try:
            import sentencepiece
        except ModuleNotFoundError:
            os.system('pip install sentencepiece')
        import torch
        try:
            from transformers import T5ForConditionalGeneration, MT5Tokenizer
        except ModuleNotFoundError:
            os.system('pip install transformers')
            from transformers import T5ForConditionalGeneration, MT5Tokenizer

        USE_GPU = torch.cuda.is_available()
        DEVICE = torch.device('cuda:0' if USE_GPU else 'cpu')
        kogi_print('DEVICE :', DEVICE)

        model = T5ForConditionalGeneration.from_pretrained(model_path)
        tokenizer = MT5Tokenizer.from_pretrained(model_path, is_fast=True)
        cached = {}


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


# def beam_search(s, max_length=128, beams=5):
#     input_ids = tokenizer.encode_plus(
#         s,
#         add_special_tokens=True,
#         max_length=max_length,
#         padding="do_not_pad",
#         truncation=True,
#         return_tensors='pt').input_ids.to(DEVICE)
#     beam_outputs = model.generate(
#         input_ids,
#         max_length=max_length,
#         num_beams=beams,
#         no_repeat_ngram_size=2,
#         num_return_sequences=beams,
#         early_stopping=True
#     )
#     return [tokenizer.decode(beam_output, skip_special_tokens=True) for beam_output in beam_outputs]


# def _translate_beam(s: str, beams: int, max_length=64):
#     global model, tokenizer, DEVICE
#     model.config.update({"num_beams": beams})
#     input_ids = tokenizer.encode_plus(s,
#                                       add_special_tokens=True,
#                                       max_length=max_length,
#                                       # padding="max_length",
#                                       padding="do_not_pad",
#                                       truncation=True,
#                                       return_tensors='pt').input_ids.to(DEVICE)
#     predict = model.generate(input_ids,
#                              return_dict_in_generate=True,
#                              output_scores=True,
#                              length_penalty=8.0,
#                              max_length=max_length,
#                              num_return_sequences=beams,
#                              early_stopping=True)
#     pred_list = sorted([[tokenizer.decode(predict.sequences[i], skip_special_tokens=True),
#                          predict.sequences_scores[i].item()] for i in range(len(predict))], key=lambda x: x[1], reverse=True)
#     sentences_list = [i[0] for i in pred_list]
#     scores_list = [i[1] for i in pred_list]
#     return sentences_list, scores_list


model_id = None


def kogi_enable_ai(access_key: str, start_loading=False):
    global model_id
    model_id = access_key
    if model_id is not None:
        load_model(model_id)


def get_nmt():
    global model, cached
    if model_id is None:
        return compose(lambda s: 'わん')
    if model is None:
        load_model(model_id)

    def generate(s, max_length=80):
        if s in cached:
            return cached[s]
        t = greedy_search(s, max_length=max_length)
        cached[s] = t
        return t
    return compose(generate)


if __name__ == '__main__':
    nmt = get_nmt()
    for a in sys.argv[1:]:
        print(a, nmt(a))
