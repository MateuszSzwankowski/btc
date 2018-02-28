import tkinter as tk
import requests
import datetime
import sys

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.lines import Line2D
from matplotlib.dates import DateFormatter


class App():
    def __init__(self, root, pairs, config):
        self.root = root
        self.pairs = pairs
        self.rows = config['rows']
        self.columns = config['columns']
        self.tick_time = config['tick_time']
        self.history_size = config['history_size']
        
        self.time = list()  # list of time values
        self.bids = dict()  # key: pair, value: list of bid values
        self.asks = dict()  # key: pair, value: list of ask values
        # all above are being updated every {tick_time} ms
        self.plots = dict()  # key: pair, value: corresponding plot in main frame
        
        self.focus = Focus(root)  # frame with single pair plot
        # created once and for all to avoid memory leaks
        self.focus.canvas.mpl_connect('button_press_event', self.unfocus)  
        
        self.main_frame = tk.Frame(root)
        self.main_frame.pack()
        
        self.fig = Figure(figsize=(16, 9))
        self.fig.suptitle('poloniex live charts', fontsize=14, fontweight='bold')
        self.start_ticking()
        self.fig.legend(self.plots[pairs[0]].lines, ('ask', 'bid'))
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.main_frame)
        self.canvas.get_tk_widget().pack(expand=True, fill=tk.BOTH)
        self.canvas.mpl_connect('button_press_event', self.focus_selected)
        self.canvas.draw()
    
    def start_ticking(self):
        try:
            tick = self.get_tick()
        except Exception as e:
            print(e)
            sys.exit()
            
        self.time.append(datetime.datetime.now())
        
        for i, pair in enumerate(self.pairs):
            self.plots[pair] = self.fig.add_subplot(self.rows, self.columns, i+1)
            bid, ask = tick[pair]
            self.bids[pair] = [bid]
            self.asks[pair] = [ask]
            self.draw_plot(self.plots[pair], pair)
        
        self.fig.autofmt_xdate()
        self.root.after(self.tick_time, self.tick)
    
    def draw_plot(self, plot, pair):
        plot.set_title(pair)
        line1 = Line2D(self.time, self.asks[pair], color='red', label='ask')
        line2 = Line2D(self.time, self.bids[pair], color='blue', label='bid')
        plot.add_line(line1)
        plot.add_line(line2)
        plot.grid()
        plot.relim()
        plot.autoscale(enable=True, axis='both', tight=False)
        plot.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))
    
    def get_tick(self):
        response = requests.get('https://poloniex.com/public?command=returnTicker')
        response.raise_for_status()
        json = response.json()
        tick = {}
        for pair in self.pairs:
            bid = float(json[pair]['highestBid'])
            ask = float(json[pair]['lowestAsk'])
            tick[pair] = round(bid, 4), round(ask, 4)
        return tick
    
    def tick(self):
        try:
            tick = self.get_tick()
        except Exception as e:
            print(e)
            self.root.after(self.tick_time, self.tick)
            return
            
        self.time.append(datetime.datetime.now())
        self.time = self.time[-self.history_size:]
        
        for pair in self.pairs:
            bid, ask = tick[pair]
            self.bids[pair].append(bid)
            self.bids[pair] = self.bids[pair][-self.history_size:]
            self.asks[pair].append(ask)
            self.asks[pair] = self.asks[pair][-self.history_size:]
            self.update_plot(self.plots[pair], pair)
        self.canvas.draw()
        
        if self.focus.pair:
            self.update_plot(self.focus.plot, self.focus.pair)
            self.focus.canvas.draw()
        
        self.root.after(self.tick_time, self.tick)
    
    def update_plot(self, plot, pair):
        plot.lines[0].set_data(self.time, self.asks[pair])
        plot.lines[1].set_data(self.time, self.bids[pair])
        plot.relim()
        plot.autoscale(enable=True, axis='both', tight=False)
    
    def focus_selected(self, event):
        if event.inaxes:
            pair = event.inaxes.get_title()
            self.focus.pair = pair
            self.draw_plot(self.focus.plot, pair)
            self.focus.plot.legend()
            self.focus.plot.set_title(pair)
            self.focus.canvas.draw()
            
            self.main_frame.pack_forget()
            self.focus.frame.pack(expand=True, fill=tk.BOTH)
    
    def unfocus(self, event):
        self.focus.plot.clear()
        self.focus.pair = None
        
        self.focus.frame.pack_forget()
        self.main_frame.pack(expand=True, fill=tk.BOTH)


class Focus():
    def __init__(self, root):
        self.frame = tk.Frame(root)
        self.fig = Figure(figsize=(16, 9))
        self.fig.autofmt_xdate()
        self.plot = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.pair = None
