from flask import Flask, request, jsonify
from flask_cors import CORS
import json

# Trie implementation
class TrieNode:
    def __init__(self):
        self.children = {}
        self.original_words = set()

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        for i in range(len(word)):
            self._insert_suffix(word[i:], word)

    def _insert_suffix(self, suffix, original_word):
        node = self.root
        for char in suffix:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
            node.original_words.add(original_word)

    def get_closest_word(self, word):
        min_distance = float('inf')
        closest_word = None

        similar_prefix_words = self._find_similar_prefix_words(word)

        if similar_prefix_words:
            for original_word in similar_prefix_words:
                distance = self._calculate_edit_distance(word, original_word)
                if distance < min_distance:
                    min_distance = distance
                    closest_word = original_word

        return closest_word

    def _find_similar_prefix_words(self, word):
        node = self.root
        similar_prefix_words = set()
        for char in word:
            if char not in node.children:
                return similar_prefix_words
            node = node.children[char]
            similar_prefix_words.update(node.original_words)
        return similar_prefix_words

    def _calculate_edit_distance(self, word1, word2):
        m, n = len(word1), len(word2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]

        for i in range(m + 1):
            dp[i][0] = i
        for j in range(n + 1):
            dp[0][j] = j

        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if word1[i - 1] == word2[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1]
                else:
                    dp[i][j] = min(dp[i - 1][j - 1], dp[i - 1][j], dp[i][j - 1]) + 1

        return dp[m][n]

# Load data
with open('/Users/pushpendrachoudhary/Desktop/8th-Semester/MTP-2/Keyword-Searching/Dictionary_Database/DB.json', 'r') as file:
    data = json.load(file)

words = [entry["word"].lower() for entry in data]

# Initialize Trie
trie = Trie()
for word in words:
    trie.insert(word)

# Initialize Flask app
app = Flask(__name__)
CORS(app, supports_credentials=True, origins="http://localhost:4200", methods=["GET", "POST", "OPTIONS"]) 

@app.route('/get_suggestions', methods=['OPTIONS', 'POST'])
def handle_get_suggestions():
    if request.method == 'OPTIONS':
        # Respond to preflight request
        response = jsonify({})
    else:
        # Handle POST request
        data = request.get_json()
        input_word = data.get('input_word')

        if input_word:
            suggestions = trie.get_closest_word(input_word)
            response = jsonify({'suggestions': suggestions})
        else:
            response = jsonify({'error': 'Input word not provided'}), 400  # This line creates a tuple

    return response

if __name__ == '__main__':
    app.run(debug=True)