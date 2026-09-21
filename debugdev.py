#!/usr/bin/env python3

# File: debug.py
# Author: Hadi Cahyadi <cumulus13@gmail.com>
# Date: 2026-01-04
# Description: 
# License: MIT
#-*- encoding: utf-8 -*-
#encoding: utf-8

from __future__ import print_function

import argparse
import os
import sys
if sys.platform == 'win32':
    import win32api  # type: ignore
import traceback
from pathlib import Path

from datetime import datetime

RICH_AVAILABLE = False
MAKE_COLORS_AVAILABLE = False
ENVDOT_AVAILABLE = False
RICH_AVAILABLE = False
MAKE_COLORS_AVAILABLE = False
USE_SQL = False
USE_DEFAULT_CONFIG = False
PID = os.getpid()
HANDLE = None
tprint = None  # type: ignore
END_MARKER = b"<END>"
CONFIGFILE = str(Path(__file__).parent / 'debug.ini')
DEBUG = True if str(os.getenv('DEBUG', '0')).lower() in ['1', 'true', 'yes', 'ok', 'on'] else False

import time
import shutil

try:
    from envdot import load_env  # type: ignore
    ENVDOT_AVAILABLE = True
    CONFIG = load_env()
except:
    pass

LOG_LEVEL = os.getenv('LOG_LEVEL', "CRITICAL")

if len(sys.argv) > 1 and any('--debug' == arg for arg in sys.argv):
    print("🐞 Debug mode enabled")
    os.environ['LOGGING'] = "1"
    os.environ.pop('NO_LOGGING', None)
    os.environ['TRACEBACK'] = "1"
    os.environ["LOGGING"] = "1"
    LOG_LEVEL = "DEBUG"
else:
    os.environ['NO_LOGGING'] = "1"

exceptions = os.getenv('LOG_EXCEPTIONS', ['socket', 'gntplib', 'sqlalchemy'], cast_type=list)  # type: ignore

try:
    from richcolorlog import setup_logging, print_exception as tprint  # type: ignore
    logger = setup_logging(
        name="pydebugger",
        level=LOG_LEVEL,
        log_file_name=os.getenv("LOG_FILE_NAME", "pydebugger.log"),
        log_file=os.getenv("LOG_FILE", True),
        syslog=os.getenv("LOG_SYSLOG", True),
        syslog_host=os.getenv('SYSLOG', 'HOST', "127.0.0.1"),  # type: ignore
        syslog_port=os.getenv('SYSLOG', 'PORT', 518),  # type: ignore
        exceptions=exceptions
    )
    HAS_RICHCOLORLOG=True
except:
    HAS_RICHCOLORLOG=False
    import logging

    try:
        from .custom_logging import get_logger  # type: ignore
    except ImportError:
        from custom_logging import get_logger  # type: ignore
    
    for exc in exceptions:
        logging.getLogger(exc).setLevel(logging.CRITICAL)

    logger = get_logger('pydebugger', level=getattr(logging, LOG_LEVEL.upper(), logging.CRITICAL))

if not tprint:
    def tprint(*args, **kwargs):
        traceback.print_exc()

try:
    from licface import CustomRichHelpFormatter
except:
    CustomRichHelpFormatter = argparse.RawDescriptionHelpFormatter

if not ENVDOT_AVAILABLE:
    try:
        from .config import CONFIG
        USE_DEFAULT_CONFIG = True
    except Exception as e:
        try:
            from config import CONFIG
            USE_DEFAULT_CONFIG = True
        except:
            pass

try:
    from rich import traceback as rich_traceback, console
    console = console.Console(width = shutil.get_terminal_size()[0])
    rich_traceback.install(theme = 'fruity', max_frames = 30, width = shutil.get_terminal_size()[0])
    from rich.syntax import Syntax
    RICH_AVAILABLE = True
except:
    pass

try:
    from make_colors import make_colors  # type: ignore
    MAKE_COLORS_AVAILABLE = True
except:
    pass

import inspect
import random
import socket
import datetime
import re
import ctypes
from urllib.parse import quote_plus
import socket
from collections import OrderedDict
import signal

from typing import Any, Callable, Dict, List, Optional, Union, Tuple

try:
    from sqlalchemy import create_engine, Column, Integer, Text, text, func, TIMESTAMP #, String, Boolean, TIMESTAMP, BigInteger, Text
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker
    USE_SQL = True
    Base = declarative_base()
except:
    pass

def get_debug_server(ENV='DEBUG_SERVER'):
    DEBUG_SERVER = []
    if os.getenv(ENV, cast_type=list):  # type: ignore
        DEBUG_SERVER = os.getenv(ENV, cast_type=list)  # type: ignore
        for item in items:  # type: ignore
            if str(item).isdigit():
                DEBUG_SERVER[items.index(item)] = f"127.0.0.1:{item.strip()}"  # type: ignore
    return DEBUG_SERVER

force = False

def get_width():
    return shutil.get_terminal_size()[0]
    
def get_source(source, lexer='python', theme='fruity', ln = True, tab_size = 2, width=get_width(), word_wrap = True, **kwargs):
    if RICH_AVAILABLE:
        if sys.version_info.major == 3:
            console.print(  # type: ignore
                Syntax(  # type: ignore
                    inspect.getsource(source), 
                    lexer, 
                    theme = theme, 
                    line_numbers=ln or kwargs.get('line_numbers', None),  # type: ignore 
                    tab_size=tab_size, 
                    code_width=width, 
                    word_wrap = word_wrap
                    )
                )
            
        else:
            try:
                cmd = """python3 -c \"import {};import inspect;from rich.console import Console;from rich.syntax import Syntax;console = Console();console.print(Syntax(inspect.getsource({}), 'python', theme = 'fruity', line_numbers=True, tab_size=2, code_width={}))\"""".format(source.__module__, source.__module__, get_width())
                os.system(cmd)
            except:
                cmd = """python3 -c \"import {};import inspect;from rich.console import Console;from rich.syntax import Syntax;console = Console();console.print(Syntax(inspect.getsource({}), 'python', theme = 'fruity', line_numbers=True, tab_size=2, code_width={}))\"""".format(source.__name__, source.__name__, get_width())
                os.system(cmd)

def serve(host = '0.0.0.0', port = 50001, on_top=False):
    END_MARKER = b'<END>'    
    logger.debug(f"END_MARKER: {END_MARKER}, TYPE: {type(END_MARKER)}")
    on_top = os.getenv('DISPLAY_ON_TOP', False)
    logger.debug(f"ON_TOP: {on_top}, TYPE: {type(on_top)}")
    
    def receive_message(server_socket):
        full_message = b''
        while True:
            try:
                #chunk = server_socket.recv(os.getenv('BUFFER_SIZE', 4096)).decode() #TCP
                chunk, _ = server_socket.recvfrom(os.getenv('BUFFER_SIZE', 4096)) #UDP
            except socket.timeout:   # <<< extra so it doesn't hang
                return b''

            if END_MARKER in chunk:
                full_message += chunk.replace(END_MARKER, b'')
                break
            full_message += chunk
        return full_message
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((host, port))    
    server_socket.settimeout(1.0)  # <<< additionally so you can Ctrl+C

    if RICH_AVAILABLE:
        console.print(f"[bold #AAAAFF]Debug server started[/] [bold #00FFFF]{host}[/]:[bold #FFFF00]{port}[/]. [bold #FF557F]Waiting for messages...[/]")  # type: ignore
    elif MAKE_COLORS_AVAILABLE:
        print(make_colors("BIND: ", 'white', 'green') + make_colors(host, 'white', 'red', attrs= ['bold']) + ":" + make_colors(str(port), 'black', 'yellow', attrs= ['bold']))  # type: ignore
    else:
        print(f"Debug server started {host}:{port}. Waiting for messages...")
    try:
        while True:
            #client_socket, client_address = server_socket.accept() #TCP
            #print(f"Connected to {client_address}")
            
            #msg = receive_message(client_socket) #TCP
            msg = receive_message(server_socket)
            
            if msg:
                if CONFIG.get_config('display', 'raise') in [1, '1', 'True', True]:
                    showme_no_delay()
                    
                if hasattr(msg, 'decode'):
                    #msg = msg.decode('utf-8')
                    msg = msg.decode(errors = 'replace')
                    
                if msg == 'cls' or msg == 'clear':
                    if sys.platform == 'win32':
                        os.system('cls')
                    else:
                        os.system('clear')  # type: ignore
                else:
                    print(msg)
                    
                print("=" * get_width())
    
            #server_socket.close() #TCP
            
    except KeyboardInterrupt:
        if RICH_AVAILABLE:
            console.print("[bold #FF5555]Server shutdown ...[/]")  # type: ignore
        elif MAKE_COLORS_AVAILABLE:
            print(make_colors("server shutdown ...", 'lw', 'r'))  # type: ignore
        else:
            print("Server shutdown ...")
    finally:
        server_socket.close()
        if RICH_AVAILABLE:
            console.print("[bold #FFFF00]Socket closed, server terminated gracefully.[/]")  # type: ignore
        elif MAKE_COLORS_AVAILABLE:
            print(make_colors("Socket closed, server terminated gracefully.", 'lw', 'g'))  # type: ignore
        else:
            print("Socket closed, server terminated gracefully.")
        os.kill(PID, signal.SIGTERM)
        
def set_detach(width=700, height=400, x=10, y=50, monitor_index=0, center=False, buffer_column=9000, buffer_row=77, on_top=True):
    if sys.platform != 'win32':
        return False

    from dcmd import dcmd
    setting = dcmd()
    setting.setBuffer(buffer_row, buffer_column)

    # Take all monitors (left, top, right, bottom)
    monitors = win32api.EnumDisplayMonitors()
    if monitor_index >= len(monitors):
        monitor_index = 0  # fallback ke primary monitor

    _, _, (left, top, right, bottom) = monitors[monitor_index]
    screen_width = right - left
    screen_height = bottom - top

    # Calculate the window position
    if center:
        x = left + (screen_width - width) // 2
        y = top + (screen_height - height) // 2
    else:
        x = left + x
        y = top + y

    # Set size and position
    setting.setSize(width, height, x, y, center)
    if on_top:
        setting.setAlwaysOnTop(width, height, x, y, center)

    return True

def showme_no_delay():
    """
    Version without delay - faster but perhaps less reliable
    """
    if not sys.platform == 'win32':
        return False
    
    global HANDLE
    if not HANDLE:
        return False
    
    # Save the currently active window
    current_foreground = ctypes.windll.user32.GetForegroundWindow()
    
    # Raise window target
    ctypes.windll.user32.SetForegroundWindow(HANDLE)
    
    # Immediately return focus    if current_foreground and current_foreground != HANDLE:
    ctypes.windll.user32.SetForegroundWindow(current_foreground)
    
    return True

def cleanup(filename, dry_run = False, verbose = False):
    
    if verbose or dry_run:
        print("=== CLEANUP FUNCTION - SMART DEBUG REMOVAL ===")
        print(f"Processing: {filename}")
    
    # Check if file exists
    if not os.path.exists(filename):
        logger.error(f"File {filename} not found!", show = True)
        return
    
    file_dir = os.path.dirname(filename) or '.'
    file_name = os.path.basename(filename)
    name_without_ext, ext = os.path.splitext(file_name)
    
    if verbose or dry_run:
        print(f"Directory: {file_dir}")
        print(f"Filename: {file_name}")
        print(f"Name: {name_without_ext}")
        print(f"Extension: {ext}")
    
    # Create backup
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S%f')  # type: ignore
    backup_name = f"{name_without_ext}_{timestamp}{ext}"
    backup_path = os.path.join(file_dir, backup_name)
    shutil.copyfile(filename, backup_path)
    if verbose or dry_run: print(f"Backup: {backup_name}")
    
    # Read original file
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except UnicodeDecodeError:
        with open(filename, 'r', encoding='latin1') as f:
            lines = f.readlines()
    
    if verbose or dry_run: print(f"\nOriginal file: {len(lines)} lines")
    
    # Process lines - SMART REMOVAL
    clean_lines = []
    removed_lines = []
    
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        original_line = line
        should_keep = True
        
        # KEEP these patterns (DON'T remove):
        keep_patterns = [
            r'from\s+.*debug',          # from ... import debug
            r'import\s+.*debug',        # import debug
            r'def\s+debug\s*\(',        # def debug(
            r'class\s+.*debug',         # class Debug
            r'#.*debug',                # comments with debug
            r'""".*debug.*"""',         # docstrings with debug
            r"'''.*debug.*'''",         # docstrings with debug
            r'debug\s*=',               # debug = something (assignment)
            r'\.debug\s*=',             # obj.debug = something
            r'".*debug.*"',             # debug inside strings
            r"'.*debug.*'",             # debug inside strings
        ]
        
        # Check if line should be kept (is import/definition/comment/string)
        for pattern in keep_patterns:
            if re.search(pattern, stripped, re.IGNORECASE):
                should_keep = True
                break
        else:
            # REMOVE these patterns (debug function calls):
            remove_patterns = [
                r'^\s*debug\s*\(',                    # debug( at start of line
                r'^\s*debug\s*\([^)]*\)\s*$',        # complete debug() call on its own line
                r'^\s*debug\s*\([^)]*\).*#.*$',      # debug() with comment
                r'^\s*debug\s*\(.*?\)\s*$',          # debug() call (multiline safe)
            ]
            
            for pattern in remove_patterns:
                if re.search(pattern, stripped, re.IGNORECASE):
                    should_keep = False
                    removed_lines.append((i, stripped))
                    if verbose or dry_run: print(f"REMOVING line {i}: {repr(stripped)}")
                    break
        
        if should_keep:
            clean_lines.append(original_line)
    
    if verbose or dry_run:
        print(f"\nAfter cleaning: {len(clean_lines)} lines")
        print(f"Removed: {len(removed_lines)} debug call lines")
        
        if len(removed_lines) == 0:
            print("\n⚠️  WARNING: No debug calls found to remove!")
        
        # Show what we're keeping vs removing
        print(f"\n=== ANALYSIS ===")
        debug_related_lines = []
        for i, line in enumerate(lines, 1):
            if 'debug' in line.lower():
                debug_related_lines.append((i, line.strip()))
        
        if debug_related_lines:
            print("All lines containing 'debug':")
            for line_num, content in debug_related_lines:
                status = "REMOVED" if any(line_num == removed[0] for removed in removed_lines) else "KEPT"
                print(f"  Line {line_num:3d} [{status:7s}]: {repr(content)}")
        
    # Prepare content
    clean_content = ''.join(clean_lines)
    original_content = ''.join(lines)
    
    # Determine output filenames
    if "_debug" in name_without_ext:
        # Input: something_debug.py -> Output: something.py (clean)
        clean_filename = name_without_ext.replace("_debug", "") + ext
        clean_path = os.path.join(file_dir, clean_filename)
        original_path = None
    else:
        # Input: something.py -> Output: something_release.py (clean)
        clean_filename = f"{name_without_ext}_release{ext}"
        clean_path = os.path.join(file_dir, clean_filename)
        original_path = name_without_ext + '_debug' + ext
    
    if verbose or dry_run:
        print(f"\n=== OUTPUT ===")
        print(f"Clean file (no debug calls): {clean_path}")
    
    # Write clean file
    try:
        if not dry_run:
            with open(clean_path, 'w', encoding='utf-8') as f:
                f.write(clean_content)
        print(f"✓ Created {'[TEST]' if dry_run else ''}: {clean_path}")

        if original_path:
            if not dry_run:
                with open(original_path, 'w', encoding='utf-8') as f:
                    f.write(original_content)
            print(f"✓ Created {'[TEST]' if dry_run else ''}: {original_path}")
            
    except Exception as e:
        print(f"ERROR writing files: {e}")
        return
    
    # if verbose or dry_run:
    # Verify the files are actually different
    if verbose or dry_run: print(f"\n=== VERIFICATION ===")
    try:
        with open(clean_path, 'r', encoding='utf-8') as f:
            written_clean = f.read()
        
        if verbose or dry_run:
            print(f"Original size: {len(original_content)} chars, {len(lines)} lines")
            print(f"Clean size: {len(written_clean)} chars, {len(clean_lines)} lines")
            print(f"Difference: {len(lines) - len(clean_lines)} lines removed")
        
        if written_clean == original_content:
            print("❌ FILES ARE IDENTICAL - No debug calls were removed")
        else:
            print("✅ FILES ARE DIFFERENT - Debug calls successfully removed!")
            
    except Exception as e:
        print(f"Error during verification: {e}")

class DebugDB(Base):  # type: ignore
    __tablename__ = 'debug'

    id = Column(Integer, primary_key=True,  autoincrement=True)  # type: ignore
    created = Column(TIMESTAMP, server_default=func.now())  # type: ignore
    message = Column(Text)  # type: ignore
    tag = Column(Text, server_default="debug")  # type: ignore

class MultiOrderedDict(OrderedDict):
    def __setitem__(self, key, value):
        if isinstance(value, list) and key in self:
            self[key].extend(value)
        else:
            super(OrderedDict, self).__setitem__(key, value)

class debugger(object):
    
    def __init__(self, defname = None, debug = None, FILENAME = None, **kwargs):
        self.FILENAME = os.getenv("DEBUG_FILENAME", FILENAME)
    
    @classmethod    
    def create_db(cls, username = None, password = None, hostname = None, dbname = None, dbtype = None):
        if USE_SQL:
            username = username or os.getenv('DB_USERNAME', 'debug_admin')
            password = password or os.getenv('DB_PASSWORD', '')
            hostname = hostname or os.getenv('DB_HOSTNAME', '127.0.0.1')
            dbname = dbname or os.getenv('DB_DBNAME', 'pydebugger')
            dbtype = dbtype or os.getenv('DB_TYPE', 'postgresql')
            
            password_encoded = quote_plus(password)
            
            engine_config = f'{dbtype}://{username}:{password_encoded}@{hostname}/{dbname}'
            engine = create_engine(engine_config, echo=True if os.getenv('DEBUG_SQL_ECHO', '0') in ['1', 'true', 'True', 'ok', 'on'] else False)  # type: ignore
            
            while 1:
                try:
                    Base.metadata.create_all(engine)
                    break
                except:
                    pass
        
            Session = sessionmaker(bind=engine)  # type: ignore
            session = Session()
            
            return session      

    @classmethod
    def debug_server_client(cls, msg, host = None, port = None):
        #client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #TCP
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #UDP
        total_sent = 0
        
        def send_message(message, client_socket, host, port):
            total_sent = 0
            while total_sent < len(message):
                END_MARKER = '<END>'                
                chunk = message[total_sent:total_sent + os.getenv('BUFFER_SIZE', 4096)]
                if not hasattr(chunk, 'decode'):
                    #client_socket.sendall(chunk.encode())
                    client_socket.sendto(chunk.encode(), (host, port))  # UDP
                else:
                    #client_socket.sendall(chunk)
                    client_socket.sendto(chunk, (host, port))  # UDP
                total_sent += os.getenv('BUFFER_SIZE', 4096)  # type: ignore
            #client_socket.sendall(END_MARKER.encode())  # TCP Send end marker to indicate end of message
            client_socket.sendto(END_MARKER.encode(), (host, port))  # UDP  # type: ignore
        
        for i in get_debug_server():
            host, port = [i.strip() for i in i.split(':')]
            try:
                if not hasattr(msg, 'decode'):
                    send_message(bytes(msg.encode('utf-8')), client_socket, host, port)
                else:
                    send_message(msg, client_socket, host, port)
            except:
                print(traceback.format_exc())
    
        client_socket.close()        
        
    @classmethod
    def get_len(cls, objects):
        if isinstance(objects, list) or isinstance(objects, tuple) or isinstance(objects, dict):
            return len(objects)
        else:
            if sys.platform == 'win32':
                if sys.version_info.major == 2:
                    return len(bytes(objects, encoding = 'utf-8'))
                else:
                    return len(str(objects))
            else:
                return len(str(objects))
        return 0

    @classmethod
    def track(cls, check = False):
        if not check and CONFIG.get_config('DEBUG', 'debug') == 1 or os.getenv('DEBUG') or os.getenv('DEBUG_SERVER'):
            traceback.format_exc()
        elif CONFIG.get_config('DEBUG', 'debug') == 1:
            return True
        return False

    @classmethod
    def insert_db(cls, message, username=None, password=None, hostname=None, dbname=None, tag = 'debug'):
        tag = os.getenv('DEBUG_TAG', os.getenv('DEBUG_APP', 'debug'))
        if USE_SQL:
            session = cls.create_db()
            try:
                session = cls.create_db()
                new_data = DebugDB(message=message, tag = tag)
                session.add(new_data)  # type: ignore
                session.commit()  # type: ignore
                session.close()  # type: ignore
                return True
            except Exception as e:
                if tprint:
                    tprint()
                else:
                    logger.exception(e, show = True)  # type: ignore 
                return False
    
    @classmethod
    def format_value(cls, key, value, lexer='python', theme='fruity', ln = True, tab_size = 2, width=get_width(), word_wrap = True):
        
        SOURCE_MUST_FORMATTED = re.split(" |,|#|:|;", os.getenv("FORMATTER_KEYS", ['TRACEBACK'], cast_type=list))  # type: ignore

        try:
            if hasattr(value, 'bytes'):
                value = value.decode()
            value = str(value)
        except Exception as e:
            if tprint:
                tprint()
            else:
                logger.exception(e, show = True)  # type: ignore 

        if key.upper() in SOURCE_MUST_FORMATTED:
            if key.lower() == 'traceback':
                lexer = 'tb'
                return Syntax(value, 'tb', theme=theme, line_numbers = ln, tab_size = tab_size, code_width = width, word_wrap = word_wrap)  # type: ignore
            else:
                return Syntax(value, lexer, theme=theme, line_numbers = ln, tab_size = tab_size, code_width = width, word_wrap = word_wrap)  # type: ignore

        elif key.lower() == 'traceback':
            lexer = 'tb'
            return Syntax(value, lexer, theme=theme, line_numbers = ln, tab_size = tab_size, code_width = width, word_wrap = word_wrap)  # type: ignore
        else:
            return make_colors(value, 'lc')  # type: ignore

    @classmethod
    def printlist(cls, defname = None, debug = None, host = None, port = None, FILENAME = '', print_function_parameters = False, source = False, lexer='python', theme='fruity', ln = True, tab_size = 2, width=get_width(), word_wrap = True, **kwargs):
        
        formatlist = ''
        args = ''
        cls = False
        values = []
        FILENAME = FILENAME or sys.argv[0]
        
        frame = inspect.currentframe()
        if frame: args, _, _, values = inspect.getargvalues(frame)  # type: ignore

        debug = debug or DEBUG
        if RICH_AVAILABLE:
            color_random = ['#AAFF00', '#FFFF00', '#FFFFFF', '#00FFFF', '#AA55FF']
        elif MAKE_COLORS_AVAILABLE:
            color_random = ['lightgreen', 'lightyellow', 'lightwhite', 'lightcyan', 'lightmagenta']
        else:
            color_random = ['','','','','']

        if RICH_AVAILABLE:
            arrow = f"[bold #AAFF00]->[/]"
        elif MAKE_COLORS_AVAILABLE:
            arrow = make_colors(' -> ', 'lg')  # type: ignore
        else:
            arrow = ' -> '
            
        if print_function_parameters:
            for i in args:  # type: ignore
                if i == 'cls':
                    pass
                else:
                    if RICH_AVAILABLE:
                        formatlist = f"[white on #0000FF]{i}:[/] [bold {color_random[int(args.index(i))]}]{values[i]}[/]{arrow}"  # type: ignore
                    elif MAKE_COLORS_AVAILABLE:
                        formatlist = f"{make_colors((str(i) + ":"), 'lw', 'bl')} {make_colors(str(values[i]), color_random_1[int(args.index(i))])}{arrow}"  # type: ignore
                    else:
                        formatlist = str(i) + ": " + str(values[i]) + arrow  # type: ignore
                        
                    if not defname: defname = str(inspect.stack()[1][3])

                    linenumbers = str(inspect.stack()[1][2])

                    if RICH_AVAILABLE:
                        formatlist = f"[bold #FFFFFF]{datetime.datetime.strftime(datetime.datetime.now(), '%Y:%m:%d~%H:%M:%S:%f')}[/] [#00FFFF on #FF0000]{defname}{arrow}[/]{formatlist} \[[bold #00FF00]{FILENAME}[/]] \[[bold #FFFF00]{linenumbers}[/]] "
                    elif MAKE_COLORS_AVAILABLE:
                        formatlist = f"{make_colors(datetime.datetime.strftime(datetime.datetime.now(), '%Y:%m:%d~%H:%M:%S:%f'), 'white')} {make_colors(defname + arrow, 'lw', 'r')}{formatlist} \[{FILENAME}] \[{make_colors(str(linenumbers), 'lw', 'lc')}] "  # type: ignore
                    else:
                        formatlist = f"{datetime.datetime.strftime(datetime.datetime.now(), '%Y:%m:%d~%H:%M:%S:%f')} {defname}{arrow}{formatlist} \[{FILENAME}] [{linenumbers}] "
                        
                    if debug:
                        print(formatlist)
                    if get_debug_server(): cls.debug_server_client(formatlist)  # type: ignore            
        
        if kwargs:
            for i in kwargs:
                if str(i) in ["cls", "clear"]: cls = True                
                try:
                    if kwargs.get(i) == '' or kwargs.get(i) == None:
                        if RICH_AVAILABLE:
                            formatlist += f"[#FFFFFF on #0000FF]{i}[/]{arrow}"
                        elif MAKE_COLORS_AVAILABLE
                            formatlist += make_colors(str(i), 'lw', 'bl') + arrow  # type: ignore
                        else:
                            formatlist += str(i) + arrow
                    else:
                        if RICH_AVAILABLE:
                            formatlist += f"[#000000 on #FFFF00]{i}:[/] {cls.format_value(i, kwargs.get(i))}{arrow}[#000000 on #FFFF00]TYPE:[/] [#000000 on #00FFFF]{str(type(kwargs.get(i)))}[/]{arrow}[white on #AA00FF]LEN:[/][bold #AAAAFF]{str(cls.get_len(kwargs.get(i)))}[/]{arrow}"  # type: ignore
                        elif MAKE_COLORS_AVAILABLE:
                            formatlist += make_colors((str(i) + ": "), 'b', 'ly') + cls.format_value(i, kwargs.get(i)) + arrow + make_colors("TYPE:", 'b', 'ly') + make_colors(str(type(kwargs.get(i))), 'b', 'lc') + arrow + make_colors("LEN:", 'lw', 'lm') + make_colors(str(cls.get_len(kwargs.get(i))), 'lightmagenta') + arrow  # type: ignore
                        else:
                            formatlist += str(i) + ": " + str(kwargs.get(i)) + arrow + "TYPE: " + str(type(kwargs.get(i))) + arrow + "LEN: " + str(cls.get_len(kwargs.get(i))) + arrow  # type: ignore
                except:
                    if tprint:
                        tprint()
                    else:
                        logger.exception("ERROR in printlist", show = True)  # type: ignore 

                    try:
                        cls.debug_server_client(traceback.format_exc())  # type: ignore
                    except:
                        print("Send traceback ERROR [290]")

            if RICH_AVAILABLE:
                formatlist += f"[{color_random[int(random.random()*4)]} on #000000]start ... [/]"  # type: ignore
            elif MAKE_COLORS_AVAILABLE:
                formatlist += " " + make_colors("start ... ", random.choice(color_random)) + arrow  # type: ignore
            else:
                formatlist += " start... " + arrow

        # formatlist = formatlist[:-4]
        defname_parent = ''
        the_class = ''
        
        defname = defname or defname = str(inspect.stack()[2][3])  # type: ignore
        if defname == "<module>": defname = sys.argv[0]
        try:
            the_class = re.split(f"'|>|<|\\.", str(inspect.stack()[1][0].f_locals.get('cls').__class__))[-3]
        except:
            pass

        if len(inspect.stack()) > 2:
            for h in inspect.stack()[3:]:
                if isinstance(h[2], int):
                    if not h[3] == '<module>':
                        if RICH_AVAILABLE:
                            defname_parent += f"[bold #00FFFF]{h[3]}[/][#00FFFF on #FF0000]{h[2]}[/]{arrow}"
                        elif MAKE_COLORS_AVAILABLE:
                            defname_parent += "%s" % (make_colors(h[3], 'lc')) + "[%s]" % (make_colors(str(h[2]), 'lw', 'r')) + arrow  # type: ignore
                        else:
                            defname_parent += "%s" % (h[3]) + "[%s]" % (str(h[2])) + arrow
        
        if the_class and not the_class == "NoneType":
            if RICH_AVAILABLE:
                defname_parent += f"[#FFFFFF on #0000FF]({the_class})[/]{arrow}"
            elif MAKE_COLORS_AVAILABLE:
                defname_parent += "(%s)" % (make_colors(the_class, 'lw', 'blue')) + arrow  # type: ignore
            else:
                defname_parent += "(%s)" % (the_class) + arrow
            
            if RICH_AVAILABLE:
                FILENAME = f"[bold #00FF00]{FILENAME}[/]"
            elif MAKE_COLORS_AVAILABLE:
                FILENAME = make_colors(FILENAME, 'lightgreen')  # type: ignore
            else:
                FILENAME = str(FILENAME)

        linenumbers = str(inspect.stack()[1][2])

        if RICH_AVAILABLE:
            formatlist = f"[bold #FFFFFF]{datetime.datetime.strftime(datetime.datetime.now(), '%Y:%m:%d~%H:%M:%S:%f')}[/] [#00FFFF on #FF0000]{defname}{arrow}[/]{formatlist} \[[bold #00FF00]{FILENAME}[/]] [bold #00FFFF]\[[/][#FFFFFF on #AA007F]{str(linenumbers)[2:-2]}[/][bold #00FFFF]][/] [bold #FF5500]PID:[/][#FFFFFF on #000000]{PID}[/]"  # type: ignore
        elif MAKE_COLORS_AVAILABLE:
            formatlist = make_colors(datetime.datetime.strftime(datetime.datetime.now(), '%Y:%m:%d~%H:%M:%S:%f'), 'lw') + " " + make_colors(defname + arrow, 'lw', 'r') + formatlist + " " + "[" + str(FILENAME) + "]" + " "  + make_colors("[", "cyan") + make_colors(str(linenumbers)[2:-2], 'lw', 'lc') + make_colors("]", "lc") + " " + make_colors("PID:", 'red', 'lg') + make_colors(str(PID), 'lw')  # type: ignore
        else:
            formatlist = f"{datetime.datetime.strftime(datetime.datetime.now(), '%Y:%m:%d~%H:%M:%S:%f')} {defname}{arrow}{formatlist} [{FILENAME}] [{linenumbers}] " + " " + "PID:" + str(PID)
            
        
        if str(os.getenv("DEBUG", '0')).lower() in ['1', 'true', 'ok', 'yes', 'on'] or debug:
            print(formatlist)
            if source:
                # call get_source
                frame_globals = inspect.stack()[2][0].f_globals
                if defname in frame_globals and inspect.isfunction(frame_globals[defname]):
                    get_source(frame_globals[defname], lexer, theme, ln, tab_size, width, word_wrap)
                            
        if get_debug_server():
            if cls: formatlist = 'cls'
            cls.debug_server_client(formatlist, host, port)  # type: ignore
        
        cls = False
        
        return formatlist

    @classmethod
    def db_log(cls, tag = None):
        session = cls.create_db()
        last_id_first = None
        if tag == None:
            tag = ''
        tag = tag.strip()
        try:
            if tag:
                last_id_first = session.query(DebugDB.id).filter(DebugDB.tag == tag).order_by(DebugDB.id.desc()).first()[0]  # type: ignore
            else:
                last_id_first = session.query(DebugDB.id).order_by(DebugDB.id.desc()).first()[0]  # type: ignore
        except:
            pass
        try:
            while 1:
                if last_id_first:  # type: ignore
                    if tag:
                        data = session.query(DebugDB).filter(DebugDB.tag == tag).order_by(DebugDB.id.desc()).first()  # type: ignore
                    else:
                        data = session.query(DebugDB).order_by(DebugDB.id.desc()).first()  # type: ignore
                    last_id = data.id  # type: ignore
                    if not last_id == last_id_first:  # type: ignore
                        #data = ActivityLog.objects.filter(id__range=(last_id_first, last_id)).order_by('id')[:obj.count()]
                        # Query the data using SQLAlchemy
                        if tag:
                            query = session.query(DebugDB).filter(DebugDB.id > last_id_first, DebugDB.id <= last_id, DebugDB.tag == tag).order_by(DebugDB.id)  # type: ignore
                        else:
                            query = session.query(DebugDB).filter(DebugDB.id > last_id_first, DebugDB.id <= last_id).order_by(DebugDB.id)  # type: ignore
                        
                        # Retrieve the count using SQLAlchemy's count method
                        count = query.count()
                        
                        # Specify the limit for the number of results
                        limit = count  # Retrieve all rows within the specified range
                        
                        # Apply the limit to the query
                        query = query.limit(limit)
                        
                        # Execute the query to get the results
                        data = query.all()
                        
                        data = query.all()
                        last_id_first = last_id
                        for i in data:
                            message = i.message
                            if hasattr(message, 'decode'): message = message.decode('utf-8')
                            if RICH_AVAILABLE:
                                console.print(f"[#5500FF on #FFFFFF]{message} [bold #FF00AA]{i.tag}[/]")  # type: ignore
                            elif MAKE_COLORS_AVAILABLE:
                                print(message + " " + make_colors(i.tag, 'm', 'lw'))  # type: ignore
                            else:
                                print(message + " " + str(i.tag))
                time.sleep(0.5)
                    
        except KeyboardInterrupt:
            sys.exit(0)
            
            
def debug(defname = None, debug = None, host = None, port = None, line_number = None, tag = 'debug', print_function_parameters = False, source = False, **kwargs):
    if not debug and str(os.getenv('DEBUG', '0')).lower() in ['0', 'false', 'no', 'off'] and not get_debug_server():
        return None
    
    msg = ''
    tag = os.getenv('DEBUG_TAG', os.getenv('DEBUG_APP', 'debug'))

    # if RICH_AVAILABLE:
    #     line_number = f" \[[#00FFFF on #FF0000]{str(inspect.stack()[1][2])}[/]] "
    # elif MAKE_COLORS_AVAILABLE:
    #     line_number =  " [" + make_colors(str(inspect.stack()[1][2]), 'red', 'lightwhite') + "] "  # type: ignore
    # else:
    #     line_number =  " [" + str(inspect.stack()[1][2]) + "] "

    c = debugger(defname, debug)
    msg = c.printlist(defname, debug, host, port, linenumbers = line_number, print_function_parameters= print_function_parameters, source = source, **kwargs)
    
    if str(os.getenv('DB_ACTIVE', '0')).lower() in ['1', 'true', 'ok', 'yes', 'on']:
        if not msg:
            c = debugger(defname, debug)
            msg = c.printlist(defname, debug, linenumbers = line_number, print_function_parameters= print_function_parameters, **kwargs)        
        c.insert_db(msg, tag)
    
    return msg


def version():
    try:
        version_file = Path(__file__).parent / "__version__.py"
        if version_file.is_file():
            with open(version_file, "r") as f:
                for line in f:
                    if line.strip().startswith("version"):
                        parts = line.split("=")
                        if len(parts) == 2:
                            return parts[1].strip().strip('"').strip("'")
    except Exception as e:
        debug(error=str(e))

    return "UNKNOWN VERSION"
    
def handle_windows():
    global HANDLE
    if sys.platform == 'win32':
        HANDLE = ctypes.windll.user32.GetForegroundWindow()
        
def usage():
    parser = argparse.ArgumentParser(
        prog='debug', 
        description= '🐍 Run debugger as server, receive debug message with default port is 50001', 
        formatter_class= CustomRichHelpFormatter
    )
    
    # === Global Command ===
    parser.add_argument('-a', '--on-top', action = 'store_true', help = 'Always On Top')
    parser.add_argument('-c', '--cleanup', action = 'store', help = 'CleanUp File')
    parser.add_argument('-v', '--version', action = 'store_true', help = 'Get version number')
    
    # === Subcommand: serve ===        
    subparsers = parser.add_subparsers(dest = 'COMMAND', help = 'Available subCommands')
    
    serve_parser = subparsers.add_parser('serve', help='Run debug message UDP server', formatter_class= CustomRichHelpFormatter)
    serve_parser.add_argument('--host', default='0.0.0.0', help='Host to bind, default: 0.0.0.0')
    serve_parser.add_argument('--port', type=int, default=50001, help='Port to bind, default: 50001')
    serve_parser.add_argument('--on-top', action='store_true', help='Always On Top')

    # === Subcommand: log ===
    log_parser = subparsers.add_parser('log', help='Database log inspection', formatter_class= CustomRichHelpFormatter)
    log_parser.add_argument('-l', '--db-log', action = 'store_true', help = 'Get Database log')
    log_parser.add_argument('-L', '--db-log-tag', action = 'store', help = 'Filter Database log by tag')
    
    # === Subcommand: cleanup ===
    cleanup_parser = subparsers.add_parser('cleanup', help='Cleanup file', formatter_class= CustomRichHelpFormatter)
    cleanup_parser.add_argument('path', help='Path file to clean')

    # === Subcommand: version ===
    version_parser = subparsers.add_parser('version', help='Print version info')
    
    # === Subcommand: cleaner ===
    cleaner_parser = subparsers.add_parser('cleaner', help='Cleaner file (comment out/in)', formatter_class= CustomRichHelpFormatter)
    cleaner_parser.add_argument(
        'path',
        help='📁 Path to directory or Python file for processing'
    )
    
    cleaner_parser.add_argument(
        '--dry-run',
        action='store_true',
        help='👁️ Preview changes without modifying files'
    )
    
    action_group = cleaner_parser.add_mutually_exclusive_group()
    action_group.add_argument(
        '-co', '--comment-out',
        action='store_true',
        help='💬 Comment out debug lines (add # in front)'
    )
    
    action_group.add_argument(
        '-ci', '--comment-in',
        action='store_true',
        help='🔓 Uncomment debug lines (remove # in front)'
    )
    
    return parser

def main():        
    handle_windows()
    
    try:
        from .cleaner import DebugCleaner  # type: ignore
    except:
        from cleaner import DebugCleaner  # type: ignore
    
    if len(sys.argv) == 3:
        if len(sys.argv[1].split(".")) == 4 and not str(sys.argv[1]).isdigit():
            if str(sys.argv[2]).isdigit():
                serve(sys.argv[1], int(sys.argv[2]))
            else:
                serve(sys.argv[1], 50001)
        elif len(sys.argv[2].split(".")) == 4 and not str(sys.argv[2]).isdigit():
            if str(sys.argv[1]).isdigit():
                serve(sys.argv[2], int(sys.argv[1]))
            else:
                serve(sys.argv[2], 50001)
    elif len(sys.argv) == 2:
        # print(f"str(sys.argv[1]).isdigit(): {str(sys.argv[1]).isdigit()}")
        if str(sys.argv[1]).isdigit():
            serve(port = int(sys.argv[1] or 50001))
        elif len(sys.argv[1].split(".")) == 4 and not str(sys.argv[1]).isdigit():
            serve(sys.argv[1], 50001)
    # serve(port = int(*sys.argv[1:]))
    
    parser = usage()
    
    if len(sys.argv) <= 1:
        print("\n")
        parser.print_help()
        print("\n💡 Use 'debug.py <command> --help' for more details.")
        try:
            serve()
        except KeyboardInterrupt:
            return
        except Exception as e:
            if tprint:
                tprint()
            else:
                logger.exception(e, show = True)  # type: ignore
            sys.exit(0)

    args = parser.parse_args()

    if args.COMMAND == 'cleaner':
        manager = DebugCleaner()
        python_files = manager.find_python_files(args.path)

        if not python_files:
            if RICH_AVAILABLE:
                console.print("\u26a0\ufe0f [bold yellow]No Python files found.[/]")  # type: ignore
            else:
                print("\u26a0\ufe0f No Python files found.")
            return

        action = 'clean'
        if getattr(args, 'comment_out', False):
            action = 'comment_out'
        elif getattr(args, 'comment_in', False):
            action = 'comment_in'

        results = []
        for file_path in python_files:
            result = manager.process_file(file_path, action, args.dry_run)
            results.append(result)

        manager.display_results(results, args.dry_run, action)

    elif args.COMMAND == 'serve':
        serve(args.host, args.port, args.on_top)

    elif args.COMMAND == 'log':
        if args.db_log:
            debugger.db_log()
        elif args.db_log_tag:
            debugger.db_log(args.db_log_tag)

    elif args.COMMAND == 'cleanup':
        print("CLEANUP ........")
        cleanup(args.path)

    elif args.COMMAND == 'version':
        print("VERSION:", version())

if __name__ == '__main__':
    if sys.platform == 'win32':
        kernel32 = ctypes.WinDLL('kernel32')
        handle2 = ctypes.windll.user32.GetForegroundWindow()
        HANDLE = handle2
        if RICH_AVAILABLE:
            console.print(f"HANDLE: [#FFFF00]{HANDLE}[/]| PID: [#00FFFF]{PID}[/]")  # type: ignore
        elif MAKE_COLORS_AVAILABLE:
            print("HANDLE:", make_colors(str(HANDLE), 'yellow'), "| PID:", make_colors(str(PID), 'cyan'))  # type: ignore
        else:
            print("HANDLE:", HANDLE, "| PID:", PID)
    else:
        print(f"PID: {PID}")
    
    main()
