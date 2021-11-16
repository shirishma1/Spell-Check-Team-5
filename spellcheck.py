import re  # Regular Expressions
from collections import Counter
import string
import ast
from flask import Flask, jsonify, render_template, request

def read_file():
    words = []
    for i in range(1, 15):
        with open('english_list_files\english_list_'+str(i)+'.txt', 'r', encoding='utf-8') as file:
            print(i)
            text = ''
            for line in file:
                text += line
                words += ast.literal_eval(text)
    return words

def split(word):
    return[(word[:i], word[i:]) for i in range(len(word) + 1)]

def delete(word):
    return [l + r[1:] for l, r in split(word) if r]

def swap(word):
    return [l + r[1] + r[0] + r[2:] for l, r in split(word) if len(r) > 1]

def replace(word):
    letters = string.ascii_lowercase
    return [l + c + r[1:] for l, r in split(word) if r for c in letters]

def insert(word):
    letters = string.ascii_lowercase
    return [l + c + r for l, r in split(word) for c in letters]

def level_one_edit(word):
    return set(delete(word) + swap(word) + replace(word) + insert(word))

def level_two_edit(word):
    return set(e2 for e1 in level_one_edit(word) for e2 in level_one_edit(e1))

def correct_spelling(word, text, word_probability):
    guesses = []
    if word in text:
        return guesses
    suggestions = level_one_edit(word) or level_two_edit(word) or [word]
    best_guesses = [w for w in suggestions if w in text]
    return [(w, word_probability[w]) for w in best_guesses]

words = read_file()
unique_words = set(words)
word_count = Counter(words)
total_word_count = float(sum(word_count.values()))
word_probability = {word: word_count[word] / total_word_count for word in word_count.keys()}

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/', methods=['GET', 'POST'])
def check():
    if request.method == "POST":
        text = ''
        text = request.form['wrongwords']
        iwords = text.strip().lower().split()
        guesses = []
        r = []
        for word in iwords:
            guesses = correct_spelling(word, unique_words, word_probability)
            toporder = sorted(guesses, key=lambda x: x[1], reverse=True)[:len(guesses)]  # arranging suggestions in decreasing order
            length = len(toporder)
            if length > 5:
                length = 5
            topfive = sorted(toporder, key=lambda x: x[1], reverse=True)[:length]  # fiding top five suggestions
            print(topfive)
            
            if len(topfive) != 0:
                # breaking guesses list to 2 lists
                cor_word, num = map(list, zip(*topfive))
                r.append(cor_word[0])
            else:
                r.append(word)
                cor_word = ''

            res = " "
            res = res.join(r)

        return jsonify({'correct_words': res, 'top_suggestions': cor_word})

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
