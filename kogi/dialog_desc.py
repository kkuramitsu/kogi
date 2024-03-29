from .settings import kogi_log

DESC = {
    "コギー": "倉光研究室で飼われているAI犬！ 研究室内の会話からプログラミングを学習した。",
    "プログラミング": "巷では諸説あるが、稼ぐ手段。お金持ちになろう！",
    "構文エラー": "Pythonの文法から外れていること。大抵、軽微な間違い",
    "型エラー": "変数の種類が間違っていること。",
    "値エラー": "想定された値でないときに発生する。Googleって使い方を確認しよう。",

    "識別子": "変数や関数の名前のこと。",
    "全角文字": "漢字やひらがなのこと。",
    "半角文字": "英数字などのアスキー文字のこと。",

    "式": "評価すると、値が得られるコードのこと。最小のプログラムの単位。",
    "評価": "計算、もしくは実行と同じ。プログラミング理論の専門用語。",
    "評価する": "「計算する」、もしくは「実行する」と同じ。プログラミング理論の専門用語。",
    "数式": "評価すると、数値の結果が得られるコードのこと。",

    "条件": "評価すると、真（True）であるか、偽(False）になるコードのこと",
    "条件式": "評価すると、真（True）であるか、偽(False）になるコードのこと。論理式と同じ。",
    "論理式": "評価すると、真（True）であるか、偽(False）になるコードのこと。条件式と同じ。",
    "条件分岐": "条件に応じて、プログラムの処理内容を変えること。if文など。",

    "論理値": "真（True）か、偽(False）の２つの値のこと。ブール値とも呼ぶ。",
    "ブール値": "真（True）か、偽(False）の２つの値のこと。論理値とも呼ぶ。",
    "命題": "真（True）か、偽(False）が定まる記述のこと。数学用語。",

    "論理否定": "与えられた命題が真のときに偽となり、偽のとき真となる論理演算",
    "論理和": "二つの命題のいずれか一方あるいは両方が真のときに真となり、いずれも偽のときに偽となる論理演算",
    "論理積": "二つの命題のいずれも真のときに真となり、それ以外のときは偽となる論理演算",
    "真理値": "ある命題が真（True）であるか、偽(False）であるかを示す値のこと。",
    "真偽値": "ある命題が真（True）であるか、偽(False）であるかを示す値のこと。",

    "インデント": "字下げのこと。Pythonでは、字下げによって順次、実行するコードの単位を表します。",

    "演算子": "演算内容を表す記号のこと。+ や - など。",
    "単項演算子": "一つの項からなる演算子のこと。例えば、-x",
    "二項演算子": "二つの項からなる演算子のこと。例えば、+x",
    "算術演算子": "数式を記述する演算子のこと。+ - * / % など",
    "論理演算子": "論理式を記述する演算子のこと and or not など。",

    "オペコード": "マイクロプロセッサ（CPU/MPU）に与える機械語の命令の識別番号のこと",
    "オペランド": "数式を構成する要素のうち、演算の対象となる値や変数のこと",

    "インクリメント": "変数の値を増やす操作のこと。例えば、x += 1など。",
    "デクリメント": "変数の値を減らす操作のこと。例えば、x -= 1など。",

    "*": "二項演算子なら掛け算、単項演算子ならリストを引数へ展開する演算子。",
    "**": "累乗。2 ** 3は、2 の 3乗になる。",
    "/": "割り算。小数点以下は切り捨てられないので注意。",
    "//": "整数除算。小数点以下は切り捨てられて、整数になる。",
    "%": "割り算の余り。",

    "ビット演算": "整数を2進数のビット列とみなし、ビット操作を行う論理演算子のこと",

    "^": "排他的論理和(XOR)の演算子。累乗(**)と勘違いしないように。",
    "XOR": "排他的論理和。X ^ Yの場合、XとYのいずれか一方のみが真のときのみに真になる。",
    "排他的論理和": "X ^ Yの場合、XとYのいずれか一方のみが真のときのみに真になる。",

    "三項演算子": "条件式に応じて、２つの値のいずれかを返す条件演算子のこと",

    "アルゴリズム": "問題を解く手順",

    "機械語": "コンピュータのマイクロプロセッサ（CPU）が直接解釈・実行できる命令コードのこと",

    "定数": "ある特定の数値やデータに名前を与えたもの。変更はできない。",
    "変数": "データを一時的に記憶しておくための領域に固有の名前を付けたもの。",

    "スコープ": "変数名を参照できる範囲のこと。",
    "参照": "変数名からその値を得ること。",
    "グローバル変数": "プログラム中、どこのコードからでも参照できる変数のこと。便利だが、バグの元になりやすい。",
    "ローカル変数": "関数やメソッドの内部からしか参照できない変数のこと。",

    "関数": "数学の関数を模したサブルーチンで引数に対し処理し、結果を返すもの。",
    "サブルーチン": "特定の機能や処理をひとまとまりにした小プログラムで、他のプログラムから呼び出して実行できるもの",
    "戻り値": "関数やメソッドが処理を終えるときに、呼び出し元に対して渡すデータのこと。return文から返される。",
    "返り値": "関数やメソッドが処理を終えるときに、呼び出し元に対して渡すデータのこと。return文から返される。",
    "ビルトイン関数": "あらかじめ用意された関数のこと。",
    "ユーザ定義関数": "ユーザが定義した関数のこと。",
    "標準ライブラリ関数": "ビルトイン関数ではないが、標準的に提供されるユーザ定義関数のこと。",
    "入出力": "入力と出力のこと。I/Oとも。",
    "浮動小数点数": "コンピュータにおける数値の表現形式の一つで、小数点以下の値を含む数値の表現法として最も広く利用されている。",
    "単精度浮動小数点数": "32ビット長の浮動小数点数を格納できる数値のこと。floatとも。",
    "倍精度浮動小数点数": "64ビット長の浮動小数点数を格納できる数値のこと。doubleとも。",
    "文字列": "文字を並べたデータのこと。",
    "データ": "何かを文字や符号、数値などのまとまりとして表現したもの。",
    "データ構造": "データの集まりをプログラムで扱いやすいようにまとめたもの。",
    "タプル": "順序付けられた複数の要素で構成されるデータ構造のこと。数学に由来。",
    "配列": "複数のデータを連続的に並べたデータ構造のこと。効率が良い。",
    "多次元配列": "配列の要素に配列が入った入れ子状の配列のこと。",
    "二次元配列": "",
    "動的配列": "配列の長さが固定的されておらず、実行時に要素を追加、削除できる配列のこと。",
    "可変長配列": "配列の長さが固定的されておらず、実行時に要素を追加、削除できる配列のこと。",
    "添字": "配列に格納された個々の要素の位置を示す値のこと。数列の添字に由来。インデックスとも。",
    "インデックス": "配列に格納された個々の要素の位置を示す値のこと。数列の添字に由来。",
    "イテレータ": "配列のようなデータ構造の要素を順に走査していく繰り返し処理を簡潔に記述できるオブジェクトのこと。",
    "連想配列": "Pythonの辞書に相当するデータ構造のこと",
    "リスト": "複数のデータを順序を付けて格納するデータ構造のこと",
    "プレフィックス": "文字列や番号の先頭に付加して特定の意味を付け加える要素のこと。接頭辞とも。",
    "サフィックス": "文字列や番号の先頭に付加して特定の意味を付け加える要素のこと。接尾辞とも。",
    "基数": "位取り記数法で数値を書き記す際に各桁の重み付けの基本となる数で、位が上がる毎に何倍になるかを表す。",
    "リテラル": "ソースコード上で、特定のデータ型の値を直に記載したもの",
    "即値": "ソースコード中に直に書き込まれたデータのこと",
    "書式": "文書や書類の定められた様式やテンプレート",
    "フォーマット": "形式、書式、様式、体裁、型、構成などの意味を持つ",
    "テンプレート": "鋳型、雛型、定型書式などの意味を持つ英単語。",
    "インデント": "字下げのこと。文の行頭に空白を挿入して読みやすくすること。Pythonのようにインデントによってプログラムの構造を記述する。",
    "マジックナンバー": "ソースコードに直書きされた数値。その意味や意図が記述した本人以外わからなくなる恐れあり。",
    "NaN": "数値として表せない数値。非数とも。",

    "オブジェクト": "互いに密接に関連するデータと手続き（処理手順）をひとまとまりにしたもののこと。",
    "クラス": "オブジェクト指向プログラミングにおけるオブジェクトの雛型のこと。",
    "インスタンス": "あらかじめ定義されたクラスなどをメインメモリ上に展開して処理・実行できる状態にした実体のこと。",
    "フィールド": "オブジェクトの持つ固有のデータのこと。メンバ変数やプロパティとも",
    "メソッド": "各オブジェクトに属する処理や操作のこと。",
    "カプセル化": "外部に対して必要な情報のみ提供し、外から直に参照や操作する必要のないプロパティやメソッドを秘匿すること。",
    "ペイロード": "送受信されるデータのパケットのうち、宛先などの制御情報を除いたデータ本体のこと",
    "パディング": "データの長さを一定にするため前後に挿入される余白や無意味なデータのこと。",
    "ゼロパディング": "数値を文字として表示する際に、固定帳の桁数に合わせて左右に「0」を追加すること。",
    "固定長": "データや要素、領域などの長さがあらかじめ決まって変化しないこと。対義語は「可変長」",
    "可変長": "データや要素、領域などの長さが実行時に変化させられること。",
    "引数": "関数やメソッドなどを呼び出すときに渡すデータのこと。",
    "パラメータ": "ソフトウェアやシステムの挙動に影響を与える外部から与えられるデータのこと。",
    "仮引数": "関数やメソッドが呼び出し元から渡された値を受け取るために宣言された変数のこと。",
    "実引数": "関数やメソッドを呼び出す際に実際に引き渡される値や変数のこと。",
    "可変長引数": "あらかじめ数が固定されてなく、任意個の引数を受け取れること",
    "ステップ数": "コンピュータプログラムの規模を測る指標の一つ。実質処理を行っているソースコード行数のこと。",
    "API": "あるサービスを外部のプログラムから呼び出して利用できる規約のこと。",
    "デバッグ": "コンピュータプログラムに潜む欠陥を探し出して取り除くこと。",
    "バグ": "はプログラムに含まれる誤りのこと。必ずある。",
    "バグる": "意図しない奇妙な挙動を示すこと。",
    "コンパイル": "ソースコードをコンピュータが実行可能な形式に変換すること。",
    "コンパイラ": "ソースコードをコンピュータが実行可能な形式に変換するツールのこと。",
    "スクリプト言語": "コンパイルなしで実行できる軽量なプログラミング言語のこと。",
    "プラットフォーム": "あるソフトウェアを動作させるのに必要な土台となる装置やソフトウェア、サービスのこと。",
    "クロスプラットフォーム": "あるソフトウェアを複数の異なる仕様の機種やOSで同じように動作させられること。",
    "VM": "ソフトウェアで実現されたコンピュータやマイクロプロセッサの動作を模した仮想的なコンピュータのこと。",
    "仮想マシン": "ソフトウェアで実現されたコンピュータやマイクロプロセッサの動作を模した仮想的なコンピュータのこと。",
    "インタプリタ": "ソースコードをコンピュータが解釈・実行できる形式に変換しながら実行するソフトウェアのこと。",
    "動的": "プログラムの実行中に状態や構成が決まること。対義語は「静的」",
    "静的": "プログラムの実行前に状態や構成が決まること。対義語は「動的」",
    "オーバーヘッド": "目的の処理を行うために発生する余分な処理やコストのこと。",
    "動作環境": "ソフトウェアが動作するハードウェアやOSの構成や設定のこと",
    "環境": "ソフトウェアが動作するハードウェアやOSの構成や設定のこと",
    "ビルド": "ソースコードなどを元に実行可能ファイルや配布パッケージを作成すること",
    "デプロイ": "開発したソフトウェアを実際の運用環境に配置・展開して実用に提供すること",
    "ポーティング": "あるシステムで動作するよう開発されたソフトウェアを、異なる仕様や設計のシステムで動作するように作り変えること。",
    "アルゴリズム": "ある特定の問題を解く手順を、単純な計算や操作の組み合わせとして明確に定義したもの。",
    "エラー": "プログラムの実行を継続できない致命的な支障のこと。（頑張って取り除こう！）",
    "ランタイムエラー": "コンピュータプログラムの実行時に発生するエラーのこと。",
    "コンパイル": "プログラミング言語で書かれたコンピュータプログラム（ソースコード）を解析し、コンピュータが直接実行可能な形式のプログラム（オブジェクトコード）に変換すること。",
    "ライブラリ": "ある機能を持ったプログラムを利用できるように部品化し、集めたプログラムのこと。",
    "ファイル": "ストレージなどにデータを記録する際の最小の記録単位となるデータのまとまり。",
    "ファイル名": "コンピュータのストレージ上に保存されたファイルの名前",
    "拡張子": "ファイル名のうち、「.」で区切られた右側の部分でファイルの種類を表す",
    "ファイルシステム": "ストレージの記録状態を管理・制御し、ファイル単位でデータ操作可能にするOSの機能のこと",
    "ディレクトリ": "複数のファイルをまとめて分類できる名前の付いた保管場所のこと。フォルダとも。",
    "フォルダ": "複数のファイルをまとめて分類できる名前の付いた保管場所のこと。ディレクトリとも。",
    "カレントディレクトリ": "実行中のソフトウェアが現在ファイル操作をできるディレクトリのこと",
    "パス": "コンピュータシステム内で特定のリソースの位置を表す文字列のこと",
    "ファイルパス": "ストレージ内のファイルやディレクトリの位置を表す文字列のこと",
    "相対パス": "現在位置からの相対的な位置によってパスを記述する記法のこと。",
    "絶対パス": "階層構造のルートからの位置によってパスを記述する記法のこと。",
    "ストレージ": "永続的にデータを保存できる記憶装置のこと。ハードディスクやSSD、USBメモリなど。",
    "シェル": "利用者からのコマンドを受け付けて結果を提示を行うOSの機能のこと",
    "CLI": "コマンドベースのユーザーインターフェースのこと",
    "プロンプト": "シェルにおいて入力を受け付けられる状態であることを示すメッセージのこと",
    "マクロ": "ソースコード中に繰り返し登場する特定の記述を、別の短い記述に置き換える機能のこと",
    "プリプロセッサ": "ある中心的な処理を行うプログラムに対して、その前処理を行うプログラムのこと。",
    "文字コード": "文字や記号を扱うために割り当てられた番号のこと。",
    "Unicode": "世界中の様々な言語の文字を同時に使えるように規格化された文字コードのこと。ユニコードと読む。",
    "ユニコード": "世界中の様々な言語の文字を同時に使えるように規格化された文字コードのこと。",
    "UTF-8": "UnicodeをASCIIコードと互換のある形式で表現できる文字コードのこと。",
    "互換のある形式": "同時に扱っても不具合が生じない形式のこと",
    "バイト": "8ビットのことを表す情報量の単位のこと",
    "バイト列": "任意のビットパターンからなるバイト単位の長さを持つデータの集合。",
    "エンディアン": "多バイトデータを記録するときの順序のこと。ビックエンディアンとリトルエンディアンがある。",
    "ビッグエンディアン": "多バイトデータを最上位から下位への順序で扱う方式。",
    "リトルエンディアン": "多バイトデータを最下位から上位への順序で扱う方式。",
    "スラッシュ": "右上から左下への斜め線「/」文字のこと。",
    "バックスラッシュ": "左上から右下への斜め線「\」のこと。スラッシュの逆向き。円マークが代わりに使われることもある。",
    "ASCII文字": "ASCII(American Standard Code for Information Interchange)規格の文字。アスキーと読む。",
    "制御文字": "通信制御などの制御に用いるように割り当てられた文字コード。タブや改行が該当する。",
    "エスケープ文字": "制御文字など印字しにくい文字コードを数値などで表記する記法のこと。",
    "エスケープシーケンス": "制御文字など印字しにくい文字コードを数値などで表記する記法のこと。",
    "EOF": "ファイルの終端のこと。",
}


def get_desc(text: str):
    if text in DESC:
        return DESC[text]
    kogi_log('undefined_desc', desc=text)
    return None
