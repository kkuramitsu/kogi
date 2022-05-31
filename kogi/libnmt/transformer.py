
import torch
import torch.nn as nn
from torch import Tensor
from torch.nn.utils.rnn import pad_sequence
from torch.utils.data import DataLoader

from torch.nn import (TransformerEncoder, TransformerDecoder,
                      TransformerEncoderLayer, TransformerDecoderLayer)
import math
import logging
import hashlib

from kogi.libnmt.downloader import download_from_google_drive

DEVICE = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
UNK_IDX, PAD_IDX, SOS_IDX, EOS_IDX = 0, 1, 2, 3


def get_transform(tokenizer, transform_text=None, max_length=128, max_target_length=None):
    if max_target_length is None:
        max_target_length = max_length

    def encode(src, max_length=max_length):
        inputs = tokenizer.encode(src, max_length=max_length,
                                  add_special_tokens=False, truncation=True, return_tensors='pt')
        input_ids = inputs[0] + 4
        return torch.cat((torch.tensor([SOS_IDX]),
                          input_ids,
                          torch.tensor([EOS_IDX]))).to(dtype=torch.long)

    def decode(output_ids):
        output_ids = [idx-4 for idx in output_ids if idx > 4]
        return tokenizer.decode(output_ids)

    if transform_text is None:
        def transform(src, tgt):
            inputs = encode(src, max_length=max_length)
            targets = encode(tgt, max_length=max_target_length)
            return inputs, targets
    else:
        def transform(src, tgt):
            src, tgt = transform_text(src, tgt)
            inputs = encode(src, max_length=max_length)
            targets = encode(tgt, max_length=max_target_length)
            return inputs, targets
    return encode, decode, transform


# from morichan

class Seq2SeqTransformer(nn.Module):
    def __init__(self,
                 num_encoder_layers: int,
                 num_decoder_layers: int,
                 emb_size: int,
                 nhead: int,
                 src_vocab_size: int,
                 tgt_vocab_size: int,
                 dim_feedforward: int = 512,
                 dropout: float = 0.1):
        super(Seq2SeqTransformer, self).__init__()
        encoder_layer = TransformerEncoderLayer(d_model=emb_size, nhead=nhead,
                                                dim_feedforward=dim_feedforward)
        self.transformer_encoder = TransformerEncoder(
            encoder_layer, num_layers=num_encoder_layers)
        decoder_layer = TransformerDecoderLayer(d_model=emb_size, nhead=nhead,
                                                dim_feedforward=dim_feedforward)
        self.transformer_decoder = TransformerDecoder(
            decoder_layer, num_layers=num_decoder_layers)

        self.generator = nn.Linear(emb_size, tgt_vocab_size)
        self.src_tok_emb = TokenEmbedding(src_vocab_size, emb_size)
        self.tgt_tok_emb = TokenEmbedding(tgt_vocab_size, emb_size)
        self.positional_encoding = PositionalEncoding(
            emb_size, dropout=dropout)

    def forward(self,
                src: Tensor,
                tgt: Tensor,
                src_mask: Tensor,
                tgt_mask: Tensor,
                src_padding_mask: Tensor,
                tgt_padding_mask: Tensor,
                memory_key_padding_mask: Tensor):
        src_emb = self.positional_encoding(self.src_tok_emb(src))
        tgt_emb = self.positional_encoding(self.tgt_tok_emb(tgt))
        memory = self.transformer_encoder(src_emb, src_mask, src_padding_mask)
        outs = self.transformer_decoder(tgt_emb, memory, tgt_mask, None,
                                        tgt_padding_mask, memory_key_padding_mask)
        return self.generator(outs)

    def encode(self, src: Tensor, src_mask: Tensor):
        return self.transformer_encoder(self.positional_encoding(
            self.src_tok_emb(src)), src_mask)

    def decode(self, tgt: Tensor, memory: Tensor, tgt_mask: Tensor):
        return self.transformer_decoder(self.positional_encoding(
            self.tgt_tok_emb(tgt)), memory,
            tgt_mask)


class PositionalEncoding(nn.Module):
    def __init__(self,
                 emb_size: int,
                 dropout: float,
                 maxlen: int = 5000):
        super(PositionalEncoding, self).__init__()
        den = torch.exp(- torch.arange(0, emb_size, 2)
                        * math.log(10000) / emb_size)
        pos = torch.arange(0, maxlen).reshape(maxlen, 1)
        pos_embedding = torch.zeros((maxlen, emb_size))
        pos_embedding[:, 0::2] = torch.sin(pos * den)
        pos_embedding[:, 1::2] = torch.cos(pos * den)
        pos_embedding = pos_embedding.unsqueeze(-2)

        self.dropout = nn.Dropout(dropout)
        self.register_buffer('pos_embedding', pos_embedding)

    def forward(self, token_embedding: Tensor):
        return self.dropout(token_embedding +
                            self.pos_embedding[:token_embedding.size(0), :])


class TokenEmbedding(nn.Module):
    def __init__(self, vocab_size: int, emb_size):
        super(TokenEmbedding, self).__init__()
        self.embedding = nn.Embedding(vocab_size, emb_size)
        self.emb_size = emb_size

    def forward(self, tokens: Tensor):
        return self.embedding(tokens.long()) * math.sqrt(self.emb_size)

# モデルが予測を行う際に、未来の単語を見ないようにするためのマスク


def generate_square_subsequent_mask(sz):
    mask = (torch.triu(torch.ones((sz, sz), device=DEVICE)) == 1).transpose(0, 1)
    mask = mask.float().masked_fill(mask == 0, float(
        '-inf')).masked_fill(mask == 1, float(0.0))
    return mask

# ソースとターゲットのパディングトークンを隠すためのマスク
# モデルが予測を行う際に、未来の単語を見ないようにするためのマスク


def create_mask(src, tgt):
    src_seq_len = src.shape[0]
    tgt_seq_len = tgt.shape[0]

    tgt_mask = generate_square_subsequent_mask(tgt_seq_len)
    src_mask = torch.zeros((src_seq_len, src_seq_len),
                           device=DEVICE).type(torch.bool)

    src_padding_mask = (src == PAD_IDX).transpose(0, 1)
    tgt_padding_mask = (tgt == PAD_IDX).transpose(0, 1)
    return src_mask, tgt_mask, src_padding_mask, tgt_padding_mask

# train/eval


def collate_fn(batch):
    src_batch, tgt_batch = [], []
    for src_ids, tgt_ids in batch:
        src_batch.append(src_ids)
        tgt_batch.append(tgt_ids)
    src_batch = pad_sequence(src_batch, padding_value=PAD_IDX)
    tgt_batch = pad_sequence(tgt_batch, padding_value=PAD_IDX)
    return src_batch, tgt_batch


def train(train_iter, model, batch_size, loss_fn, optimizer):
    model.train()
    losses = 0

    # 学習データ
    #collate_fn = string_collate(hparams)
    train_dataloader = DataLoader(
        train_iter, batch_size=batch_size, shuffle=True,
        collate_fn=collate_fn, num_workers=2)

    for src, tgt in train_dataloader:
        src = src.to(DEVICE)
        tgt = tgt.to(DEVICE)

        tgt_input = tgt[:-1, :]

        src_mask, tgt_mask, src_padding_mask, tgt_padding_mask = create_mask(
            src, tgt_input)

        logits = model(src, tgt_input, src_mask, tgt_mask,
                       src_padding_mask, tgt_padding_mask, src_padding_mask)

        optimizer.zero_grad()

        tgt_out = tgt[1:, :]
        loss = loss_fn(
            logits.reshape(-1, logits.shape[-1]), tgt_out.reshape(-1))
        loss.backward()

        optimizer.step()
        losses += loss.item()

    return losses / len(train_dataloader)


def evaluate(val_iter, model, batch_size, loss_fn):
    model.eval()
    losses = 0

    val_dataloader = DataLoader(
        val_iter, batch_size=batch_size, shuffle=True,
        collate_fn=collate_fn, num_workers=2)

    for src, tgt in val_dataloader:
        src = src.to(DEVICE)
        tgt = tgt.to(DEVICE)

        tgt_input = tgt[:-1, :]

        src_mask, tgt_mask, src_padding_mask, tgt_padding_mask = create_mask(
            src, tgt_input)

        logits = model(src, tgt_input, src_mask, tgt_mask,
                       src_padding_mask, tgt_padding_mask, src_padding_mask)

        tgt_out = tgt[1:, :]
        loss = loss_fn(
            logits.reshape(-1, logits.shape[-1]), tgt_out.reshape(-1))
        losses += loss.item()

    return losses / len(val_dataloader)


# greedy search を使って翻訳結果 (シーケンス) を生成
# https://kikaben.com/transformers-evaluation-details/#chapter-2

def _greedy_decode(model, src, src_mask, max_len, start_symbol, device):  # original
    src = src.to(device)
    src_mask = src_mask.to(device)

    memory = model.encode(src, src_mask)
    ys = torch.ones(1, 1).fill_(start_symbol).type(torch.long).to(device)
    for i in range(max_len-1):
        memory = memory.to(device)
        tgt_mask = (generate_square_subsequent_mask(ys.size(0))
                    .type(torch.bool)).to(device)
        out = model.decode(ys, memory, tgt_mask)
        out = out.transpose(0, 1)
        prob = model.generator(out[:, -1])
        _, next_word = torch.max(prob, dim=1)
        next_word = next_word.item()

        ys = torch.cat([ys,
                        torch.ones(1, 1).type_as(src.data).fill_(next_word)], dim=0)
        if next_word == EOS_IDX:
            break
    return ys

# 翻訳

def md5(filename):
    with open(filename, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def save_model(hparams, model, file='transformer-model.pt'):
    torch.save(dict(
        tokenizer=hparams.tokenizer_name_or_path,
        additional_tokens=hparams.additional_tokens,
        num_encoder_layers=hparams.num_encoder_layers,
        num_decoder_layers=hparams.num_decoder_layers,
        emb_size=hparams.emb_size,
        nhead=hparams.nhead,
        vocab_size=hparams.vocab_size + 4,
        fnn_hid_dim=hparams.fnn_hid_dim,
        model=model.state_dict(),
    ), file)
    logging.info(f'saving... {file} {md5(file)}')


def load_model(filename, AutoTokenizer, device='cpu', dynamic_qint8=False):
    if isinstance(device, str):
        device = torch.device(device)
    checkpoint = torch.load(filename, map_location=device)
    tokenizer = AutoTokenizer.from_pretrained(checkpoint['tokenizer'])
    tokenizer.add_tokens(checkpoint['additional_tokens'])
    model = Seq2SeqTransformer(
        checkpoint['num_encoder_layers'],
        checkpoint['num_decoder_layers'],
        checkpoint['emb_size'],
        checkpoint['nhead'],
        checkpoint['vocab_size'],
        checkpoint['vocab_size'],
        checkpoint['fnn_hid_dim']
    )
    model.load_state_dict(checkpoint['model'])

    if dynamic_qint8:
        model = torch.quantization.quantize_dynamic(
            model, {torch.nn.Linear}, dtype=torch.qint8
        )
    model.to(device)
    return model, tokenizer

def load_transformer_nmt(filename, device='cpu', dynamic_qint8=False, print=print):
    if not filename.endswith('.pt'):
        download_from_google_drive(filename, filename='model.pt')
        filename='model.pt'
    if isinstance(device, str):
        device = torch.device(device)
    
    model, tokenizer = load_model(filename, device, dynamic_qint8)
    encode, decode, _ = get_transform(tokenizer)

    def generate_greedy(src: str, beam=1, max_length=128) -> str:
        model.eval()
        src = encode(src).view(-1, 1).to(device)
        num_tokens = src.shape[0]
        src_mask = (torch.zeros(num_tokens, num_tokens)).type(torch.bool)
        output_ids = _greedy_decode(
            model, src, src_mask, max_len=max_length, start_symbol=SOS_IDX, device=device).flatten()
        return decode(output_ids)
    return generate_greedy
