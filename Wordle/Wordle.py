"""
Authors: Augusto Escudero and Joe Cox
Date: May 4, 2022
Description: A Python/tkinter implementation of wordle.
"""

# Imports
import random
import tkinter as tk
import tkinter.font as font
from enum import Enum
import time


class Wordy:
    def __init__(self):
        """ Initialize the game """
        # Constants
        self.WORD_SIZE = 5  # number of letters in the hidden word
        self.NUM_GUESSES = 6  # number of guesses that the user gets
        self.LONG_WORDLIST_FILENAME = "long_wordlist.txt"
        self.SHORT_WORDLIST_FILENAME = "short_wordlist.txt"

        self.PADDING = 10
        self.SPECIFY_ENTRY_WIDTH = 5

        self.started_game = False
        self.last_square = 0

        self.words_list_short = []
        self.words_list_long = []

        # Size of the frame that holds all guesses.  This is the upper left
        # frame in the window.
        self.PARENT_GUESS_FRAME_WIDTH = 750
        self.PARENT_GUESS_FRAME_HEIGHT = 500

        # Parameters for an individual letter in the guess frame
        # A guess frame is an individual box that contains a guessed letter.
        self.GUESS_FRAME_SIZE = 50  # the width and height of the guess box.
        self.GUESS_FRAME_PADDING = 3
        self.GUESS_FRAME_BG_BEGIN = 'white'  # background color of a guess box
        # after the user enters the letter,
        # but before the guess is entered.
        self.GUESS_FRAME_TEXT_BEGIN = 'black'  # color of text in guess box after the
        # user enters the letter, but before
        # the guess is entered.
        self.GUESS_FRAME_BG_WRONG = 'grey'  # background color of guess box
        # after the guess is entered, and the
        # letter is not in the hidden word.
        self.GUESS_FRAME_BG_CORRECT_WRONG_LOC = 'orange'  # background color
        # guess box after the guess is entered
        # and the letter is in the hidden word
        # but in the wrong location.
        self.GUESS_FRAME_BG_CORRECT_RIGHT_LOC = 'green'  # background color
        # guess box after the guess is entered
        # and the letter is in the hidden word
        # and in the correct location.
        self.GUESS_FRAME_TEXT_AFTER = 'white'  # color of text in guess box after
        # the guess is entered.
        # Font to use for letters in the guess boxes.
        self.FONT_FAMILY = 'ariel'
        # Font size for letters in the guess boxes.
        self.FONT_SIZE_GUESS = 35

        # Parameters for the keyboard frame
        self.KEYBOARD_FRAME_HEIGHT = 200
        self.KEYBOARD_BUTTON_HEIGHT = 1
        self.KEYBOARD_BUTTON_WIDTH = 6  # width of the letter buttons.  Remember,
        # width of buttons is measured in characters.
        # width of the enter and back buttons.
        self.KEYBOARD_BUTTON_WIDTH_LONG = 8
        self.BUTTON_PAD_X = 2

        # The following colors for the keyboard buttons
        # follow the same specifications as the colors defined above for the guess
        # boxes.  The problem is that if one or both of you have a mac, you will
        # not be able to change the background color of a button.  In this case,
        # just change the color of the text in the button, instead of the background color.
        # So the text color starts as the default (black), and then changes to grey, orange,
        # green depending on the result of the guess for that letter.
        self.KEYBOARD_BUTTON_BG_BEGIN = 'white'
        self.KEYBOARD_BUTTON_TEXT_BEGIN = 'black'
        self.KEYBOARD_BUTTON_BG_WRONG = 'grey'
        self.KEYBOARD_BUTTON_BG_CORRECT_WRONG_LOC = 'orange'
        self.KEYBOARD_BUTTON_BG_CORRECT_RIGHT_LOC = 'green'
        self.KEYBOARD_BUTTON_TEXT_AFTER = 'white'

        self.keyboard_frame_padding_y = 15

        self.KEYBOARD_BUTTON_NAMES = [
            ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
            ["A", "S", "D", "F", "G", "H", "J", "K", "L"],
            ["ENTER", "Z", "X", "C", "V", "B", "N", "M", "BACK"]]

        # Parameters for the control frame
        self.CONTROL_FRAME_HEIGHT = self.PARENT_GUESS_FRAME_HEIGHT + self.KEYBOARD_FRAME_HEIGHT
        self.CONTROL_FRAME_WIDTH = 300
        # Horizontal padding on either side of the widgets in
        self.USER_SELECTION_PADDING = 10
        # the parameter frame.

        self.MESSAGE_DISPLAY_TIME_SECS = 5  # Length of time the message should be
        # displayed.
        # When processing a guess (changing color
        self.PROCESS_GUESS_WAITTIME = 1
        # of the guess frames), time to wait between
        # updating successive frames.

        self.previous_guesses = {}
        self.incorrect_letters = {}
        self.right_spots = {}
        self.found_inconsistency = False

        self.window = tk.Tk()
        self.window.title("Wordy")

        self.window.geometry("1050x700")

        self.setup_parent_guess_frame()
        self.setup_buttons_frame()
        self.setup_ride_parent_frame()
        self.setup_message_frame()
        self.setup_options_frame()
        self.setup_start_quit_frame()

        self.load_words()

        tk.mainloop()

    def button_handler(self, key):
        if self.started_game:
            if key == "ENTER":
                self.enter()
            elif key == "BACK":
                if self.last_square > 0 and self.last_square > self.last_guess_index:
                    self.Guess_label_list[self.last_square-1]['text'] = ""
                    self.last_square -= 1
                    if self.last_square == self.last_guess_index:
                        self.guess_finished = True

            else:
                if self.last_square < len(self.Guess_label_list):
                    if self.last_square > 1 and (self.last_square) % self.WORD_SIZE == 0 and not self.guess_finished:
                        return
                    self.guess_finished = False
                    self.Guess_label_list[self.last_square]['text'] = key
                    self.last_square += 1
                    self.current_guess_row = (
                        self.last_square-1)//self.WORD_SIZE + 1
             


        else:
            return

    def enter(self):
        ''' Preforms the correct action for the guess frame, if the enter key is pressed '''
        # check if word in current guess row is 5 letters long
        if (self.last_square) % self.WORD_SIZE != 0:
            self.display_message("Word not finished")
        elif self.last_square != 0:
            word = ""
            if self.guesses_must_be_words.get():
                word = self.check_word()
                if self.guess_finished:
                    self.process_guess(word)
            else:
                word = self.create_word()
                self.process_guess(word)
            if word != None and not self.found_inconsistency:
                self.guess_finished = True
                self.last_guess_index = self.last_square
            if word.lower() != self.hidden_word.get() and word != None and self.last_square == len(self.Guess_label_list):
                self.display_message(
                    f"Guesses used up. Word was {self.hidden_word.get()}. Game over.")

    def check_word(self):
        ''' Checks if entered word is valid guess, and returns the word if it is '''
        # initialize word for the for loop
        word = self.create_word()

        # check if the word is a valid guess
        if word.lower() not in self.words_list_long:
            self.display_message("Word is not in word list")

        else:
            # test passed
            self.guess_finished = True
            return word

    def process_guess(self, word):
        hidden_word = self.hidden_word.get()
        count = 0
        if word == hidden_word:
            for i in range(self.last_square - self.WORD_SIZE, self.last_square):
                self.Color_Guess_Frame(i, 1)
                time.sleep(self.PROCESS_GUESS_WAITTIME)
                self.window.update()
                self.Color_Keyboard_Frame(word[count], 1)
                # time.sleep(self.PROCESS_GUESS_WAITTIME)
                count += 1
            self.Game_over()
        else:
            finished_correct = False
            correct_done = 0
            letter_instances = letter_instance_init(hidden_word)
            letter_count = letter_counter(hidden_word)
            unchecked_indeces = [index for index in range(self.last_square -self.WORD_SIZE, self.last_square)]
            styles = []
            temp_letters = []
            for _ in range(self.WORD_SIZE):
                styles.append(0)
            for i in range(self.last_square - self.WORD_SIZE, self.last_square):
                user_letter = word[count]
                hidden_letter = hidden_word[count]
                if user_letter == hidden_letter:
                    #self.Color_Guess_Frame(i, 1)
                    self.previous_guesses[user_letter+"#c"]=("correct",i%self.WORD_SIZE)
                    self.right_spots[i%self.WORD_SIZE]=user_letter
                    styles[count]=(i,1)
                    self.Color_Keyboard_Frame(user_letter, 1)
                    letter_instances[hidden_letter] = letter_instances.get(hidden_letter,0) + 1
                    unchecked_indeces.remove(i)
                    hidden_word = replace(hidden_word, "#", count)
                elif user_letter not in hidden_word:
                    #self.Color_Guess_Frame(i, 3)
                    if self.hard_mode.get():
                        if (self.incorrect_letters.get(user_letter,0)==1 and self.last_square>self.WORD_SIZE) or self.right_spots.get(count, None) != None:
                            self.display_message(f"{word} is not consistent with previous guesses1.")
                            self.guess_finished = False
                            self.found_inconsistency = True
                            self.remove_guesses(temp_letters)
                            return
                    self.incorrect_letters[user_letter]=1
                    temp_letters.append(user_letter)
                    styles[count]=(i,3)
                    self.Color_Keyboard_Frame(user_letter, 3)
                    unchecked_indeces.remove(i)
                
                count += 1

            temp_count = count-self.WORD_SIZE
            for index in unchecked_indeces:
                letter = word[index%self.WORD_SIZE]

                if letter in hidden_word:
                    if letter_instances[letter]<letter_count[letter]:
                        #self.Color_Guess_Frame(index, 2)
                        styles[index%self.WORD_SIZE]=(index,2)
                        if self.hard_mode.get():
                            previous_data = self.previous_guesses.get(letter,0)
                            if previous_data!=0:
                                if index%self.WORD_SIZE in previous_data[1] and self.right_spots.get(index, None) == None:
                                    self.display_message(f"{word} is not consistent with previous guesses2.")
                                    self.guess_finished = False
                                    self.found_inconsistency = True
                                    if self.previous_guesses.get(letter,0) == 0:
                                        self.previous_guesses[letter] = ("incorrect",[index%self.WORD_SIZE])
                                    else:
                                        self.previous_guesses[letter][1].append(index%self.WORD_SIZE)
                                    return
                            else:
                                if self.right_spots.get(index, None) == None and self.last_square>self.WORD_SIZE:
                                    self.display_message(f"{word} is not consistent with previous guesses2.")
                                    self.guess_finished = False
                                    self.found_inconsistency = True
                                    return
                        self.Color_Keyboard_Frame(letter, 2)
                else:
                    #self.Color_Guess_Frame(index, 3)
                    styles[index%self.WORD_SIZE]=(index,3)
                    self.Color_Keyboard_Frame(letter, 3)
            
            for index,style in styles:
                self.Color_Guess_Frame(index, style)
                time.sleep(self.PROCESS_GUESS_WAITTIME)
                self.window.update()

            self.last_guess_index=self.last_square
            self.guess_finished = True
            

    def Color_Guess_Frame(self, index, style):
        self.Guess_label_list[index]['fg'] = self.GUESS_FRAME_TEXT_AFTER
        if style == 1:
            self.Guess_label_list[index]['bg'] = self.GUESS_FRAME_BG_CORRECT_RIGHT_LOC
            self.Guess_frame_list[index]['bg'] = self.GUESS_FRAME_BG_CORRECT_RIGHT_LOC
        elif style == 2:
            self.Guess_label_list[index]['bg'] = self.GUESS_FRAME_BG_CORRECT_WRONG_LOC
            self.Guess_frame_list[index]['bg'] = self.GUESS_FRAME_BG_CORRECT_WRONG_LOC
        else:
            self.Guess_label_list[index]['bg'] = self.GUESS_FRAME_BG_WRONG
            self.Guess_frame_list[index]['bg'] = self.GUESS_FRAME_BG_WRONG
        
    def remove_guesses(self, items):
        for item in items:
            del self.incorrect_letters[item]

    def Color_Keyboard_Frame(self, letter, style):
        letter = letter.upper()
        if style == 1:
            self.buttons[letter]['fg'] = self.KEYBOARD_BUTTON_BG_CORRECT_RIGHT_LOC
        elif style == 2:
            self.buttons[letter]['fg'] = self.KEYBOARD_BUTTON_BG_CORRECT_WRONG_LOC
        else:
            self.buttons[letter]['fg'] = self.KEYBOARD_BUTTON_BG_WRONG

    def Game_over(self):
        self.display_message("Correct. Nice Job. Game Over")
        self.started_game = False

    def create_word(self):
        word = ""
        for i in range(self.last_square-self.WORD_SIZE, self.last_square):
            word += self.Guess_label_list[i].cget("text").lower()
        return word

    def show_hide_word(self):
        ''' 
        Shows/Hides the hidden word
        '''
        # If word is hidden, show it
        if self.show_word.get():
            self.hidden_word_label.grid(row=3, column=1)
        else:  # If word is being shown, hide it
            self.hidden_word_label.grid_remove()

    def display_message(self, message):
        ''' 
        Displays the message in the message frame and schedules an event 5 seconds in the future to hide the message
        '''
        self.message_variable.set(message)
        # Schedule the hide message event (5 secs after)
        self.window.after(self.MESSAGE_DISPLAY_TIME_SECS *
                          1000, self.hide_message)

    def hide_message(self):
        ''' 
        Hides the message in the message frame
        '''
        self.message_variable.set("")

    def start_game(self):
        if not self.specify_word.get():  # user did not specify word
            self.hidden_word.set(random.choice(self.words_list_short))
        else:  # user specified word
            word = self.specify_word_entry.get().lower()
            if len(word) != self.WORD_SIZE:  # specified word is not of correct length
                self.display_message("Incorrect specified word length")
                return
            else:  # specified word is of correct length
                if self.guesses_must_be_words.get():  # guess only words enabled
                    # word is valid (Changed to short list)
                    if word in self.words_list_short:
                        self.hidden_word.set(self.specify_word_entry.get())
                    else:  # word is invalid
                        self.display_message("Specified word not a valid word")
                        return
                self.hidden_word.set(self.specify_word_entry.get())
        self.started_game = True

        # Since we return whenever we find an error, the code below is only going to be executed if the game started
        self.hard_mode_check["state"] = "disabled"
        self.guesses_must_be_words_check["state"] = "disabled"
        self.specify_word_check["state"] = "disabled"
        self.specify_word_entry["state"] = "disabled"

    def quit_game(self):
        ''' 
        Quits the program
        '''
        self.window.destroy()

    def load_words(self):
        ''' 
        Loads the words from the files long_wordlist.txt and short_wordlist.txt into lists
        '''
        try:
            file_long = open(self.LONG_WORDLIST_FILENAME, "r")
            file_short = open(self.SHORT_WORDLIST_FILENAME, "r")

            for line in file_long:
                line = line.strip()
                if len(line) == self.WORD_SIZE:
                    self.words_list_long.append(line)

            for line in file_short:
                line = line.strip()
                if len(line) == self.WORD_SIZE:
                    self.words_list_short.append(line)
        except FileNotFoundError:
            print(
                "Couldn't load words from file/s. Try again or check that the files exist")

    ''' 
    Frame set up methods:
    '''

    def setup_parent_guess_frame(self):
        ''' Start of Guess Frame'''
        self.parent_guess_frame = tk.Frame(self.window, height=self.PARENT_GUESS_FRAME_HEIGHT,
                                           width=self.PARENT_GUESS_FRAME_WIDTH, borderwidth=1, relief="solid")
        self.parent_guess_frame.grid_propagate(False)
        self.parent_guess_frame.grid(row=0, column=0, sticky="N")
        # trying to display text
        self.font = font.Font(family=self.FONT_FAMILY,
                              size=self.FONT_SIZE_GUESS)
        self.Guess_label_list = []
        self.Guess_frame_list = []

        self.last_guess_index = 0

        self.current_guess_row = 1

        self.create_guesses_frames()

        self.parent_guess_frame.grid_columnconfigure(0, weight=2)
        self.parent_guess_frame.grid_columnconfigure(
            self.WORD_SIZE+1, weight=2)

        self.parent_guess_frame.grid_rowconfigure(0, weight=2)
        self.parent_guess_frame.grid_rowconfigure(self.NUM_GUESSES+1, weight=2)

        ''' End of Parent Guess Frame'''

    def create_guesses_frames(self):
        for r in range(1, self.NUM_GUESSES+1):
            for c in range(1, self.WORD_SIZE+1):
                frame = tk.Frame(self.parent_guess_frame, height=self.GUESS_FRAME_SIZE, width=self.GUESS_FRAME_SIZE,
                                 background=self.GUESS_FRAME_BG_BEGIN, borderwidth=1, relief="solid")
                frame.grid_propagate(False)
                frame.grid(row=r, column=c, padx=self.GUESS_FRAME_PADDING,
                           pady=self.GUESS_FRAME_PADDING)
                frame.grid_rowconfigure(0, weight=1)
                frame.grid_columnconfigure(0, weight=1)
                self.Guess_frame_list.append(frame)

                label = tk.Label(frame, background=self.GUESS_FRAME_BG_BEGIN,
                                 fg=self.GUESS_FRAME_TEXT_BEGIN, font=self.font)
                label.grid_propagate(False)
                label.grid(row=0, column=0, sticky="")
                self.Guess_label_list.append(label)

    def setup_buttons_frame(self):
        ''' Start of buttons frame '''
        self.keyboard_frame = tk.Frame(self.window, height=self.KEYBOARD_FRAME_HEIGHT,
                                       width=self.PARENT_GUESS_FRAME_WIDTH, borderwidth=1, relief="solid", pady=self.keyboard_frame_padding_y)
        self.keyboard_frame.grid_propagate(False)
        self.keyboard_frame.grid(row=1, column=0)

        self.button_text = [['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
                            ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
                            ['ENTER', 'Z', 'X', 'C', 'V', 'B', 'N', 'M', 'BACK']]

        self.buttons = {}
        self.group_frames = []

        self.guess_finished = False

        self.create_keyboard()

        grid_size = self.keyboard_frame.grid_size()

        self.keyboard_frame.grid_columnconfigure(0, weight=1)
        self.keyboard_frame.grid_columnconfigure(grid_size[0]-1, weight=1)
        ''' End of buttons frame'''

    def create_keyboard(self):
        for group_num in range(len(self.button_text)):
            group_frame = tk.Frame(self.keyboard_frame,
                                   width=self.PARENT_GUESS_FRAME_WIDTH)
            pady = self.KEYBOARD_FRAME_HEIGHT//4
            if group_num != 0:
                pady = 0
            group_frame.grid(row=group_num, column=0, pady=(pady, 5))
            for key_num in range(len(self.button_text[group_num])):
                def handler(key=self.button_text[group_num][key_num]):
                    self.button_handler(key)

                width = self.KEYBOARD_BUTTON_WIDTH
                if group_num == 2 and (key_num == 0 or key_num == (len(self.button_text[group_num])-1)):
                    width = self.KEYBOARD_BUTTON_WIDTH_LONG
                button = tk.Button(group_frame,
                                   height=self.KEYBOARD_BUTTON_HEIGHT,
                                   width=width,
                                   text=self.button_text[group_num][key_num],
                                   font=self.FONT_FAMILY,
                                   command=handler,
                                   )
                button.grid(row=group_num + 1, column=key_num +
                            1, padx=self.BUTTON_PAD_X)

                # Put the button in a dictionary of buttons
                # where the key is the button text, and the
                # value is the button object.
                self.buttons[self.button_text[group_num][key_num]] = button
            self.group_frames.append(group_frame)

    def setup_ride_parent_frame(self):
        ''' Right side frames'''
        self.control_frame = tk.Frame(self.window, height=self.CONTROL_FRAME_HEIGHT,
                                      width=self.CONTROL_FRAME_WIDTH, borderwidth=1, relief="solid")
        self.control_frame.grid_propagate(False)
        self.control_frame.grid(row=0, column=1, rowspan=2)

    def setup_message_frame(self):
        ''' Start of results/message frame'''
        self.results_frame = tk.Frame(self.control_frame, height=self.CONTROL_FRAME_HEIGHT //
                                      3, width=self.CONTROL_FRAME_WIDTH, borderwidth=1, relief="solid")
        self.results_frame.grid_propagate(False)
        self.results_frame.grid(row=0, column=0)

        self.message_variable = tk.StringVar()

        self.message = tk.Label(
            self.results_frame, textvariable=self.message_variable)
        self.message.grid(row=1, column=1)

        self.results_frame.grid_columnconfigure(0, weight=2)
        self.results_frame.grid_columnconfigure(2, weight=2)

        self.results_frame.grid_rowconfigure(0, weight=2)
        self.results_frame.grid_rowconfigure(2, weight=2)

        ''' End of results/message frame'''

    def setup_options_frame(self):
        ''' Start of Options Frame '''
        self.options_Frame = tk.Frame(self.control_frame, height=self.CONTROL_FRAME_HEIGHT //
                                      3, width=self.CONTROL_FRAME_WIDTH, borderwidth=1, relief="solid")
        self.options_Frame.grid_propagate(False)
        self.options_Frame.grid(row=1, column=0)

        self.hard_mode = tk.BooleanVar()
        self.hard_mode.set(False)
        self.guesses_must_be_words = tk.BooleanVar()
        self.guesses_must_be_words.set(True)
        self.show_word = tk.BooleanVar()
        self.show_word.set(False)
        self.specify_word = tk.BooleanVar()
        self.specify_word.set(False)

        self.specified_word = tk.StringVar()

        self.hidden_word = tk.StringVar()

        self.setup_option_widgets()

        self.options_Frame.grid_rowconfigure(0, weight=1)
        self.options_Frame.grid_rowconfigure(5, weight=1)

        ''' End of Options Frame '''

    def setup_option_widgets(self):
        # Setting up widgets, onvalue and offvalue handle the value of the boolean variables
        self.hard_mode_check = tk.Checkbutton(
            self.options_Frame, text="Hard Mode", variable=self.hard_mode, onvalue=True, offvalue=False)
        self.hard_mode_check.grid(
            row=1, column=0, sticky="W", padx=self.PADDING)

        self.guesses_must_be_words_check = tk.Checkbutton(
            self.options_Frame, text="Guesses must be words", variable=self.guesses_must_be_words, onvalue=True, offvalue=False)
        self.guesses_must_be_words_check.grid(
            row=2, column=0, sticky="W", padx=self.PADDING)

        self.show_word_check = tk.Checkbutton(
            self.options_Frame, text="Show Word", variable=self.show_word, onvalue=True, offvalue=False, command=self.show_hide_word)
        self.show_word_check.grid(
            row=3, column=0, sticky="W", padx=self.PADDING)

        self.hidden_word_label = tk.Label(
            self.options_Frame, textvariable=self.hidden_word)

        self.specify_word_check = tk.Checkbutton(
            self.options_Frame, text="Specify word", variable=self.specify_word, onvalue=True, offvalue=False)
        self.specify_word_check.grid(
            row=4, column=0, sticky="W", padx=self.PADDING)

        self.specify_word_entry = tk.Entry(
            self.options_Frame, width=self.SPECIFY_ENTRY_WIDTH)
        self.specify_word_entry.grid(
            row=4, column=1, sticky="W", padx=self.PADDING)

    def setup_start_quit_frame(self):
        ''' Start of start/quit frame '''
        self.start_quit_frame = tk.Frame(self.control_frame, height=self.CONTROL_FRAME_HEIGHT //
                                         3, width=self.CONTROL_FRAME_WIDTH, borderwidth=1, relief="solid")
        self.start_quit_frame.grid_propagate(False)
        self.start_quit_frame.grid(row=2, column=0)

        self.start_button = tk.Button(
            self.start_quit_frame, text="Start game", command=self.start_game)
        self.start_button.grid(row=1, column=1)

        self.quit_button = tk.Button(
            self.start_quit_frame, text="Quit", command=self.quit_game)
        self.quit_button.grid(row=1, column=2)

        ''' End of start/quit frame '''

        # Centering widgets
        self.start_quit_frame.grid_rowconfigure(0, weight=2)
        self.start_quit_frame.grid_rowconfigure(1, weight=1)
        self.start_quit_frame.grid_rowconfigure(2, weight=2)

        self.start_quit_frame.grid_columnconfigure(0, weight=2)
        self.start_quit_frame.grid_columnconfigure(3, weight=2)

def replace(s,ch,index):
    ret_s = ""
    if index>(len(s)+1):
        raise BadReplacementIndexError
    else:
        for i in range(len(s)):
            if i!=index:
                ret_s+=s[i]
            else:
                ret_s+=ch
    return ret_s

def letter_counter(s):
    count_dict = {}
    for ch in s:
        if ch not in count_dict:
            count_dict[ch]=s.count(ch)
    return count_dict

def letter_instance_init(s):
    instance_dict = {}
    for ch in s:
        if ch not in instance_dict:
            instance_dict[ch]=0
    return instance_dict

class BadReplacementIndexError(Exception):
    pass

if __name__ == "__main__":
    Wordy()
