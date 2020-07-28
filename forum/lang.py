# task state control
def showstatebylang(word, lang='zh-tw'):
    if lang == 'zh-tw':
        dic_state = {
            'open': '接受取件',
            'accept': '有人取件',
            'wait_confirm': '待發案人確認',
            'wait_pickup': '待取貨',
            'shipping': '運送中',
            'arrived': '物品抵達',
            'score': '互給評價',
            'finish': '結案'
        }
        dic_base_html = {

        }
    if word in dic_state:
        return dic_state[word]
    else:
        return ''