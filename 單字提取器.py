import json
import time
import requests


def fetch_multi_meanings(word):
    """ 調用 Google Translate 抓取多重常用語意 """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=zh-TW&dt=t&dt=at&q={word}"

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            main_trans = data[0][0][0]

            others = []
            if len(data) > 5 and data[5] is not None:
                for entry in data[5][0][2]:
                    others.append(entry[0])

            unique_meanings = []
            all_raw = [main_trans] + others
            for m in all_raw:
                if m not in unique_meanings and len(m) <= 5:
                    unique_meanings.append(m)

            return ", ".join(unique_meanings[:3])
        return "翻譯失敗"
    except Exception as e:
        return f"連線錯誤"


def fetch_word_info(word):
    """ 抓取英英字典定義與例句 """
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
    headers = {'User-Agent': 'Mozilla/5.0'}

    try:
        res = requests.get(url, headers=headers, timeout=10)
        ipa = "[N/A]"
        en_def = word
        example = f"The {word} is very important."

        if res.status_code == 200:
            data = res.json()
            ipa = data[0].get('phonetic', '[N/A]')
            en_def = data[0]['meanings'][0]['definitions'][0]['definition']
            for meaning in data[0]['meanings']:
                for d in meaning['definitions']:
                    if 'example' in d:
                        example = d['example']
                        break

        cn_meanings = fetch_multi_meanings(word)
        short_en_def = " ".join(en_def.split()[:6]) + "..."

        print(f"  [SUCCESS] {word} -> {cn_meanings}")
        return {
            "w": word,
            "i": ipa,
            "d": short_en_def,
            "dt": cn_meanings,
            "s": example
        }
    except:
        print(f"  [ERROR] 無法抓取 {word}")
        return {"w": word, "i": "[N/A]", "d": "N/A", "dt": "N/A", "s": "N/A"}


def build_database():
    print(">>> TITAN OMNI-ENGINE v3.0: BULK AUTO-PARSER <<<")
    final_db = {}
    current_unit = "未分類單元"

    try:
        with open('words.txt', 'r', encoding='utf-8') as file:
            lines = file.readlines()

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 🌟 核心智慧分類：如果這行開頭是 '#'，就把它當作新的單元名稱
            if line.startswith('#'):
                current_unit = line.replace('#', '').strip()
                if current_unit not in final_db:
                    final_db[current_unit] = []
                print(f"\n📂 建立新單元資料夾: [{current_unit}]")
                continue

            # 否則，把它當作單字，存入目前的單元中
            if current_unit not in final_db:
                final_db[current_unit] = []

            final_db[current_unit].append(fetch_word_info(line))
            time.sleep(1)  # 冷卻防封鎖

        with open('TitanDB.json', 'w', encoding='utf-8') as out_file:
            json.dump(final_db, out_file, ensure_ascii=False, indent=4)
        print(f"\n[DONE] 完美！所有單元已合併存入單一 TitanDB.json 檔案中。")

    except FileNotFoundError:
        print("[CRITICAL] 找不到 words.txt 檔案。")


if __name__ == "__main__":
    build_database()