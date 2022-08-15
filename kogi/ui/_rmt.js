var timer = null;
var logtimer = null;
var inputPane = document.getElementById('input');
inputPane.addEventListener('input', (e) => {
    var text = e.srcElement.value;
    if (timer !== null) {
        clearTimeout(timer);
    }
    if (logtimer !== null) {
        clearTimeout(logtimer);
    }
    timer = setTimeout(() => {
        timer = null;
        (async function () {
            const result = await google.colab.kernel.invokeFunction('notebook.Convert', [text], {});
            const data = result.data['application/json'];
            const textarea = document.getElementById('output');
            textarea.textContent = data.result;
        })();
    }, 800);  // 何も打たななかったら600ms秒後に送信
    logtimer = setTimeout(() => {
        // logtimer = null;
        google.colab.kernel.invokeFunction('notebook.Logger', [], {});
    }, 60 * 1000 * 5); // 5分に１回まとめて送信
});
