var timer = null;
var inputPane = document.getElementById('input');
inputPane.addEventListener('keydown', (e) => {
    if (e.keyCode == 13) {
        var text = inputPane.value;
        google.colab.kernel.invokeFunction('notebook.ask', [text], {});
        inputPane.value = '';
        if (timer !== null) {
            clearTimeout(timer);
        }
        timer = setTimeout(() => {
            google.colab.kernel.invokeFunction('notebook.log', [], {});
        }, 1000 * 60 * 5);
    }
});
inputPane.addEventListener('focusin', (e) => {
    inputPane.style.height = 200;
});
// var target = document.getElementById('output');
// target.scrollIntoView(false);
