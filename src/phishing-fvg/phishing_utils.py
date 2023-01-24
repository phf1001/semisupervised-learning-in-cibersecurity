import nltk
nltk.download('stopwords')
nltk.download('punkt')
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from num2words import num2words
import numpy as np




class Utils:

    def turn_lower_case(self, text):
        return np.char.lower(text)


    def remove_stop_words(self, data):

        stop_words = ( stopwords.words('english') + stopwords.words('spanish'))

        new_text = ''
        for w in data:
            if w not in stop_words and len(w) > 1:
                new_text = new_text + ' ' + w
        return new_text

    def remove_punctuation(self, data):
        symbols = "!\"#$%&()*+-./:;<=>?@[\]^_`{|}~\n"
        for i in range(len(symbols)):
            data = np.char.replace(data, symbols[i], ' ')
            data = np.char.replace(data, "  ", " ")
        data = np.char.replace(data, ',', '')
        return data

    

    def remove_apostrophe(self, data):
        return np.char.replace(data, "'", "")

        

    def stemming(self, data):
        stemmer= PorterStemmer()
        
        tokens = word_tokenize(str(data))
        new_text = ""
        for w in tokens:
            new_text = new_text + " " + stemmer.stem(w)
        return new_text


    def convert_numbers(self, data):
        tokens = word_tokenize(str(data))
        new_text = ""
        for w in tokens:
            try:
                w = num2words(int(w))
            except:
                a = 0
            new_text = new_text + " " + w
        new_text = np.char.replace(new_text, "-", " ")
        return new_text


    def preprocess(self, data):

        data = data.split()
        data = self.turn_lower_case(data)
        data = self.remove_punctuation(data)
        data = self.remove_apostrophe(data)
        data = self.remove_stop_words(data)

        return word_tokenize(str(data))

