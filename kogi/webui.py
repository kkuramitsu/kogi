import IPython
from IPython.display import display, HTML
from google.colab import output
from .utils import listfy
from .logger import load_slack, kogi_print, log, send_log, print_nop, record_login
from .nmt import get_nmt, kogi_enable_ai
from .dialog import get_chatbot

def debug_log():
    try:
        kogi_print('recieving events')
        send_log()
    except Exception as e:
        kogi_print(e)

# https://github.com/googlecolab/colabtools/tree/0162530b8c7f76741ee3e518db34aa5c173e8ebe/google/colab

BOT_ICON = 'https://iconbu.com/wp-content/uploads/2021/02/コーギーのイラスト.jpg'
#BOT_ICON = 'https://kohacu.com/wp-content/uploads/2021/05/kohacu.com_samune_003370-768x768.png'
YOUR_ICON = 'https://2.bp.blogspot.com/-VVtgu8RyEJo/VZ-QWqgI_wI/AAAAAAAAvKY/N-xnZvqeGYY/s800/girl_question.png'

CHAT_CSS = '''
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
textarea {
  width: 100%; 
  box-sizing: border-box;  /* ※これがないと横にはみ出る */
  height:30px; 
  font-size: large;
  outline: none; /* ※ブラウザが標準で付加する線を消したいとき */
  resize: none;
}
</style>
'''

CHAT_HTML = '''
<div id='main'>
<script>
var timer = null;
var inputPane = document.getElementById('input');
inputPane.addEventListener('keydown', (e) => {
  if(e.keyCode == 13) {
    var text = inputPane.value;
    google.colab.kernel.invokeFunction('notebook.ask', [text], {});
    inputPane.value='';
    if(timer !== null) {
        clearTimeout(timer);
    }
    timer = setTimeout(()=>{
        google.colab.kernel.invokeFunction('notebook.log', [], {});
    }, 1000*60*5);
  }
});
var target = document.getElementById('output');
target.scrollIntoView(false);
</script>
<div id='output' class='box scrolly'>
</div>
<div style='text-align: right'>
<textarea id='input' placeholder='質問はここに'></textarea>
</div>
</div>
'''

BOT_HTML = '''
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

CLEAR_HTML = '''
<script>
setTimeout(()=>{
    const element = document.getElementById('main'); 
    element.remove();
}, 8000);
</script>
'''


USER_HTML = '''
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
        bot_name = kw.get('bot_name', 'コギー')
        bot_icon = kw.get('bot_icon', BOT_ICON)
        for text in listfy(bot_text):
            display(HTML(BOT_HTML.format(bot_icon, bot_name, text)))
    if 'バイバイ' in bot_text:
        display(HTML(CLEAR_HTML))


def _display_you(your_text, **kw):
    with output.redirect_to_element('#output'):
        your_name = kw.get('your_name', 'あなた')
        your_icon = kw.get('your_icon', YOUR_ICON)
        for text in listfy(your_text):
            display(HTML(USER_HTML.format(your_icon, your_name, text)))


kogi_frame = {  # グローバルフレーム
    'your_name': 'あなた',
    'your_icon': YOUR_ICON,
    'bot_name': 'コギー',
    'bot_icon': BOT_ICON,
    'display': _display_bot,
}


N_GLOBALS = 0


def _needs_new_chat():
    global N_GLOBALS
    state = get_ipython().ev('len(globals())')
    if state != N_GLOBALS:
        N_GLOBALS = state
        return True
    return False


def _display_chat(chatbot=None):
    display(HTML(CHAT_CSS))
    display(HTML(CHAT_HTML))
    if chatbot is None:
        chatbot = get_chatbot()

    def ask(your_text):
        global kogi_frame
        your_text = your_text.strip()
        if 'ありがとう' in your_text or 'バイバイ' in your_text:
            _display_bot('バイバイ')
        else:
            bot_text = chatbot(your_text)
            log(type='chat', user=your_text, bot=bot_text)
            _display_you(your_text, **kogi_frame)
            if bot_text is not None:
                _display_bot(bot_text, **kogi_frame)

    output.register_callback('notebook.ask', ask)
    output.register_callback('notebook.log', debug_log)


def kogi_say(msg, chatbot=None):
    if _needs_new_chat():
        _display_chat(chatbot)
    _display_bot(msg, **kogi_frame)


def kogi_help(chatbot=None):
    kogi_say('どうした？', chatbot)


# translate
TRANSLATE_CSS_HTML = '''
<style>
.parent {
  background-color: #edebeb;
  width: 100%;
  height: 150px;
}
textarea {
  width: 100%; 
  box-sizing: border-box;  /* ※これがないと横にはみ出る */
  height:120px; 
  font-size: large;
  outline: none;           /* ※ブラウザが標準で付加する線を消したいとき */
  resize: none;
}
.box11{
//    padding: 0.5em 1em;
//    margin: 2em 0;
    color: #5d627b;
    background: white;
    border-top: solid 5px #5d627b;
    box-shadow: 0 3px 5px rgba(0, 0, 0, 0.22);
}
.box18{
  //padding: 0.2em 0.5em;
  //margin: 2em 0;
  color: #565656;
  background: #ffeaea;
  background-image: url(https://2.bp.blogspot.com/-u7NQvQSgyAY/Ur1HXta5W7I/AAAAAAAAcfE/omW7_szrzao/s800/dog_corgi.png);
  background-size: 150%;
  background-repeat: no-repeat;
  background-position: top right;
  background-color:rgba(255,255,255,0.8);
  background-blend-mode:lighten;
  //box-shadow: 0px 0px 0px 10px #ffeaea;
  border: dashed 2px #ffc3c3;
  //border-radius: 8px;
}
.box16{
    //padding: 0.5em 1em;
    //margin: 2em 0;
    background: -webkit-repeating-linear-gradient(-45deg, #f0f8ff, #f0f8ff 3px,#e9f4ff 3px, #e9f4ff 7px);
    background: repeating-linear-gradient(-45deg, #f0f8ff, #f0f8ff 3px,#e9f4ff 3px, #e9f4ff 7px);
}
.box24 {
    position: relative;
    padding: 0.5em 0.7em;
    margin: 2em 0;
    background: #6f4b3e;
    color: white;
    font-weight: bold;
}
.box24:after {
    position: absolute;
    content: '';
    top: 100%;
    left: 30px;
    border: 15px solid transparent;
    border-top: 15px solid #6f4b3e;
    width: 0;
    height: 0;
}
</style>
<div class="parent">
<div style="float: left; width: 48%; text-align: right;">
<label class="box24" for="input">日本語</label>
<textarea id="input" class="box16"></textarea>
</div>
<div style="float: left; width: 48%; text-align: right;">
<label class="box24" for="outout">Python</label>
<textarea id="output" class="box18 python" readonly></textarea>
</div>
</div>
'''

TRANSLATE_SCRIPT = '''
<script>
    var timer = null;
    var logtimer = null;
    document.getElementById('input').addEventListener('input', (e) => {
        var text = e.srcElement.value;
        if(timer !== null) {
            clearTimeout(timer);
        }
        if(logtimer !== null) {
            clearTimeout(logtimer);
        }
        timer = setTimeout(() => {
            timer = null;
            (async function() {
                const result = await google.colab.kernel.invokeFunction('notebook.Convert', [text], {});
                const data = result.data['application/json'];
                const textarea = document.getElementById('output');
                textarea.textContent = data.result;
            })();
        }, 600);  // 何も打たななかったら600ms秒後に送信
        logtimer = setTimeout(() => {
            // logtimer = null;
            google.colab.kernel.invokeFunction('notebook.Logger', [], {});
        }, 60*1000*5); // 5分に１回まとめて送信
    });
</script>
'''


cached = {}


def kogi_translate(delay=600, print=print_nop):
    nmt = get_nmt()

    def convert(text):
        try:
            ss = []
            for line in text.split('\n'):
                if line not in cached:
                    translated = nmt(line)
                    print(line, '=>', translated)
                    cached[line] = translated
                    log(
                        type='realtime-nmt',
                        input=line, output=translated,
                    )
                else:
                    translated = cached[line]
                ss.append(translated)
            text = '\n'.join(ss)
            return IPython.display.JSON({'result': text})
        except Exception as e:
            print(e)
        return e
    output.register_callback('notebook.Convert', convert)
    output.register_callback('notebook.Logger', debug_log)
    display(IPython.display.HTML(TRANSLATE_CSS_HTML))
    SCRIPT = TRANSLATE_SCRIPT.replace('600', str(delay))
    display(IPython.display.HTML(SCRIPT))


# LOGIN


# ダミー関数
LOGIN_HTML = '''
<style>
.parent {
  background-color: #edebeb;
  width: 100%;
  height: 150px;
}
textarea {
  width: 100%; 
  box-sizing: border-box;  /* ※これがないと横にはみ出る */
  height:120px; 
  font-size: large;
  outline: none;           /* ※ブラウザが標準で付加する線を消したいとき */
  resize: none;
}
.box18{
  //padding: 0.2em 0.5em;
  //margin: 2em 0;
  color: #565656;
  background: #ffeaea;
  //box-shadow: 0px 0px 0px 10px #ffeaea;
  border: dashed 2px #ffc3c3;
  //border-radius: 8px;
}
.box16{
    //padding: 0.5em 1em;
    //margin: 2em 0;
    background: -webkit-repeating-linear-gradient(-45deg, #f0f8ff, #f0f8ff 3px,#e9f4ff 3px, #e9f4ff 7px);
    background: repeating-linear-gradient(-45deg, #f0f8ff, #f0f8ff 3px,#e9f4ff 3px, #e9f4ff 7px);
}
.box24 {
    position: relative;
    padding: 0.5em 0.7em;
    margin: 2em 0;
    background: #6f4b3e;
    color: white;
    font-weight: bold;
}
.button02 {
  //justify-content: space-between;
  //margin: 0 auto;
  //padding: 1em 2em;
  width: 300px;
  color: #333;
  //font-size: 18px;
  font-weight: 700;
  background-color: #cccccc;
  border-radius: 50vh;
}
</style>
<label>Student ID</label><input id="name"/>
<span class="button02" id="ok">Ready</span>
<div class="parent">
<div style="float: left; width: 48%; text-align: right;">
<label class="box24" for="input">Type In</label>
<textarea id="input" class="box16"></textarea>
</div>
<div style="float: left; width: 48%; text-align: right;">
<label class="box24" for="outout">Code</label>
<textarea id="output" class="box18 python" readonly>print(math.sin(math.pi/2))
print(["oranges", "tables"])
print(weight / (height * height))
print(x if x >= y else y)
print(s[0].upper() for s in "abc")
</textarea>
</div>
</div>
'''

LOGIN_SCRIPT = '''
<script>
    var timer = null;
    var buffers = [];
    var dict = {};
    const idPane = document.getElementById('name');
    const inputPane = document.getElementById('input');
    var submitted = false;
    var buttonClick = () => {
        if(!submitted) {
            var name = idPane.value;
            var value = inputPane.value;
            var text = buffers.join(' ');
            google.colab.kernel.invokeFunction('notebook.login', [name, value, dict, text, window.navigator.userAgent], {});
            submitted = true;
        }
    };
    var before = new Date().getTime();
    idPane.addEventListener('keydown', (e) => {
        before = new Date().getTime();
        if(idPane.value.length >= 7) {
            document.getElementById('ok').innerText = 'Go';
            return;
        }
    });
    inputPane.addEventListener('keydown', (e) => {
      var now = new Date().getTime();
      if(e.key === ' ') {
        buffers.push(`${now - before} SPACE`);
      }
      else {
        buffers.push(`${now - before} ${e.key}`);
      }
      before = now;
      if(idPane.value.length < 7) {
          inputPane.value = '';
          return;
      }
      dict[e.key] = (dict[e.key] || 0) + 1;
      var size = inputPane.value.length;
      if(size > 10 && dict[')'] >= 8 && dict['i'] >= 10 && dict['t'] >= 10) {
        document.getElementById('ok').innerText = '出席';
        setTimeout(buttonClick, 5000);
      }
      else{
        document.getElementById('ok').innerText = `${size}`;
      }
    });
</script>
'''


def kogi_login(ai_key=None, slack_key=None, print=kogi_print):
    def login(name, code, counts, keys, useragent):
        code = code.strip()
        keys = keys.split('\n')[-1]
        record_login(uid=name, code=code, keys=keys, counts=counts, browser=useragent)

    output.register_callback('notebook.login', login)
    display(IPython.display.HTML(LOGIN_HTML))
    display(IPython.display.HTML(LOGIN_SCRIPT))
    load_slack(slack_key)
    if ai_key is not None:
        try:
            kogi_enable_ai(ai_key, start_loading=True)
        except Exception as e:
            print('Disabled AI', e)
            kogi_enable_ai(None, start_loading=True)
