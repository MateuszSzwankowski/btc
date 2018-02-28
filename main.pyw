import tkinter as tk
from app import App


def center(win):
    win.update_idletasks()
    width = win.winfo_width()
    height = win.winfo_height()
    x = (win.winfo_screenwidth() // 2) - (width // 2)
    y = (win.winfo_screenheight() // 2) - (height // 2)
    win.geometry(f'+{x}+{y}')

if __name__ == '__main__':
    root = tk.Tk()
    root.title('$$$')
    
    pairs = ['USDT_BTC', 'USDT_ETH', 'USDT_DASH', 'USDT_LTC',
             'USDT_NXT','USDT_XMR', 'USDT_XRP', 'USDT_STR',
             'USDT_ETC', 'USDT_REP', 'USDT_ZEC', 'USDT_BCH']
             
    config = {'rows':3,
              'columns':4,
              'tick_time':30000,    # ms
              'history_size':2880}  # 2880 for 24h with 30s ticks
    
    app = App(root, pairs, config)
    center(root)
    root.mainloop()
    