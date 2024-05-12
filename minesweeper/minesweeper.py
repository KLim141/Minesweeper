import sys
from random import randint
import tkinter as tk
from threading import Thread
import time


class Main(tk.Frame):
    def __init__(self, app_root):
        super().__init__(app_root)
        self.create_window()

    def create_window(self):
        # creating main window

        # toolbar for buttons
        toolbar = tk.Frame(bg='white')
        toolbar.pack()

        # buttons to select game mode
        button1 = tk.Button(toolbar, text='8x8\n10 мин', width=15,
                            height=7, bg='#7d7d7d', font=('Roboto', 14),
                            command=lambda: self.create_game_field(10, 10, 10))
        button1.pack(padx=[30, 15], pady=30, side=tk.LEFT, expand=1)

        button2 = tk.Button(toolbar, text='16x16\n40 мин', width=15,
                            height=7, bg='#7d7d7d', font=('Roboto', 14),
                            command=lambda: self.create_game_field(16, 16, 40))
        button2.pack(padx=15, pady=30, side=tk.LEFT, expand=1)

        button3 = tk.Button(toolbar, text='16x30\n99 мин', width=15,
                            height=7, bg='#7d7d7d', font=('Roboto', 14),
                            command=lambda: self.create_game_field(16, 30, 99))
        button3.pack(padx=[15, 30], pady=30, side=tk.LEFT, expand=1)

    @staticmethod
    def create_game_field(row, column, mines):
        GameWindow(root, row, column, mines)


class GameWindow(tk.Toplevel):
    def __init__(self, app_root, row, column, mines):
        super().__init__(app_root)
        self.r = row
        self.c = column
        self.mines = mines
        self.open_cells = 0
        self.marked_cells = 0
        self.corr_marked_cells = 0
        self.game_time = 0
        self.start_time = time.time()
        self.title('Minesweeper')
        self.resizable(False, False)
        self['background'] = 'white'
        self.focus_set()
        self.buttons = {}
        self.fl_loose = False
        self.fl_win = False
        self.images = {
            0: tk.PhotoImage(file='./images/0.png'),
            1: tk.PhotoImage(file='./images/1.png'),
            2: tk.PhotoImage(file='./images/2.png'),
            3: tk.PhotoImage(file='./images/3.png'),
            4: tk.PhotoImage(file='./images/4.png'),
            5: tk.PhotoImage(file='./images/5.png'),
            6: tk.PhotoImage(file='./images/6.png'),
            7: tk.PhotoImage(file='./images/7.png'),
            8: tk.PhotoImage(file='./images/8.png'),
            'cl_cell': tk.PhotoImage(file='./images/cl_cell.png'),
            'mark': tk.PhotoImage(file='./images/mark.png'),
            'bomb_act': tk.PhotoImage(file='./images/bomb_act.png'),
            'bomb': tk.PhotoImage(file='./images/bomb.png'),
            'mark_false': tk.PhotoImage(file='./images/mark_false.png'),
            'mark_true': tk.PhotoImage(file='./images/mark_true.png'),
        }
        self.create_window()

    def randomize_mines(self, not_r, not_c):
        # randomizing mines places
        counter = 0
        while counter < self.mines:
            row = randint(0, self.r - 1)
            column = randint(0, self.c - 1)
            if row != not_r and column != not_c and not self.buttons[row, column].mine:
                self.buttons[row, column].mine = True
                for x in range(-1, 2):
                    for y in range(-1, 2):
                        self.calculate_mines(row + x, column + y)
                counter += 1

    def calculate_mines(self, r, c):
        if self.check_cords(r, c):
            self.buttons[r, c].around_mines += 1

    def check_cords(self, r, c):
        if self.r > r >= 0 and self.c > c >= 0 and not self.buttons[r, c].mine:
            return True
        return False

    def create_window(self):
        # creating field window

        self.field = tk.Frame(self)
        self.field.grid(row=1, column=0, padx=10, pady=[5, 10], columnspan=2)

        dash_board = tk.Frame(self, background='white')
        dash_board.grid(row=0, column=0, padx=[10, 5], pady=[5, 5], sticky='w')

        self.mark_label = tk.Label(dash_board,
                                   text=f'Осталось открыть {self.mines - self.marked_cells} мин',
                                   font=('Roboto Regular', 11), background='white')
        self.mark_label.grid(row=0, column=0, sticky='w')

        self.clock_label = tk.Label(dash_board, text=f'Время: 00:00', background='white',
                                    font=('Roboto Regular', 11))
        self.clock_label.grid(row=1, column=0, sticky='w')
        self.thread = Thread(target=self.game_timer)
        self.thread.start()

        for r in range(self.r):
            for c in range(self.c):
                self.buttons[r, c] = Cell(tk.Label(self.field, image=self.images['cl_cell'],
                                                   border=1, highlightthickness=0,
                                                   relief=tk.FLAT,state='normal'))
                self.buttons[r, c].button.bind(
                    '<Button-1>', lambda ev, row=r, col=c: self.left_click(row, col))
                self.buttons[r, c].button.bind(
                    '<Button-3>', lambda ev, row=r, col=c: self.right_click(row, col))
                self.buttons[r, c].button.grid(row=r, column=c)

    def left_click(self, r, c):
        if self.fl_loose:
            return
        if self.buttons[r, c].mine:
            self.loose(r, c)
            return
        if self.open_cells == 0:
            self.randomize_mines(r, c)
            self.open_cells = 1
        self.open_all_cells(r, c)

    def open_all_cells(self, r, c):
        queue = set()
        queue.add((r, c))
        flag = True
        while flag:
            flag = False
            temp_queue = set()
            for i in queue:
                for x in range(-1, 2):
                    for y in range(-1, 2):
                        row = i[0] + x
                        col = i[1] + y
                        if (self.check_cords(row, col) and
                                not self.buttons[row, col].mine and
                                (row, col) not in queue and
                                self.buttons[i[0], i[1]].around_mines == 0):
                            temp_queue.add((i[0] + x, i[1] + y))
            if len(temp_queue) > 0:
                queue.update(temp_queue)
                flag = True
        for q in queue:
            self.open_cell(q[0], q[1])

    def open_cell(self, r, c):
        # opening selected cell
        if not self.check_cords(r, c):
            return
        cell = self.buttons[r, c]
        cell.fl_open = True
        if cell.is_marked:
            cell.is_marked = False
            self.marked_cells -= 1
            self.mark_label.config(text=f'Осталось открыть {self.mines - self.marked_cells} мин')
            if cell.mine:
                self.corr_marked_cells -= 1
        cell.button.config(image=self.images[cell.around_mines])

    def right_click(self, r, c):
        if self.fl_loose:
            return
        if not self.buttons[r, c].fl_open and not self.buttons[r, c].is_marked:
            self.buttons[r, c].button.config(image=self.images['mark'])
            self.marked_cells += 1
            self.mark_label.config(text=f'Осталось открыть {self.mines - self.marked_cells} мин')
            self.buttons[r, c].is_marked = True
            if self.buttons[r, c].mine:
                self.corr_marked_cells += 1
        elif self.buttons[r, c].is_marked:
            self.buttons[r, c].button.config(image=self.images['cl_cell'])
            self.buttons[r, c].is_marked = False
            self.marked_cells -= 1
            self.mark_label.config(text=f'Осталось открыть {self.mines - self.marked_cells} мин')
            if self.buttons[r, c].mine:
                self.corr_marked_cells -= 1
        self.is_win()

    def loose(self, r, c):
        for i in range(self.r):
            for j in range(self.c):
                if self.buttons[i, j].mine and not self.buttons[i, j].is_marked:
                    self.buttons[i, j].button['image'] = self.images['bomb']
                if not self.buttons[i, j].mine and self.buttons[i, j].is_marked:
                    self.buttons[i, j].button['image'] = self.images['mark_false']
                if self.buttons[i, j].is_marked and self.buttons[i, j].mine:
                    self.buttons[i, j].button['image'] = self.images['mark_true']
        self.buttons[r, c].button.config(image=self.images['bomb_act'])
        self.fl_loose = True
        self.win_loose_window('loose')
    
    def is_win(self):
        if self.corr_marked_cells == self.marked_cells == self.mines:
            self.fl_win = True
            for i in range(self.r):
                for j in range(self.c):
                    if self.buttons[i, j].is_marked:
                        self.buttons[i, j].button['image'] = self.images['mark_true']
            self.win_loose_window('win')

    def game_timer(self):
        while not(self.fl_loose or self.fl_win):
            self.game_time = int(round(time.time() - self.start_time, 0))
            minutes = self.game_time // 60
            secs = self.game_time % 60
            self.clock_label.config(text=f'Время: {str(minutes).zfill(2)}:{str(secs).zfill(2)}')
            time.sleep(0.1)

    def win_loose_window(self, flag):
        self.wind = tk.Toplevel(self, background='white')
        self.wind.geometry('320x175')
        self.wind.resizable(False, False)
        text = tk.Label(self.wind, text='Вы проиграли!' if flag == 'loose' else 'Вы выиграли!', 
                        font=('Roboto', 13), bg='white')
        text.pack(padx=20, pady=[20, 10], expand=1)

        ex_button = tk.Button(self.wind, text='Выйти', font=('Roboto', 11),
                              command=sys.exit, bg='#7d7d7d', width=15)
        ex_button.pack(padx=[20, 10], pady=20, side=tk.LEFT, anchor='s')

        play_again = tk.Button(self.wind, text='Играть заново', font=('Roboto', 11),
                               command=self.play_again, bg='#7d7d7d', width=15)
        play_again.pack(padx=[10, 20], pady=20, side=tk.RIGHT, anchor='s')

    def play_again(self):
        self.destroy()
        Main.create_game_field(self.r, self.c, self.mines)


class Cell:
    def __init__(self, button):
        self.around_mines = 0
        self.mine = False
        self.fl_open = False
        self.is_marked = False
        self.button = button


root = tk.Tk()
icon = tk.PhotoImage(file='./images/icon.png')
root.iconphoto(True, icon)
app = Main(root)
app.place()
root.title('Minesweeper')
root.resizable(False, False)
root.mainloop()
