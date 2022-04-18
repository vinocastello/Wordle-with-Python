"""
Wordle Clone using BeeWare
"""
from ctypes import alignment
from tkinter import CENTER
from tkinter.ttk import Style

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from toga.colors import rgb

import random

def all_letters(s: str) -> bool:
    return all(char.isalpha() for char in s)

def readfile(full_path: str) -> list[str]:
    with open(full_path) as f:
        lines: list[str] = f.read().splitlines()
        return lines

def get_freq(s: str) -> dict[str:int]:
    return {x: s.count(x) for x in set(s)}

class GuessObj:
    def __init__(self,new_guess):
        self.guess_input = toga.TextInput(style=Pack(flex=1))
        self.guess_box = toga.Box(style=Pack(direction=ROW, padding=5))
        self.guess_button = toga.Button('Guess',on_press=new_guess,style=Pack(padding=5))
        self.guess_label = toga.Label('Guess: ',style=Pack(padding=(0, 5)))
    def setup(self):
        self.guess_box.add(self.guess_label)
        self.guess_box.add(self.guess_input)

class GridObj:
    def __init__(self,num_rows,num_squares,row_padding,square_size):
        self.rows = [toga.Box(style=Pack(padding=row_padding,alignment=CENTER)) for i in range(num_rows)]
        self.squares = [[toga.Button('',on_press=None,style=Pack(width=square_size,height=square_size,color=rgb(255,255,255),alignment=CENTER,text_align=CENTER,flex=1,font_size = 15)) for i in range(num_squares)] for j in range(num_rows)]

    def setup_grid(self,num_rows,num_squares,side_padding,inner_padding,top_padding):
        for i in range(num_rows):
            for j in range(num_squares):
                if (j == 0):
                    self.squares[i][j].style.padding_left = side_padding
                    self.squares[i][j].style.padding_right = inner_padding
                elif (j == num_squares-1):
                    self.squares[i][j].style.padding_right = side_padding
                    self.squares[i][j].style.padding_left = inner_padding
                else:
                    self.squares[i][j].style.padding_left = inner_padding
                    self.squares[i][j].style.padding_right = inner_padding
                self.rows[i].add(self.squares[i][j])
        self.rows[0].style.padding_top = top_padding


class RestartObj:
    def __init__(self,reset_button,reset_padding,reset_height):
        self.restart_button = toga.Button('Restart',on_press=reset_button,style=Pack(padding=reset_padding,height=reset_height))

class WordleClone(toga.App):

    def startup(self):
        # Initializations
        file_path: str = str(self.paths.app)
        src: str = file_path[:len(file_path)-11]
        self.allowed_guesses: list[str] = readfile(src+'wordle-allowed-guesses.txt')
        self.answers: list[str] = readfile(src+'wordle-answers-alphabetical.txt')
        self.goal_index: int = random.randrange(0,len(self.answers))
        self.guess_count: int = 3
        self.goal_word: str = self.answers[self.goal_index]
        self.freq: dict[str:int] = get_freq(self.goal_word)
        self.win: bool = True

        main_box = toga.Box(style=Pack(direction=COLUMN))
        self.main_window = toga.MainWindow(title=self.formal_name,size=(640,640))

        self.Guess: GuessObj = GuessObj(self.new_guess)
        self.Grid: GridObj = GridObj(6,5,10,60)
        self.restart_box: RestartObj = RestartObj(self.reset_button,5,40)

        # setup
        self.Guess.setup()
        self.Grid.setup_grid(6,5,self.main_window.size[0]//2,5,5)
        
        alphabet_label = toga.Label('A B C D E F G H I J K L M N O P Q R S T U V W X Y Z',style=Pack(text_align=CENTER))

        main_box.add(self.Guess.guess_box)
        main_box.add(self.Guess.guess_button)
        main_box.add(alphabet_label)

        # add rows to main_box
        for i in range(6):
            main_box.add(self.Grid.rows[i])

        main_box.add(self.restart_box.restart_button)

        
        self.main_window.content = main_box
        self.main_window.show()

    def new_guess(self,widget):
        self.Guess.guess_input.value = self.Guess.guess_input.value.lower()
        if(len(self.Guess.guess_input.value) != 5):
            self.main_window.info_dialog('Input Error','Your guess is not 5 letters long')
            self.Guess.guess_input.clear()
        elif (all_letters(self.Guess.guess_input.value) == False):
            self.main_window.info_dialog('Input Error','Your guess has numbers in it')
            self.Guess.guess_input.clear()
        elif (self.Guess.guess_input.value != self.goal_word and self.Guess.guess_input.value not in self.allowed_guesses):
            self.main_window.info_dialog('Input Error','Your guess is not included in the allowed list of guesses')
            self.Guess.guess_input.clear()
        else:
            self.win = self.Guess.guess_input.value == self.goal_word
            objs = self.main_window.content.children
            target_row = objs[self.guess_count].children
            upper_guess = self.Guess.guess_input.value.upper()
            self.color_squares(target_row,upper_guess)
            self.guess_count += 1
            self.isDone()
    

    def isDone(self):
        if(self.guess_count == 9 and self.win == False):
                self.defeat()
        elif (self.guess_count <= 9 and self.win == True):
            self.victory()
        else:
            self.Guess.guess_input.clear()

    def restart(self):
        self.guess_count = 3
        objs = self.main_window.content.children
        for i in range(3,9):
            row = objs[i].children
            for j in range(len(row)):
                row[j].label = ""
                row[j].style.background_color = rgb(255,255,255)
                row[j].refresh()
        self.Guess.guess_input.clear()
        self.win = True
        self.goal_index: int = random.randrange(0,len(self.answers))
        self.goal_word = self.answers[self.goal_index]

    def reset_button(self,widget):
        self.restart()

    def defeat(self):
        self.main_window.info_dialog('GAME OVER!',f'The correct answer is {self.goal_word}')
        self.restart()

    def victory(self):
        self.main_window.info_dialog('GAME FINISHED','CONGRATULATIONS! YOU GUESSED IT RIGHT!')
        self.restart()

    def color_squares(self,target_row,upper_guess):
        guess_freq: dict[str:int] = get_freq(self.Guess.guess_input.value)
        for i in range(len(target_row)):
                target_row[i].label = upper_guess[i]
                curr_letter: str = target_row[i].label.lower()
                if(curr_letter in self.goal_word):
                    if (curr_letter == self.goal_word[i]):
                        target_row[i].style.background_color = rgb(83,141,78) # green
                    else:
                        if(guess_freq[curr_letter] <= self.freq[curr_letter]):
                            target_row[i].style.background_color = rgb(180,160,60) # yellow
                        else:
                            target_row[i].style.background_color = rgb(58,58,60) # gray

                else:
                    target_row[i].style.background_color = rgb(58,58,60) # gray
                
                target_row[i].refresh()
        
def main():
    return WordleClone()
