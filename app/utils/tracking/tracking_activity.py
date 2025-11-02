# --- Imports des bibliothèques standards (intégrées à Python) ---
import json  # Pour gérer le fichier JSON
import time  # Pour l'horodatage (timestamping)
import os
import threading

# --- Imports des bibliothèques tierces (celles que vous avez installées) ---
import psutil                 # Pour les processus, le réseau, le CPU
import pyperclip              # Pour le presse-papiers
import pygetwindow as gw      # Pour le titre de la fenêtre active
import mss                    # Pour les captures d'écran (rapide)
from pynput.keyboard import Listener as KeyboardListener      # Pour le clavier
from pynput.mouse import Listener as MouseListener            # Pour la souris

_tracking_folder_path = "tracking"
_last_title = None
_last_clipboard = ""
_known_pids = set()
_event_log = []
stop_event = threading.Event()
_running_lstnr = {
    "keyboard": None,
    "mouse": None
}

def tracking(duration, output):
    _start_tracking_activity()
    stop_event.wait(duration)
    _stop_tracking_activity()
    _take_screenshot()
    output["json_path"]=_save_log_to_json()

def stop_tracking():
    stop_event.set()

def _start_tracking_activity():
    stop_event.clear()
    _start_all_tracking_event()

def _start_all_tracking_event():
    tasks = [
        (_start_kbd_lstnr, ()),
        (_start_mouse_lstnr, ()),
        (_window_tracker_loop, ()),
        (_screenshot_loop, ()),
        (_clipboard_tracker_loop, ()),
        (_new_process_loop, ())
    ]
    for task_func, task_args in tasks:
        thread = threading.Thread(target=task_func, args=task_args, daemon=True)
        thread.start()

def _stop_tracking_activity():
    stop_event.set()
    if _running_lstnr["mouse"]:
        _running_lstnr["mouse"].stop()


def _add_to_log(data_dict):
    data_dict["timestamp"] = time.time()
    _event_log.append(data_dict)

def _get_active_window_title():
    try:
        active_window = gw.getActiveWindow()
        if active_window:
            return active_window.title
    except Exception as e:
        pass
    return None

def _start_lstnr(name, lstnr):
    _running_lstnr[name] = lstnr
    lstnr.join()
    




# Keyboard
def _start_kbd_lstnr():
    with KeyboardListener(on_press=_log_keystroke) as lstnr:
        _start_lstnr("keyboard", lstnr)

def _log_keystroke(key):
    data = {
        "type": "keystroke",
        "key": str(key)
    }
    _add_to_log(data)





# Mouse
def _start_mouse_lstnr():
    with MouseListener(on_click=_log_mouse_click) as lstnr:
        _start_lstnr("mouse", lstnr)

def _log_mouse_click(x, y, button, pressed):
    if pressed:
        data = {
            "type": "mouse_click",
            "x": x,
            "y": y,
            "button": str(button),
            "window_title": _get_active_window_title()
        }
        _add_to_log(data)





# Window
def _window_tracker_loop(interval=1):
    while not stop_event.is_set():
        _log_active_window()
        stop_event.wait(interval)

def _log_active_window():
    global _last_title
    title = _get_active_window_title()
    if title and title != _last_title:
        _last_title = title
        data = {
            "type": "window_change",
            "title": title
        }
        _add_to_log(data)





# screenshots
# screenshots
def _screenshot_loop(output_dir = "screenshots", interval = 1):
    if not os.path.exists(_tracking_folder_path):
        os.makedirs(_tracking_folder_path)
    output_dir_path = f"{_tracking_folder_path}/{output_dir}"
    if not os.path.exists(output_dir_path):
        os.makedirs(output_dir_path)
    while not stop_event.is_set():
        file_name = f"{output_dir_path}/screenshot_{int(time.time())}.jpeg"
        try:
            with mss.mss() as sct:
                sct.shot(output=file_name)
                data = {
                    "type": "screenshot",
                    "file_path": file_name,
                    "window_title" : _get_active_window_title()
                }
                _add_to_log(data)
        except Exception as e:
            print (f"Erreur MSS: {e}")
        stop_event.wait(interval)

def _take_screenshot(output_dir="screenshots"):

    output_dir_path = f"{_tracking_folder_path}/{output_dir}"

    # Nom de fichier simplifié, sans suffixe
    file_name = f"{output_dir_path}/screenshot_{int(time.time())}.jpeg"
    try:
        with mss.mss() as sct:
            sct.shot(output=file_name)
            data = {
                "type": "screenshot",
                "file_path": file_name,
                "window_title": _get_active_window_title()
            }
            _add_to_log(data)
    except Exception as e:
        print(f"Erreur MSS lors de la capture : {e}")


# clipboard
def _clipboard_tracker_loop(interval=1):
    global _last_clipboard
    _last_clipboard = pyperclip.paste()
    while not stop_event.is_set():
        _log_clipboard()
        stop_event.wait(interval)

def _log_clipboard():
    global _last_clipboard
    try:
        content = pyperclip.paste()
        if content and content != _last_clipboard :
            _last_clipboard = content
            data = {
                "type": "clipboard_copy",
                "content": content   
            }
            _add_to_log(data)
    except Exception as e:
        pass




# new prossess
def _new_process_loop(interval=1):
    global _known_pids 
    _known_pids = set(psutil.pids())
    while not stop_event.is_set():
        _log_new_process()
        stop_event.wait(interval)


def _log_new_process():
    global _known_pids
    try:
        cur_pids = set(psutil.pids())
        new_pids = cur_pids - _known_pids
        for pid in new_pids:
            try:
                p = psutil.Process(pid)
                data={
                    "type": "process_start",
                    "pid": pid,
                    "name": p.name(),
                    "username": p.username()  
                }
                _add_to_log(data)
            except Exception:
                pass
        _known_pids = cur_pids
    except Exception as e:
        print(f"Erreur PSUtil: {e}")





def _save_log_to_json(output_dir = "intrusions", file_name="intrusion_log"):
    if not os.path.exists(_tracking_folder_path):
        os.makedirs(_tracking_folder_path)
    output_dir_path = f"{_tracking_folder_path}/{output_dir}"
    if not os.path.exists(output_dir_path):
        os.makedirs(output_dir_path)
    try:
        json_path = f"{output_dir_path}/{file_name}_{int(time.time())}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(_event_log, f, indent=4)
        return json_path
    except Exception as e:
        print(f"Log to JSON Error : {e}")
        return None