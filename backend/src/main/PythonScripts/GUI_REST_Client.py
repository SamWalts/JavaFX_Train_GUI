"""
GUI REST Client - Replacement for GUI19WithServer.py
A Tkinter-based GUI that communicates with the REST server via HTTP endpoints.
This replaces the socket-based communication with REST API calls.

This GUI mimics the PI sending updates to HMI (always sets HMI_READi=1).

Usage:
    1. Start the REST server: python rest_server.py
    2. Run this GUI client: python GUI_REST_Client.py
"""
from tkinter import ttk
import tkinter as tk
import functools
from time import strftime
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

# Dictionary to hold dynamic UI elements for updating
value_labels = {}


class VerticalScrolledFrame(ttk.Frame):
    """A scrollable frame widget for Tkinter."""
    
    def __init__(self, parent, *args, **kw):
        ttk.Frame.__init__(self, parent, *args, **kw)
        
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
        
        def _on_mousewheel_mac(event):
            # On macOS, delta is usually small (1-4), scroll one unit at a time
            if event.delta > 0:
                canvas.yview_scroll(-1, "units")
            elif event.delta < 0:
                canvas.yview_scroll(1, "units")

        def _bind_to_mousewheel(event):
            canvas.bind_all("<Button-4>", fp(_on_mousewheel, scroll=-1))
            canvas.bind_all("<Button-5>", fp(_on_mousewheel, scroll=1))
            # Also bind for macOS
            canvas.bind_all("<MouseWheel>", _on_mousewheel_mac)

        def _unbind_from_mousewheel(event):
            canvas.unbind_all("<Button-4>")
            canvas.unbind_all("<Button-5>")
            canvas.unbind_all("<MouseWheel>")

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
        self.interior = interior = ttk.Frame(canvas)
        interior_id = canvas.create_window(0, 0, window=interior, anchor=tk.NW)
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
    root.geometry("1400x900+50+50")
    root.title("Train Control GUI (REST API Client) - PI Simulator (HMI_READi=1)")

    # Create main container frame
    main_frame = tk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Create the VerticalScrolledFrame for the data table
    vs_frame = VerticalScrolledFrame(main_frame)
    vs_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Create a side panel for controls
    control_frame = tk.Frame(main_frame, width=250, bg="lightgray")
    control_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)
    control_frame.pack_propagate(False)

    # Helper function for updating values - ALWAYS sets HMI_READi=1 (PI to HMI)
    def update_integer_value(index, spinbox):
        """Update integer value (HMI_VALUEi) and set HMI_READi=1."""
        try:
            value = int(spinbox.get())
            GUIdb.update({"HMI_VALUEi": value, "HMI_READi": 1}, query.INDEX == index)
            logger.info(f"Updated INDEX {index}: HMI_VALUEi={value}, HMI_READi=1")
        except ValueError:
            logger.warning(f"Invalid integer value for INDEX {index}")

    def update_float_value(index, spinbox):
        """Update float value (PI_VALUEf) and set HMI_READi=1."""
        try:
            value = float(spinbox.get())
            GUIdb.update({"PI_VALUEf": value, "HMI_READi": 1}, query.INDEX == index)
            logger.info(f"Updated INDEX {index}: PI_VALUEf={value}, HMI_READi=1")
        except ValueError:
            logger.warning(f"Invalid float value for INDEX {index}")

    def toggle_hmi_bool(index):
        """Toggle HMI_VALUEb and set HMI_READi=1."""
        temp = GUIdb.get(query.INDEX == index)
        if temp:
            current = temp.get("HMI_VALUEb", False)
            new_value = not current if current is not None else True
            GUIdb.update({"HMI_VALUEb": new_value, "HMI_READi": 1}, query.INDEX == index)
            logger.info(f"Updated INDEX {index}: HMI_VALUEb={new_value}, HMI_READi=1")

    def toggle_pi_bool(index):
        """Toggle PI_VALUEb and set HMI_READi=1."""
        temp = GUIdb.get(query.INDEX == index)
        if temp:
            current = temp.get("PI_VALUEb", False)
            new_value = not current if current is not None else True
            GUIdb.update({"PI_VALUEb": new_value, "HMI_READi": 1}, query.INDEX == index)
            logger.info(f"Updated INDEX {index}: PI_VALUEb={new_value}, HMI_READi=1")

    def Print(who):
        """Print database contents."""
        if who == "HMI":
            for i in range(1, 50):
                temp = GUIdb.get(query['INDEX'] == i)
                if temp:
                    print(temp)
        elif who == "PI":
            for i in range(50, 81):
                temp = GUIdb.get(query['INDEX'] == i)
                if temp:
                    print(temp)
        elif who == "ALL":
            for row in GUIdb:
                print(row)
        elif who == "Server":
            data = rest_client.print_server_db()
            if data:
                for row in data:
                    print(row)
    
    def refresh_display():
        """Refresh all value displays from the database."""
        for idx, labels in value_labels.items():
            temp = GUIdb.get(query.INDEX == idx)
            if temp:
                if 'hmi_valuei' in labels:
                    labels['hmi_valuei'].configure(text=str(temp.get("HMI_VALUEi", 0)))
                if 'hmi_valueb' in labels:
                    val = temp.get("HMI_VALUEb")
                    color = "lawngreen" if val else "salmon" if val is not None else "gray"
                    labels['hmi_valueb'].configure(text=str(val), bg=color)
                if 'pi_valuef' in labels:
                    labels['pi_valuef'].configure(text=str(temp.get("PI_VALUEf", 0.0)))
                if 'pi_valueb' in labels:
                    val = temp.get("PI_VALUEb")
                    color = "lawngreen" if val else "salmon" if val is not None else "gray"
                    labels['pi_valueb'].configure(text=str(val), bg=color)
                if 'hmi_readi' in labels:
                    readi = temp.get("HMI_READi", 0)
                    color = "white"
                    if readi == 1:
                        color = "yellow"
                    elif readi == 2:
                        color = "cyan"
                    labels['hmi_readi'].configure(text=str(readi), bg=color)

        # Schedule next refresh
        root.after(500, refresh_display)

    # --- Build Header Row ---
    headers = ["IDX", "TAG", "HMI_VALUEi", "Set Int", "HMI_VALUEb", "Toggle",
               "PI_VALUEf", "Set Float", "PI_VALUEb", "Toggle", "HMI_READi"]
    header_widths = [5, 20, 10, 8, 10, 8, 10, 8, 10, 8, 8]

    for col, (header, width) in enumerate(zip(headers, header_widths)):
        tk.Label(vs_frame.interior, text=header, width=width, borderwidth=1,
                relief="solid", font=('Arial', 9, 'bold'), bg="lightblue").grid(row=0, column=col, sticky="nsew")

    # --- Dynamically Build Rows for All Database Entries ---
    # Get all records sorted by INDEX
    all_records = sorted(GUIdb.all(), key=lambda x: x.get("INDEX", 0))

    for row_num, record in enumerate(all_records, start=1):
        idx = record.get("INDEX", 0)
        tag = record.get("TAG", "")

        value_labels[idx] = {}

        # INDEX
        tk.Label(vs_frame.interior, text=str(idx), width=5, borderwidth=1,
                relief="solid", font=('Arial', 9)).grid(row=row_num, column=0, sticky="nsew")

        # TAG
        tk.Label(vs_frame.interior, text=tag, width=20, borderwidth=1,
                relief="solid", font=('Arial', 8), anchor="w").grid(row=row_num, column=1, sticky="nsew")

        # HMI_VALUEi - display
        hmi_i_label = tk.Label(vs_frame.interior, text=str(record.get("HMI_VALUEi", 0)),
                              width=10, borderwidth=1, relief="solid", font=('Arial', 9))
        hmi_i_label.grid(row=row_num, column=2, sticky="nsew")
        value_labels[idx]['hmi_valuei'] = hmi_i_label

        # HMI_VALUEi - spinbox and button frame
        int_frame = tk.Frame(vs_frame.interior)
        int_frame.grid(row=row_num, column=3, sticky="nsew")
        int_spin = tk.Spinbox(int_frame, from_=0, to=100, increment=1, width=5, font=('Arial', 8))
        int_spin.pack(side=tk.LEFT)
        int_spin.delete(0, tk.END)
        int_spin.insert(0, str(record.get("HMI_VALUEi", 0)))
        tk.Button(int_frame, text="Set", font=('Arial', 7), bg="lightyellow",
                 command=lambda i=idx, s=int_spin: update_integer_value(i, s)).pack(side=tk.LEFT)

        # HMI_VALUEb - display
        hmi_b_val = record.get("HMI_VALUEb")
        hmi_b_color = "lawngreen" if hmi_b_val else "salmon" if hmi_b_val is not None else "gray"
        hmi_b_label = tk.Label(vs_frame.interior, text=str(hmi_b_val), width=10, borderwidth=1,
                              relief="solid", font=('Arial', 9), bg=hmi_b_color)
        hmi_b_label.grid(row=row_num, column=4, sticky="nsew")
        value_labels[idx]['hmi_valueb'] = hmi_b_label

        # HMI_VALUEb - toggle button
        tk.Button(vs_frame.interior, text="Toggle", width=6, font=('Arial', 7), bg="lightgoldenrod",
                 command=lambda i=idx: toggle_hmi_bool(i)).grid(row=row_num, column=5, sticky="nsew")

        # PI_VALUEf - display
        pi_f_label = tk.Label(vs_frame.interior, text=str(record.get("PI_VALUEf", 0.0)),
                             width=10, borderwidth=1, relief="solid", font=('Arial', 9))
        pi_f_label.grid(row=row_num, column=6, sticky="nsew")
        value_labels[idx]['pi_valuef'] = pi_f_label

        # PI_VALUEf - spinbox and button frame
        float_frame = tk.Frame(vs_frame.interior)
        float_frame.grid(row=row_num, column=7, sticky="nsew")
        float_spin = tk.Spinbox(float_frame, from_=0.0, to=100.0, increment=0.5, width=5, font=('Arial', 8), format="%.1f")
        float_spin.pack(side=tk.LEFT)
        float_spin.delete(0, tk.END)
        float_spin.insert(0, str(record.get("PI_VALUEf", 0.0)))
        tk.Button(float_frame, text="Set", font=('Arial', 7), bg="lightyellow",
                 command=lambda i=idx, s=float_spin: update_float_value(i, s)).pack(side=tk.LEFT)

        # PI_VALUEb - display
        pi_b_val = record.get("PI_VALUEb")
        pi_b_color = "lawngreen" if pi_b_val else "salmon" if pi_b_val is not None else "gray"
        pi_b_label = tk.Label(vs_frame.interior, text=str(pi_b_val), width=10, borderwidth=1,
                             relief="solid", font=('Arial', 9), bg=pi_b_color)
        pi_b_label.grid(row=row_num, column=8, sticky="nsew")
        value_labels[idx]['pi_valueb'] = pi_b_label

        # PI_VALUEb - toggle button
        tk.Button(vs_frame.interior, text="Toggle", width=6, font=('Arial', 7), bg="lightgoldenrod",
                 command=lambda i=idx: toggle_pi_bool(i)).grid(row=row_num, column=9, sticky="nsew")

        # HMI_READi - display
        readi_val = record.get("HMI_READi", 0)
        readi_color = "white"
        if readi_val == 1:
            readi_color = "yellow"
        elif readi_val == 2:
            readi_color = "cyan"
        readi_label = tk.Label(vs_frame.interior, text=str(readi_val), width=8, borderwidth=1,
                              relief="solid", font=('Arial', 9), bg=readi_color)
        readi_label.grid(row=row_num, column=10, sticky="nsew")
        value_labels[idx]['hmi_readi'] = readi_label

    # --- Control Panel Widgets ---
    tk.Label(control_frame, text="CONTROLS", font=('Arial', 12, 'bold'), bg="lightgray").pack(pady=10)

    # Time display
    time_string = strftime('%H:%M:%S')
    tk.Label(control_frame, text="TIME", font=('Arial', 10, 'bold'), bg="lightgray").pack(pady=5)
    timelbl = tk.Label(control_frame, text=time_string, font=('Helvetica', 14), bg='purple', fg='white', width=10)
    timelbl.pack(pady=5)

    def update_time():
        timelbl.configure(text=strftime('%H:%M:%S'))
        timelbl.after(1000, update_time)

    # Connection status
    tk.Label(control_frame, text="STATUS", font=('Arial', 10, 'bold'), bg="lightgray").pack(pady=5)
    connection_status = tk.Label(control_frame, text="Connecting...", font=('Arial', 10), bg="yellow", width=18)
    connection_status.pack(pady=5)

    def update_connection_status():
        if rest_client.connected:
            connection_status.configure(text="Connected (REST)", bg="lawngreen")
        else:
            connection_status.configure(text="Disconnected", bg="salmon")
        root.after(2000, update_connection_status)
    
    # Poll interval
    tk.Label(control_frame, text="Poll Interval (sec)", font=('Arial', 10, 'bold'), bg="lightgray").pack(pady=10)
    var1 = tk.DoubleVar(control_frame)
    var1.set(1.0)
    UpdateServerspin = tk.Spinbox(control_frame, from_=0.100, to=5.00, increment=0.5, textvariable=var1,
                                  justify="center", width=10, format="%.03f", font=('Arial', 12))
    UpdateServerspin.pack(pady=5)

    # Print buttons
    tk.Label(control_frame, text="DEBUG", font=('Arial', 10, 'bold'), bg="lightgray").pack(pady=10)
    tk.Button(control_frame, text="Print HMI db", width=15, bg="springgreen",
              command=lambda: Print("HMI")).pack(pady=3)
    tk.Button(control_frame, text="Print PI db", width=15, bg="springgreen",
              command=lambda: Print("PI")).pack(pady=3)
    tk.Button(control_frame, text="Print ALL db", width=15, bg="springgreen",
              command=lambda: Print("ALL")).pack(pady=3)
    tk.Button(control_frame, text="Print Server db", width=15, bg="goldenrod",
              command=lambda: Print("Server")).pack(pady=3)
    tk.Button(control_frame, text="Check Pending", width=15, bg="orange",
              command=lambda: rest_client.check_pending_on_server()).pack(pady=3)

    # Terminal display
    tk.Label(control_frame, text="TERMINAL", font=('Arial', 10, 'bold'), bg="lightgray").pack(pady=10)
    Terminal = tk.Label(control_frame, text=terminal, justify="left", width=25, height=3,
                       borderwidth=1, bg="aqua", font=('Arial', 9), wraplength=200)
    Terminal.pack(pady=5)

    def update_terminal():
        Terminal.configure(text=terminal)
        Terminal.after(1000, update_terminal)

    # Legend
    tk.Label(control_frame, text="LEGEND", font=('Arial', 10, 'bold'), bg="lightgray").pack(pady=10)
    tk.Label(control_frame, text="HMI_READi:", font=('Arial', 9), bg="lightgray").pack()
    legend_frame = tk.Frame(control_frame, bg="lightgray")
    legend_frame.pack(pady=5)
    tk.Label(legend_frame, text="0=Idle", bg="white", width=8, font=('Arial', 8)).pack(side=tk.LEFT, padx=2)
    tk.Label(legend_frame, text="1=PI→HMI", bg="yellow", width=8, font=('Arial', 8)).pack(side=tk.LEFT, padx=2)
    tk.Label(legend_frame, text="2=HMI→PI", bg="cyan", width=8, font=('Arial', 8)).pack(side=tk.LEFT, padx=2)

    # Note about this GUI
    tk.Label(control_frame, text="This GUI simulates\nPI sending to HMI\n(always HMI_READi=1)",
            font=('Arial', 9, 'italic'), bg="lightgray", fg="darkblue").pack(pady=10)

    # Start connection in background thread
    def start_connection():
        global terminal
        success, message = connect_to_server(rest_client, GUIdb, query, max_retries=10)
        terminal = message
    
    connection_thread = threading.Thread(target=start_connection, daemon=True)
    connection_thread.start()
    
    # Start periodic updates
    update_time()
    update_connection_status()
    update_terminal()
    refresh_display()

    # Start REST polling after a short delay to allow connection
    root.after(2000, lambda: poll_server_via_rest(rest_client, GUIdb, root, UpdateServerspin))
    
    # Run the main loop
    root.mainloop()
