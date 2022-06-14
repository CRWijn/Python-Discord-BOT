import random
import os

class start_hangman:

    def __init__(self):
        self.hangman_matrix = [
            ['-', '-', '-', '-', '-', '-'],
            [' ', '|', ' ', ' ', ' ', '|'],
            [' ', '|', ' ', ' ', ' ', 'O'],
            [' ', '|', ' ', '/', '|', '\\'],
            [' ', '|', ' ', ' ', ' ', '|'],
            [' ', '|', ' ', '/', ' ', '\\'],
            [' ', '|', ' ', ' ', ' ', ' '],
            ['-', '-', '-', '-', '-', '-']
            ]

        self.reset()

    def reset(self):
        self.output_matrix = [
            [' ', ' ', ' ', ' ', ' ', ' '],
            [' ', ' ', ' ', ' ', ' ', ' '],
            [' ', ' ', ' ', ' ', ' ', ' '],
            [' ', ' ', ' ', ' ', ' ', ' '],
            [' ', ' ', ' ', ' ', ' ', ' '],
            [' ', ' ', ' ', ' ', ' ', ' '],
            [' ', ' ', ' ', ' ', ' ', ' '],
            [' ', ' ', ' ', ' ', ' ', ' ']
            ]

        self.player = ''
        self.errors_made = 0
        self.guessed_letters = []
        self.word = self.get_word()
        self.word_status = []
        for ndx in range(0, len(self.word)):
            self.word_status.append('-')
                        
    def __str__(self):
        return_string = ''
        for row in self.output_matrix:
            output_line = '';
            for col in row:
                output_line += col;
            return_string += output_line + "\n"
        return_string += 'Guessed Letters: ' + ", ".join(self.guessed_letters) + "\n"
        return_string += 'Your Word: ' + "".join(self.word_status) + "\n"
        return return_string

    def get_word(self):
        with open('words.txt') as f:
            num_words = sum(1 for line in f)
            word_int = random.randint(0, num_words-1)
            f.seek(0)
            for ndx, content in enumerate(f):
                if ndx == word_int:
                    return content.strip()

    def update_output(self, is_error, inp, word = ''):
        
        error_dict = {
            1: [(7, 0), (7, 1), (7, 2), (7, 3), (7, 4), (7, 5)],
            2: [(6, 1), (5, 1), (4, 1), (3, 1), (2, 1), (1, 1)],
            3: [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5)],
            4: [(1, 5), (2, 5)],
            5: [(3, 4), (4, 5)],
            6: [(3, 3), (3, 5)],
            7: [(5, 3), (5, 5)]
            }
        
        if is_error:
            for coord in error_dict[self.errors_made]:
                    self.output_matrix[coord[0]][coord[1]] = self.hangman_matrix[coord[0]][coord[1]]
            if word == '' and self.errors_made < 7:
                self.guessed_letters.append(inp)
        else:
            if word != '':
                for ndx, letter in enumerate(self.word):
                    self.word_status[ndx] = letter
            else:
                for ndx, letter in enumerate(self.word):
                    if letter == inp:
                        self.word_status[ndx] = letter

