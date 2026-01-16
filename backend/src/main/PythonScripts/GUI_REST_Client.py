"""
GUI REST Client - Replacement for GUI19WithServer.py
A Tkinter-based GUI that communicates with the REST server via HTTP endpoints.
This replaces the socket-based communication with REST API calls.

Usage:
    1. Start the REST server: python rest_server.py
    2. Run this GUI client: python GUI_REST_Client.py
"""
from tkinter import ttk
import tkinter as tk
import functools
from time import strftime
import time
from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage
import threading
import logging

# Import REST client module
from rest_client_module import RESTClient, LoadGUIDB, connect_to_server, poll_server

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger("GUI_REST_Client")

# REST Server configuration
REST_SERVER_URL = "http://127.0.0.1:5000"

# Query for TinyDB
query = Query()
fp = functools.partial

# Global state variables
paulBusy = False  # guard to avoid overlapping poll with active transaction
terminal = "Starting..."  # GUI terminal on display
UpdateServerf = 1.0  # Polling interval in seconds


class VerticalScrolledFrame(ttk.Frame):
    """A scrollable frame widget for Tkinter."""
    
    def __init__(self, parent, *args, **kw):
        ttk.Frame.__init__(self, parent, *args, **kw)
        
        # track changes to the canvas and frame width and sync them
        def _configure_interior(event):
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                canvas.config(width=interior.winfo_reqwidth())
        
        def _configure_canvas(event):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())
        
        def _on_mousewheel(event, scroll):
            canvas.yview_scroll(int(scroll), "units")
        
        def _bind_to_mousewheel(event):
            canvas.bind_all("<Button-4>", fp(_on_mousewheel, scroll=-1))
            canvas.bind_all("<Button-5>", fp(_on_mousewheel, scroll=1))
        
        def _unbind_from_mousewheel(event):
            canvas.unbind_all("<Button-4>")
            canvas.unbind_all("<Button-5>")
        
        # Create canvas and scrollbar
        vscrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL)
        vscrollbar.pack(fill=tk.Y, side=tk.RIGHT, expand=tk.FALSE, padx=0)
        
        canvas = tk.Canvas(self, bd=0, highlightthickness=1,
                          yscrollcommand=vscrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.TRUE)
        vscrollbar.config(command=canvas.yview)
        
        # Reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)
        
        # Create interior frame
        self.interior = interior = ttk.Frame(canvas, height=1000, width=1000)
        interior_id = canvas.create_window(0, 0, window=interior, anchor=tk.NW,
                                          height=1000, width=1300)
        interior.bind('<Configure>', _configure_interior)
        canvas.bind('<Configure>', _configure_canvas)
        canvas.bind('<Enter>', _bind_to_mousewheel)
        canvas.bind('<Leave>', _unbind_from_mousewheel)


def poll_server_via_rest(rest_client, GUIdb, root, UpdateServerspin):
    """Periodically poll the server for updates via REST API."""
    global paulBusy, terminal
    
    try:
        if not paulBusy:
            paulBusy = True
            received, sent = poll_server(rest_client, GUIdb, query)
            if received > 0 or sent > 0:
                logger.debug(f"Poll: received={received}, sent={sent}")
            paulBusy = False
            
    except Exception as e:
        logger.error(f"Poll error: {e}")
        paulBusy = False
    finally:
        # Schedule next poll
        try:
            delay_ms = int(float(UpdateServerspin.get()) * 1000)
        except Exception:
            delay_ms = 1000
        root.after(delay_ms, lambda: poll_server_via_rest(rest_client, GUIdb, root, UpdateServerspin))


if __name__ == "__main__":
    # Initialize local database
    GUIdb = TinyDB(storage=MemoryStorage)
    if len(GUIdb) < 10:
        LoadGUIDB(GUIdb)
    
    # Create REST client
    rest_client = RESTClient(REST_SERVER_URL)
    
    # Set up root of app
    root = tk.Tk()
    root.geometry("1200x800+50+50")
    root.title("Train Control GUI (REST API Client)")
    
    # Create a frame to put the VerticalScrolledFrame inside
    holder_frame = tk.Frame(root)
    holder_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.TRUE)
    
    # Create the VerticalScrolledFrame
    vs_frame = VerticalScrolledFrame(holder_frame)
    vs_frame.pack_propagate(1)
    vs_frame.grid(row=0, column=0, rowspan=100, columnspan=11)
    
    # Helper function for HMI interface
    def HMI_Interface(a, index, zz):
        """Handle HMI value updates."""
        Failedb = False
        try:
            index = int(index)
        except TypeError:
            # If index is of an unexpected type, log and proceed with the original value.
            logger.exception("HMI_Interface received index of invalid type; proceeding without casting")
        
        logger.debug(f"HMI_Interface called with index={index}, value={zz}")
        
        if index <= 2:  # Integer HMI to PI data (indexes 1-2)
            GUIdb.update({"HMI_VALUEi": int(zz), "HMI_READi": 2}, query.INDEX == index)
        elif index >= 3 and index < 50:  # Boolean HMI to PI data (indexes 3-49)
            temp = GUIdb.get(query['INDEX'] == index)
            if temp:
                temp1 = temp.get("HMI_VALUEb")
                temp1 = not temp1
                GUIdb.update({"HMI_VALUEb": temp1, "HMI_READi": 1}, query.INDEX == index)
        elif index >= 50 and index <= 52:  # Speed values
            try:
                zz = float(zz)
            except ValueError:
                zz = 0.0
            if 0.0 <= zz <= 99:
                GUIdb.update({"PI_VALUEf": zz, "HMI_READi": 2}, query.INDEX == index)
            else:
                Failedb = True
                logger.warning("Speed value out of range")
        elif 65 <= index <= 70:  # Tram station buttons
            temp = GUIdb.get(query['INDEX'] == index)
            if temp:
                temp1 = temp.get("PI_VALUEb")
                temp1 = not temp1
                GUIdb.update({"PI_VALUEb": temp1, "HMI_READi": 1}, query.INDEX == index)
        
        return Failedb
    
    def HMI_PB(a, index, b):
        """Handle HMI pushbutton actions."""
        if index < 22:
            temp = GUIdb.get(query['INDEX'] == index)
            if temp:
                temp1HMI = temp.get("HMI_VALUEb")
                temp1HMI = not temp1HMI
                GUIdb.update({"HMI_VALUEb": temp1HMI, "HMI_READi": 2}, query.INDEX == index)
        elif 71 <= index < 99:
            temp = GUIdb.get(query['INDEX'] == index)
            if temp:
                temp1HMI = temp.get("PI_VALUEb")
                temp1HMI = not temp1HMI
                GUIdb.update({"PI_VALUEb": temp1HMI, "HMI_READi": 1}, query.INDEX == index)
    
    def Print(who):
        """Print database contents."""
        if who == "HMI":
            for i in range(1, 50):
                temp = GUIdb.get(query['INDEX'] == i)
                print(temp)
        elif who == "PI":
            for i in range(50, 70):
                temp = GUIdb.get(query['INDEX'] == i)
                print(temp)
        elif who == "ALL":
            for row in GUIdb:
                print(row)
        elif who == "Server":
            data = rest_client.print_server_db()
            if data:
                for row in data:
                    print(row)
    
    def Time():
        """Update time display and terminal."""
        global UpdateServerf, terminal
        time_string = strftime('%H:%M:%S')
        timelbl.configure(text=time_string)
        try:
            UpdateServerf = float(UpdateServerspin.get())
        except (ValueError, tk.TclError) as exc:
            logging.warning("Invalid value for UpdateServerspin; keeping previous UpdateServerf. Error: %s", exc)
        Terminal.configure(text=terminal)
        timelbl.after(1000, Time)
    
    def UpdateSpeed1a():
        """Update speed display for RR1AB."""
        temp = GUIdb.get(query['INDEX'] == 50)
        if temp:
            temp1 = str(temp.get("PI_VALUEf", 0))
            HMI_lbl1d.configure(text=temp1)
        HMI_lbl1d.after(1050, UpdateSpeed1a)
    
    def UpdateSpeed1c():
        """Update speed display for RR1CD."""
        temp = GUIdb.get(query['INDEX'] == 51)
        if temp:
            temp1 = str(temp.get("PI_VALUEf", 0))
            HMI_lbl2d.configure(text=temp1)
        HMI_lbl2d.after(1055, UpdateSpeed1c)
    
    def UpdateHMIRHT():
        """Update HMI RHT display."""
        temp = GUIdb.get(query['INDEX'] == 1)
        if temp:
            temp1 = temp.get("HMI_VALUEi", 0)
            PI_lbl4h.configure(text=temp1)
        PI_lbl4h.after(1100, UpdateHMIRHT)
    
    def UpdateHMI_TramStopTime():
        """Update Tram Stop Time display."""
        temp = GUIdb.get(query['INDEX'] == 2)
        if temp:
            temp1 = temp.get("HMI_VALUEi", 0)
            PI_lbl5h.configure(text=temp1)
        PI_lbl5h.after(1200, UpdateHMI_TramStopTime)
    
    def UpdatePISwitch1():
        """Scan and update all switch displays."""
        # Update tram bypass buttons
        for i in range(18, 22):
            temp = GUIdb.get(query['INDEX'] == i)
            if temp:
                temp1 = temp.get("HMI_VALUEb")
                if temp1:
                    textHMI, back = "Will Stop", "yellowgreen"
                else:
                    textHMI, back = "Bypass", "goldenrod"
                if i == 18:
                    HMI_btn22c.configure(text=textHMI, bg=back)
                elif i == 19:
                    HMI_btn23c.configure(text=textHMI, bg=back)
                elif i == 20:
                    HMI_btn25c.configure(text=textHMI, bg=back)
                elif i == 21:
                    HMI_btn26c.configure(text=textHMI, bg=back)
        PI_lbl14h.after(500, UpdatePISwitch1)
    
    # --- UI Widget Definitions ---
    # Load HMI Index variables
    HMIIndex01 = tk.IntVar(vs_frame.interior, value=1)
    HMIIndex02 = tk.IntVar(vs_frame.interior, value=2)
    HMIIndex03 = tk.IntVar(vs_frame.interior, value=3)
    HMIIndex04 = tk.IntVar(vs_frame.interior, value=4)
    HMIIndex18 = tk.IntVar(vs_frame.interior, value=18)
    HMIIndex19 = tk.IntVar(vs_frame.interior, value=19)
    HMIIndex20 = tk.IntVar(vs_frame.interior, value=20)
    HMIIndex21 = tk.IntVar(vs_frame.interior, value=21)
    
    # PI Index variables
    PIIndex50 = tk.IntVar(vs_frame.interior, value=50)
    PIIndex51 = tk.IntVar(vs_frame.interior, value=51)
    PIIndex52 = tk.IntVar(vs_frame.interior, value=52)
    PIIndex65 = tk.IntVar(vs_frame.interior, value=65)
    PIIndex66 = tk.IntVar(vs_frame.interior, value=66)
    
    # Header row
    tk.Label(vs_frame.interior, text="IND", justify="center", width=4, borderwidth=1, relief="solid", font=('Times new roman', 10, 'bold'), bg="springgreen").grid(row=0, column=0)
    tk.Label(vs_frame.interior, text="TAG", justify="center", width=18, borderwidth=1, relief="solid", font=('Times new roman', 10, 'bold')).grid(row=0, column=1)
    tk.Label(vs_frame.interior, text="BTN", justify="center", width=6, borderwidth=1, relief="solid", font=('Times new roman', 10, 'bold')).grid(row=0, column=2)
    tk.Label(vs_frame.interior, text="Val", justify="center", width=6, borderwidth=1, relief="solid", font=('Times new roman', 10, 'bold')).grid(row=0, column=3)
    tk.Label(vs_frame.interior, text="IND", justify="center", width=4, borderwidth=1, relief="solid", font=('Times new roman', 10, 'bold'), bg="springgreen").grid(row=0, column=4)
    tk.Label(vs_frame.interior, text="TAG", justify="center", width=18, borderwidth=1, relief="solid", font=('Times new roman', 10, 'bold')).grid(row=0, column=5)
    tk.Label(vs_frame.interior, text="BTN", justify="center", width=6, borderwidth=1, relief="solid", font=('Times new roman', 10, 'bold')).grid(row=0, column=6)
    tk.Label(vs_frame.interior, text="Val", justify="center", width=10, borderwidth=1, relief="solid", font=('Times new roman', 10, 'bold')).grid(row=0, column=7)
    
    # Time display
    time_string = strftime('%H:%M:%S')
    tk.Label(vs_frame.interior, text="TIME", justify="center", width=8, borderwidth=1, relief="solid", font=('Times new roman', 10, 'bold')).grid(row=0, column=8)
    timelbl = tk.Label(vs_frame.interior, text=time_string, justify="center", width=7, borderwidth=1, relief="solid", font=('Helvetica', 13), bg='purple', fg='white')
    timelbl.grid(row=1, column=8)
    
    # Speed displays (rows 1-3)
    HMI_lbl1d = tk.Label(vs_frame.interior, text="0.0", justify="center", width=10, borderwidth=1, relief="solid")
    HMI_lbl1d.grid(row=1, column=3)
    tk.Label(vs_frame.interior, text="--", justify="center", width=6, borderwidth=1, relief="solid").grid(row=1, column=0)
    tk.Label(vs_frame.interior, text="RR1ABspeed_HMI", justify="center", width=20, borderwidth=1, relief="solid").grid(row=1, column=1)
    
    HMI_lbl2d = tk.Label(vs_frame.interior, text="0.0", justify="center", width=10, borderwidth=1, relief="solid")
    HMI_lbl2d.grid(row=2, column=3)
    tk.Label(vs_frame.interior, text="--", justify="center", width=6, borderwidth=1, relief="solid").grid(row=2, column=0)
    tk.Label(vs_frame.interior, text="RR1CDspeed_HMI", justify="center", width=20, borderwidth=1, relief="solid").grid(row=2, column=1)
    
    tk.Label(vs_frame.interior, text="--", justify="center", width=6, borderwidth=1, relief="solid").grid(row=3, column=0)
    tk.Label(vs_frame.interior, text="RR2ABspeed_HMI", justify="center", width=20, borderwidth=1, relief="solid").grid(row=3, column=1)
    
    # HMI_RHT (row 4)
    tk.Label(vs_frame.interior, textvariable=HMIIndex01, justify="center", width=6, borderwidth=1, relief="solid").grid(row=4, column=0)
    tk.Label(vs_frame.interior, text="HMI_RHT", justify="center", width=20, borderwidth=1, relief="solid").grid(row=4, column=1)
    HMI_spin4d = tk.Spinbox(vs_frame.interior, from_=10, to=25, increment=1.0, justify="center", width=8)
    HMI_spin4d.grid(row=4, column=3)
    tk.Button(vs_frame.interior, text="Click", justify="center", width=8, borderwidth=1, relief="solid", bg="lightgoldenrod",
              command=lambda: HMI_Interface(1, HMIIndex01.get(), HMI_spin4d.get()), pady=0).grid(row=4, column=2)
    
    # HMI_TramStopTime (row 5)
    tk.Label(vs_frame.interior, textvariable=HMIIndex02, justify="center", width=6, borderwidth=1, relief="solid").grid(row=5, column=0)
    tk.Label(vs_frame.interior, text="HMI_TramStopTime", justify="center", width=20, borderwidth=1, relief="solid").grid(row=5, column=1)
    HMI_spin5d = tk.Spinbox(vs_frame.interior, from_=5, to=55, increment=1, justify="center", width=8)
    HMI_spin5d.grid(row=5, column=3)
    tk.Button(vs_frame.interior, text="Click", justify="center", width=8, borderwidth=1, pady=0, relief="solid", bg="lightgoldenrod",
              command=lambda: HMI_Interface(1, HMIIndex02.get(), HMI_spin5d.get())).grid(row=5, column=2)
    
    # Boolean controls (rows 6-7)
    tk.Label(vs_frame.interior, textvariable=HMIIndex03, justify="center", width=6, borderwidth=1, relief="solid").grid(row=6, column=0)
    tk.Label(vs_frame.interior, text="HMI_AllQuietb", justify="center", width=20, borderwidth=1, relief="solid").grid(row=6, column=1)
    tk.Button(vs_frame.interior, text="Snd/Quite", justify="center", width=8, borderwidth=1, relief="solid", bg="lightgoldenrod", pady=0,
              command=lambda: HMI_PB(1, HMIIndex03.get(), 2)).grid(row=6, column=2)
    
    tk.Label(vs_frame.interior, textvariable=HMIIndex04, justify="center", width=6, borderwidth=1, relief="solid").grid(row=7, column=0)
    tk.Label(vs_frame.interior, text="HMI_LIGHTONOFFb", justify="center", width=20, borderwidth=1, relief="solid").grid(row=7, column=1)
    tk.Button(vs_frame.interior, text="Lights", justify="center", width=8, borderwidth=1, relief="solid", bg="lightgoldenrod",
              command=lambda: HMI_PB(1, HMIIndex04.get(), 2), pady=0).grid(row=7, column=2)
    
    # Tram station buttons (rows 22-26)
    HMI_btn22c = tk.Button(vs_frame.interior, text="Bypass/Stop", justify="center", width=8, pady=0, borderwidth=1, relief="solid", bg="lightgoldenrod",
                           command=lambda: HMI_PB(1, HMIIndex18.get(), 2))
    HMI_btn22c.grid(row=22, column=2)
    tk.Label(vs_frame.interior, textvariable=HMIIndex18, justify="center", width=6, borderwidth=1, relief="solid").grid(row=22, column=0)
    tk.Label(vs_frame.interior, text="HMI_TramStpStn_2b", justify="center", width=20, borderwidth=1, relief="solid").grid(row=22, column=1)
    
    HMI_btn23c = tk.Button(vs_frame.interior, text="Bypass/Stop", justify="center", width=8, pady=0, borderwidth=1, relief="solid", bg="lightgoldenrod",
                           command=lambda: HMI_PB(1, HMIIndex19.get(), 2))
    HMI_btn23c.grid(row=23, column=2)
    tk.Label(vs_frame.interior, textvariable=HMIIndex19, justify="center", width=6, borderwidth=1, relief="solid").grid(row=23, column=0)
    tk.Label(vs_frame.interior, text="HMI_TramStpStn_3b", justify="center", width=20, borderwidth=1, relief="solid").grid(row=23, column=1)
    
    HMI_btn25c = tk.Button(vs_frame.interior, text="Bypass/Stop", justify="center", width=8, pady=0, borderwidth=1, relief="solid", bg="lightgoldenrod",
                           command=lambda: HMI_PB(1, HMIIndex20.get(), 2))
    HMI_btn25c.grid(row=25, column=2)
    tk.Label(vs_frame.interior, textvariable=HMIIndex20, justify="center", width=6, borderwidth=1, relief="solid").grid(row=25, column=0)
    tk.Label(vs_frame.interior, text="HMI_TramStpStn_5b", justify="center", width=20, borderwidth=1, relief="solid").grid(row=25, column=1)
    
    HMI_btn26c = tk.Button(vs_frame.interior, text="Bypass/Stop", justify="center", width=8, pady=0, borderwidth=1, relief="solid", bg="lightgoldenrod",
                           command=lambda: HMI_PB(1, HMIIndex21.get(), 2))
    HMI_btn26c.grid(row=26, column=2)
    tk.Label(vs_frame.interior, textvariable=HMIIndex21, justify="center", width=6, borderwidth=1, relief="solid").grid(row=26, column=0)
    tk.Label(vs_frame.interior, text="HMI_TramStpStn_6b", justify="center", width=20, borderwidth=1, relief="solid").grid(row=26, column=1)
    
    # PI column displays
    PI_lbl4h = tk.Label(vs_frame.interior, text="0", justify="center", width=10, borderwidth=1, relief="solid")
    PI_lbl4h.grid(row=4, column=7)
    tk.Label(vs_frame.interior, text="--", justify="center", width=6, borderwidth=3, relief="solid").grid(row=4, column=4)
    tk.Label(vs_frame.interior, text="HMI_RHT", justify="center", width=20, borderwidth=1, relief="solid").grid(row=4, column=5)
    
    PI_lbl5h = tk.Label(vs_frame.interior, text="0", justify="center", width=10, borderwidth=1, relief="solid")
    PI_lbl5h.grid(row=5, column=7)
    tk.Label(vs_frame.interior, text="--", justify="center", width=6, borderwidth=3, relief="solid").grid(row=5, column=4)
    tk.Label(vs_frame.interior, text="HMI_TramStopTime", justify="center", width=20, borderwidth=1, relief="solid").grid(row=5, column=5)
    
    # Speed input controls
    tk.Label(vs_frame.interior, text="50", justify="center", width=6, borderwidth=3, relief="solid").grid(row=1, column=4)
    tk.Label(vs_frame.interior, text="RR1ABspeed_HMI", justify="center", width=20, borderwidth=1, relief="solid").grid(row=1, column=5)
    PI_ent1h = tk.Spinbox(vs_frame.interior, from_=0.1, to=75.4, increment=0.5, justify="center", width=8)
    PI_ent1h.grid(row=1, column=7)
    tk.Button(vs_frame.interior, text="Click", justify="center", width=8, pady=0, borderwidth=1, bg="lightgoldenrod", relief="raised",
              command=lambda: HMI_Interface(1, PIIndex50.get(), PI_ent1h.get())).grid(row=1, column=6)
    
    tk.Label(vs_frame.interior, textvariable=PIIndex51, justify="center", width=6, borderwidth=3, relief="solid").grid(row=2, column=4)
    tk.Label(vs_frame.interior, text="RR1CDspeed_HMI", justify="center", width=20, borderwidth=1, relief="solid").grid(row=2, column=5)
    PI_ent2h = tk.Spinbox(vs_frame.interior, from_=0.2, to=75.4, increment=0.5, justify="center", width=8)
    PI_ent2h.grid(row=2, column=7)
    tk.Button(vs_frame.interior, text="Click", justify="center", width=8, pady=0, borderwidth=1, bg="lightgoldenrod", relief="raised",
              command=lambda: HMI_Interface(1, PIIndex51.get(), PI_ent2h.get())).grid(row=2, column=6)
    
    tk.Label(vs_frame.interior, textvariable=PIIndex52, justify="center", width=6, borderwidth=3, relief="solid").grid(row=3, column=4)
    tk.Label(vs_frame.interior, text="RR2ABspeed_HMI", justify="center", width=20, borderwidth=1, relief="solid").grid(row=3, column=5)
    PI_ent3h = tk.Spinbox(vs_frame.interior, from_=0.3, to=75.4, increment=0.5, justify="center", width=8)
    PI_ent3h.grid(row=3, column=7)
    tk.Button(vs_frame.interior, text="Click", justify="center", width=8, pady=0, borderwidth=1, bg="lightgoldenrod", relief="raised",
              command=lambda: HMI_Interface(1, PIIndex52.get(), PI_ent3h.get())).grid(row=3, column=6)
    
    # Switch feedback display
    PI_lbl14h = tk.Label(vs_frame.interior, text="--", justify="center", width=10, borderwidth=1, relief="solid")
    PI_lbl14h.grid(row=10, column=7)
    
    # Print buttons and server update controls
    tk.Button(vs_frame.interior, text="Print HMI db", justify="center", width=10, pady=0, borderwidth=1, bg="springgreen",
              relief="raised", command=lambda: Print("HMI")).grid(row=3, column=8)
    tk.Button(vs_frame.interior, text="Print PI db", justify="center", width=10, pady=0, borderwidth=1, bg="springgreen",
              relief="raised", command=lambda: Print("PI")).grid(row=4, column=8)
    tk.Button(vs_frame.interior, text="Print ALL db", justify="center", width=10, pady=0, borderwidth=1, bg="springgreen",
              relief="raised", command=lambda: Print("ALL")).grid(row=5, column=8)
    tk.Button(vs_frame.interior, text="Print Server db", justify="center", width=10, pady=0, borderwidth=1, bg="goldenrod",
              relief="raised", command=lambda: Print("Server")).grid(row=6, column=8)
    
    tk.Label(vs_frame.interior, text="Poll Interval (sec)", justify="center", width=20, pady=0, borderwidth=1, bg="springgreen", relief="raised").grid(row=7, column=8)
    
    var1 = tk.DoubleVar(vs_frame.interior)
    var1.set(1.0)
    UpdateServerspin = tk.Spinbox(vs_frame.interior, from_=0.100, to=5.00, increment=0.5, textvariable=var1,
                                  justify="center", width=18, format="%.03f", font=('Times new roman', 14, 'bold'))
    UpdateServerspin.grid(row=8, column=8)
    
    # Terminal display
    tk.Label(vs_frame.interior, text="TERMINAL", borderwidth=1, relief="solid", justify="center", width=25, font=('Times new roman', 12, 'bold'), bg="lightgrey").grid(row=20, column=8, columnspan=1)
    Terminal = tk.Label(vs_frame.interior, text=terminal, justify="left", width=30, height=2, padx=0, pady=0, borderwidth=1, bg="aqua", font=('Times new roman', 10, 'bold'))
    Terminal.grid(row=21, column=8, columnspan=1, rowspan=2)
    
    # Connection status label
    connection_status = tk.Label(vs_frame.interior, text="Connecting...", justify="center", width=20, borderwidth=2, relief="solid", bg="yellow", font=('Times new roman', 10, 'bold'))
    connection_status.grid(row=2, column=8)
    
    def update_connection_status():
        """Update connection status display."""
        if rest_client.connected:
            connection_status.configure(text="Connected (REST)", bg="lawngreen")
        else:
            connection_status.configure(text="Disconnected", bg="salmon")
        root.after(2000, update_connection_status)
    
    # Start connection and polling in background thread
    def start_connection():
        global terminal
        success, message = connect_to_server(rest_client, GUIdb, query, max_retries=10)
        terminal = message
    
    # Initialize updates and start polling
    connection_thread = threading.Thread(target=start_connection, daemon=True)
    connection_thread.start()
    
    # Start periodic UI updates
    UpdateSpeed1a()
    UpdateSpeed1c()
    UpdateHMIRHT()
    UpdateHMI_TramStopTime()
    UpdatePISwitch1()
    Time()
    update_connection_status()
    
    # Start REST polling after a short delay to allow connection
    root.after(2000, lambda: poll_server_via_rest(rest_client, GUIdb, root, UpdateServerspin))
    
    # Run the main loop
    root.mainloop()
