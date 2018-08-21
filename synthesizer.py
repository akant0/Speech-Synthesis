#11 November 2017
# Requires a folder "monophones" with wav files for each monophone (not uploaded, as it belongs to the University of Edinburgh)
# Example1: -p "HELLO. i was born {22/01} with {3.14} or, 344 cats"
# Example 2: -p "A rose by any other name would smell as sweet"
# Features: allows for volume control
# Applies small silence for punctuation
# Text normalization for numbers and dates
# --spell mode synthesizes text spelled out 
# emphasis can be applied to a word with {word}
import os
import simpleaudio
import numpy as np
import argparse
from nltk.corpus import cmudict
import re
import datetime
import nltk
nltk.download('cmudict')
parser = argparse.ArgumentParser(
    description='A basic text-to-speech app that synthesises an input phrase using monophone unit selection.')
parser.add_argument('--monophones', default="./monophones", help="Folder containing monophone wavs")
parser.add_argument('--play', '-p', action="store_true", default=False, help="Play the output audio")
parser.add_argument('--outfile', '-o', action="store", dest="outfile", type=str, help="Save the output audio to a file",
                    default=None)
parser.add_argument('phrase', nargs=1, help="The phrase to be synthesised")

# Arguments for extensions
parser.add_argument('--spell', '-s', action="store_true", default=False,
                    help="Spell the phrase instead of pronouncing it")
parser.add_argument('--volume', '-v', default=None, type=float,
                    help="A float between 0.0 and 1.0 representing the desired volume")
args = parser.parse_args()

class Synth(object):
    def __init__(self, wav_folder):
        self.phones = {}
        self.get_wavs(wav_folder)

    def get_wavs(self, wav_folder):
        """Searches through folder for wav audio files.
        Creates dict. with 'phone':audio object (made from file)"""
        p = {}
        for root, dirs, files in os.walk(wav_folder, topdown=False):
            for file in files:
                if file[-3:] == 'wav' and file[0] != '.':
                    name = re.sub(r'\.wav', '', file)
                    aud = simpleaudio.Audio()
                    aud.load(args.monophones + '/' + file)
                    p[name] = aud
                    self._Rate = aud.rate
        self.phones = p

    def expand_date(self, str_date):
        """Expands date string input written in form DD/MM, DD/MM/YY or DD/MM/YYYY, to words.
        Returns expanded form."""
        ordinal = {1: 'first', 2: 'second', 3: 'third', 4: 'fourth', 5: 'fifth', 6: 'sixth', 7: 'seventh', 8: 'eighth',
                   9: 'ninth', 10: 'tenth', 11: 'eleventh', 12: 'twelfth', 20: 'twentieth', 30: 'thirtieth',
                   31: 'thirty first'}
        # Matches DD/MM/YYYY or D/MM/YYYY, ie 22/01/1980.
        # Year treated as two numbers and combines, ie 'nineteen eighty'.
        if re.match(r"[0-3]?[0-9]\/\d\d\/\d\d\d\d", str_date):
            date = datetime.datetime.strptime(str_date, "%d/%m/%Y").date()
            Year = date.strftime("%Y")
            yearP1 = self.expand_num(Year[:2])
            yearP2 = self.expand_num(Year[2:])
            year = yearP1 + ' ' + yearP2
        # Matches DD/MM/YY or D/MM/YY, ie 22/01/80.
        # Assumes in 1900s. '80'-> 'nineteen eighty'
        elif re.match(r"[0-3]?[0-9]\/\d\d\/\d\d", str_date):
            date = datetime.datetime.strptime(str_date, "%d/%m/%y").date()
            year = date.strftime("%y")
            year = self.expand_num(year)
            year = 'nineteen' + ' ' + year
        # Matches DD/MM or D/MM. Year set to nothing.
        elif re.match(r"[0-3]?[0-9]\/\d\d", str_date):
            date = datetime.datetime.strptime(str_date, "%d/%m").date()
            year = ''
        # Expands day to ordinal form
        Day = date.strftime("%d")
        Month = date.strftime("%B")
        if Day[0] == '0':
            newDay = ordinal[int(Day[1])]
        else:
            str_day = Day[:2]
            day = int(str_day)
            if day in range(1, 13) or day in [20, 30, 31]:
                newDay = ordinal[day]
            elif day in range(13, 20):
                newDay = self.expand_num(str(day)) + 'th'
            else:
                dayP1 = self.expand_num(str_day[0] + '0')
                dayP2 = ordinal[int(str_day[1])]
                newDay = dayP1 + ' ' + dayP2
        # Final version of day, ie 'the twenty second of January'
        finalDay = 'the' + ' ' + newDay + ' ' + 'of '
        if year == '':
            Final = finalDay + Month
        # Final form of date: the ORDINAL of MONTH YEAR, ie 'the twenty second of january nineteen eighty'
        else:
            Final = finalDay + Month + ' ' + year
        return Final

    def expand_num(self, str_num):
        """Expands numbers (string input) into words.
        Returns expanded form.
        Uses dictionaries of numbers below: """
        ones = {0: 'zero', 1: 'one', 2: 'two', 3: 'three', 4: 'four', 5: 'five', 6: 'six', 7: 'seven', 8: 'eight',
                9: 'nine'}
        teens = {11: 'eleven', 12: 'twelve', 13: 'thirteen', 14: 'fourteen', 15: 'fifteen', 16: 'sixteen',
                 17: 'seventeen', 18: 'eighteen', 19: 'nineteen'}
        tens = {10: 'ten', 20: 'twenty', 30: 'thirty', 40: 'forty', 50: 'fifty', 60: 'sixty', 70: 'seventy',
                80: 'eighty', 90: 'ninety'}
        # Expands numbers with decimals, ie 3.14 -> 'three point one four'
        if '.' in str_num:
            new = []
            L = [i for i in str_num]
            for i in L:
                if i == '.':
                    new.append('point')
                else:
                    new.append(ones[int(i)])
            return ' '.join(new)
        # Below, expands all other numbers using dictionaries above:
        num = float(str_num)
        if num < 10:
            num = ones[num]                                         # i.e '9' -> 'nine'
            return num
        if num == 10:
            return 'ten'
        if num in range(11, 20):
            num = teens[int(num)]                                   # '11' -> 'eleven'
            return num
        if 19 < num < 100:
            if str(num)[1] == '0':                                  # i.e 20 or 30
                num = tens[num]                                     # '20' -> 'twenty'
                return num
            else:
                first = int(num / 10) * 10                          # i.e 49: first is 'forty', next is 'nine'
                next = int(str(num)[1])
                num = tens[first] + ' ' + ones[next]
                return num
        if num > 99:
            num = int(num)
            if str(num)[1] == '0' and str(num)[2] == '0':           # i.e '100' -> 'one hundred'
                first = int(str(num)[0])
                num = ones[first] + ' hundred '
                return num
            elif int(str(num)[1:]) < 10:                            # i.e '101', '509', etc.
                first = int(str(num)[0])
                sec = int(str(num)[-1])
                num = ones[first] + ' hundred and ' + ones[sec]     # '101'-> 'one hundred and one'
                return num
            elif int(str(num)[1:]) == 10:                           # i.e '110', '210'...
                first = int(str(num)[0])
                sec = int(str(num)[1:])
                num = ones[first] + ' hundred and ' + tens[sec]     # '110'-> 'one hundred ten'
                return num
            elif int(str(num)[1:]) < 20:                            # i.e '112', '219', etc.
                first = int(str(num)[0])
                sec = int(str(num)[1:])
                num = ones[first] + ' hundred and ' + teens[sec]    # '112'-> 'one hundred and twelve'
                return num
            elif int(str(num)[1:]) in range(20, 100):               # i.e '120', '999'
                first = int(str(num)[0])
                if str(num)[2] == '0':                              # i.e '120', '990'
                    sec = int(str(num)[1:])
                    num = ones[first] + ' hundred ' + tens[sec]     # '120'-> 'one hundred twenty'
                    return num
                else:
                    # Else all others, i.e '342', '999', etc.
                    sec1 = (int(num / 10) * 10)
                    sec2 = int(str(sec1)[1:])
                    next = int(str(num)[2])
                    # '999'-> 'nine hundred and ninety nine':
                    num = ones[first] + ' hundred and ' + tens[sec2] + ' ' + ones[next]
                    return num

    def add_break(self, audioObj, lengthB):
        """Adds a break to audio object.
        Input an audio object and break time in ms.
        Returns new audio object with break."""
        if lengthB == 250:
            lengthB = int(audioObj.rate) / 4
        else:
            lengthB = int(audioObj.rate) / 2
        empty = np.zeros(int(lengthB), dtype=audioObj.nptype)
        newData = np.append(audioObj.data, empty).astype(np.int16)
        newAudio = simpleaudio.Audio(rate=self._Rate)
        newAudio.data = newData
        return newAudio

    def conc_audio(self, audio_objects):
        """Combines audio objects from input list.
        Input is a list of audio objects.
        Returns new audio object."""
        array = []
        for obj in audio_objects:
            array = np.append(array, obj.data).astype(np.int16)
        # Create a new object to return
        new_object = simpleaudio.Audio(rate=self._Rate)
        new_object.data = array
        return new_object

    def get_phone_seq(self, phrase):
        """Creates the synthesized audio object and applies the appropriate args (-v, -p, -s, -o, etc.)
        Input is the phrase string, tokenized.
        Tokens put into dictionary with ultimate format:
            ('token', index):[Loudness?, Break amount(250or500), Number?, []*, []**]
                *empty list will later hold audio object
                **empty list will later hold phones
        How? Each token put through process:
        1. marked for loudness changes if brackets 2. marked with break amounts based on punctuation
        3. if a number, expanded 4. If a date, expanded 5. normalized 6. put into dictionary with all this info
        Note: each expanded number/word treated as unit in dict for later processing so that,ie {234} or {22/01} will
        have an increased loudness on everything in expanded form.
        Output: depends on args. Audio can be played, volume altered, spelled out, output into a file.
         """

        # Helper functions:
        def phones_to_Dict(L_word, index, one=True):
            """Adds phone sequence to the feature dictionary.
            Input: 1. a list of word(s) (if NSW in expanded form), else one word. 2. Its index in the sentence.
            3. marker if one word or multiple
            """
            entries = cmudict.dict()
            for word in L_word:
                if len(word.split()) == 1:
                    try:
                        options = entries[word]
                    except KeyError:
                        raise ValueError(word + ' is not in our Dictionary. Please try another word.')
                    if len(options) > 1:
                        option1 = options[0]
                    else:
                        option1 = options[0]
                    wordphones = []
                    for item in option1:
                        item = item.lower()
                        item = re.sub(r'\d+', '', item)
                        wordphones.append(item)
                    if one is True:
                        features[(word, index)][4].append(wordphones)
                    else:
                        features[(' '.join(L_word), index)][4].append(wordphones)
                else:
                    phones_to_Dict(word.split(), index, one=False)

        # check if a token is a number
        def is_num(token):
            try:
                int(token)
                return True
            except ValueError:
                return False

        # vs has a decimal
        def is_float(token):  # can be float or int
            try:
                float(token)
            except ValueError:
                return False
            return True

        # for Spelling- split phrase into letters and later pronounce so
        L = ''
        if args.spell is True:
            phrase = re.sub(r'\s+', '', phrase)
            phrase = list(phrase)
            for i in phrase:
                L += i
                L += ' '
            phrase = L

        # Main part of function starts here:
        phrase = phrase.split()
        words = []
        features = {}
        # Token's index in sentence
        index = 0
        # Mark special features based on context, expands NSWs (numbers, dates)
        for token in phrase:
            Loud = None
            Break = None
            Num = False
            # Loudness
            if token[0] == '{' and token[-1] == '}':
                Loud = True
                token = re.sub(r'[{}]', '', token).lower()
            # Breaks
            if token[-1] == ',':
                Break = 250
            if token[-1] in ['.', '!', '?']:
                Break = 500
            # Expand/replace numbers
            if is_num(token) or is_float(token):
                Num = True
                token = self.expand_num(token)
            # Expand dates
            if re.match(r"[0-3]?[0-9]\/\d\d(\/\d\d(\d\d)*)*", token):
                token = self.expand_date(token)
            # Normalize token(s)
            token = re.sub(r'[^A-Za-z\s]', '', token).lower()
            # Put in dict: loud?, break amt, num?, later audio file, phones
            features[(token, index)] = [Loud, Break, Num, [], []]
            words.append(token)
            phones_to_Dict([token], index)
            index += 1
        #print(features)

        # Add audio objects to dictionary
        for word in features.values():
            word[4] = [item for sublist in word[4] for item in sublist]
            auds = []
            for phone in word[4]:
                try:
                    auds.append(self.phones[phone])
                except KeyError:
                    raise KeyError('We do not have this sound. Please try another input.')
            word[3] = self.conc_audio(auds)
            if word[0] is True:
                word[3].rescale(1.00)
            if word[1] == 250:
                word[3] = self.add_break(word[3], 250)
            if word[1] == 500:
                word[3] = self.add_break(word[3], 500)
            # To make -spell say letters more pronounced. Sounds eerie though:
            #if args.spell is not None:
            #    word[3].time_stretch_fft(.5)

        # Create final audio object
        final = []
        index = 0
        for item in words:
            final.append(features[(item, index)][3])
            index += 1
        # print(features) # see what the final dictionary looks like
        Final = self.conc_audio(final)

        # Volume Control
        if args.volume is not None:
            amount = args.volume
            Final.rescale(amount)

        # Play
        if args.play is True:
            Final.play()

        if args.outfile is not None:
            Final.save(args.outfile)

if __name__ == "__main__":
    import sys

    S = Synth(wav_folder=args.monophones)
    phone_seq = S.get_phone_seq(args.phrase[0])
