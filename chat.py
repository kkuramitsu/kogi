import IPython
from IPython.display import display, HTML
from google.colab import output
# https://github.com/googlecolab/colabtools/tree/0162530b8c7f76741ee3e518db34aa5c173e8ebe/google/colab

BOT_ICON = 'https://iconbu.com/wp-content/uploads/2021/02/コーギーのイラスト.jpg'
#BOT_ICON = 'https://kohacu.com/wp-content/uploads/2021/05/kohacu.com_samune_003370-768x768.png'
# 'https://chojugiga.com/c/choju51_0039/s512_choju51_0039_0.png'
YOUR_ICON = 'https://2.bp.blogspot.com/-VVtgu8RyEJo/VZ-QWqgI_wI/AAAAAAAAvKY/N-xnZvqeGYY/s800/girl_question.png'

HTML_CSS = '''
<style>
.sb-box { position: relative; overflow: hidden; }
/* アイコン画像 */
.icon-img {
    position: absolute; overflow: hidden; top: 0; width: 64px; height: 64px;
}
/* アイコン画像（左） */
.icon-img-left { left: 0; }
/* アイコン画像（右） */
.icon-img-right { right: 0; }
/* アイコン画像 */
.icon-img img { border-radius: 50%; border: 2px solid #eee; }
/* アイコンネーム */
.icon-name {
    position: absolute; width: 64px; text-align: center;
    top: 68px; color: #fff; font-size: 10px;
}
/* アイコンネーム（左） */
.icon-name-left { left: 0; }
/* アイコンネーム（右） */
.icon-name-right { right: 0; }
/* 吹き出し */
.sb-side { position: relative; float: left; margin: 0 85px 20px 85px; }
.sb-side-right { float: right; }
/* 吹き出し内のテキスト */
.sb-txt {
    position: relative; border: 2px solid #eee; border-radius: 6px;
    background: #eee; color: #333;
    font-size: 15px; line-height: 1.7; padding: 18px;
}
.sb-txt>p:last-of-type { padding-bottom: 0; margin-bottom: 0; }
/* 吹き出しの三角 */
.sb-txt:before { content: ""; position: absolute; border-style: solid; top: 16px; z-index: 3; }
.sb-txt:after { content: ""; position: absolute; border-style: solid; top: 15px; z-index: 2; }
/* 吹き出しの三角（左） */
.sb-txt-left:before {
    left: -7px; border-width: 7px 10px 7px 0;
    border-color: transparent #eee transparent transparent;
}
.sb-txt-left:after {
    left: -10px; border-width: 8px 10px 8px 0;
    border-color: transparent #eee transparent transparent;
}
/* 吹き出しの三角（右） */
.sb-txt-right:before {
    right: -7px; border-width: 7px 0 7px 10px;
    border-color: transparent transparent transparent #eee;
}
.sb-txt-right:after {
    right: -10px; border-width: 8px 0 8px 10px;
    border-color: transparent transparent transparent #eee;
}
.box{ background: powderblue; }
.scrolly{ overflow-y: scroll; }
</style>
'''

HTML_CHAT = '''
<div id='main'>
<script>
var inputPane = document.getElementById('input');
inputPane.addEventListener('keydown', (e) => {
  if(e.keyCode == 13) {
    var text = inputPane.value;
    google.colab.kernel.invokeFunction('notebook.ask', [text], {});
    inputPane.value=''
  }
});
var target = document.getElementById('output');
target.scrollIntoView(false);
</script>
<div id='output' class='box scrolly'>
</div>
<div style='text-align: right'>
<textarea id='input' placeholder='質問はここに' style='width: 100%; background: #eee;'></textarea>
</div>
</div>
'''

HTML_BOT = '''
<div class="sb-box">
    <div class="icon-img icon-img-left">
        <img src="{}" width="60px">
    </div>
    <div class="icon-name icon-name-left">{}</div>
    <div class="sb-side sb-side-left">
        <div class="sb-txt sb-txt-left">
          {}
        </div>
    </div>
</div>
'''

HTML_CLEAR = '''
<script>
setTimeout(()=>{
    const element = document.getElementById('main'); 
    element.remove();
}, 8000);
</script>
'''


HTML_USER = '''
<div class="sb-box">
  <div class="icon-img icon-img-right">
      <img src="{}" width="60px">
  </div>
  <div class="icon-name icon-name-right">{}</div>
  <div class="sb-side sb-side-right">
      <div class="sb-txt sb-txt-right">
        {}
      </div>
  </div>
</div>
'''


def _display_bot(bot_text, **kw):
    with output.redirect_to_element('#output'):
        bot_name = kw.get('bot_name', 'コーギー')
        bot_icon = kw.get('bot_icon', BOT_ICON)
        display(HTML(HTML_BOT.format(bot_icon, bot_name, bot_text)))
    if 'バイバイ' in bot_text:
        display(HTML(HTML_CLEAR))


def _display_you(your_text, **kw):
    with output.redirect_to_element('#output'):
        your_name = kw.get('your_name', 'あなた')
        your_icon = kw.get('your_icon', YOUR_ICON)
        display(HTML(HTML_USER.format(your_icon, your_name, your_text)))


corgi_frame = {  # グローバルフレーム
    'your_name': 'あなた',
    'your_icon': YOUR_ICON,
    'bot_name': 'コーギー',
    'bot_icon': BOT_ICON,
    'display': _display_bot,
}


def chat_vow(your_text, frame):
    if your_text == '':
        return 'わん'

    #print(repr(your_text), frame)
    if 'asking' in frame:
        asking = frame['asking']
        frame[asking] = your_text
        del frame['asking']

    if frame['your_name'] == 'あなた':
        frame['asking'] = 'your_name'
        return 'お名前は？'

    if 'access_key' not in frame:
        frame['asking'] = 'access_key'
        your_name = frame['your_name']
        return f'{your_name}さん、アクセスキーは？'
    else:
        return '出席記録できました. 今日も１日がんばりましょう!'


def corgi_chat(msg=[], asking=None, chat=chat_vow, background='powderblue'):
    display(HTML(HTML_CSS.replace('powderblue', background)))
    display(HTML(HTML_CHAT))

    def ask(your_text):
        global corgi_frame
        your_text = your_text.strip()
        if 'ありがとう' in your_text or 'バイバイ' in your_text:
            _display_bot('バイバイ')
        else:
            bot_text = chat(your_text, corgi_frame)
            _display_you(your_text, **corgi_frame)
            if bot_text is not None:
                _display_bot(bot_text, **corgi_frame)

    output.register_callback('notebook.ask', ask)

    if isinstance(msg, str):
        msg = [msg]
    for m in msg:
        _display_bot(m)
    if asking is not None:
        corgi_frame['asking'] = asking


# corgi_chat('お名前は？', asking='your_name')
