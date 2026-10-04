#!/usr/bin/env python3

# File: debug.py
# Author: Hadi Cahyadi <cumulus13@gmail.com>
# Date: 2026-01-04
# Description: Python debugger with remote debugging capabilities
# License: MIT
#-*- encoding: utf-8 -*-
#encoding: utf-8

from __future__ import print_function

import argparse
import os
import sys
if sys.platform == 'win32':
    try:
        import win32api  # type: ignore
    except:
        pass
import traceback
from pathlib import Path
from datetime import datetime
import time
import shutil
import inspect
import random
import socket
import re
import ctypes
from urllib.parse import quote_plus
from collections import OrderedDict
import signal
from typing import Any, Callable, Dict, List, Optional, Union, Tuple

# Global variables
RICH_AVAILABLE = False

ENVDOT_AVAILABLE = False
USE_SQL = False
USE_DEFAULT_CONFIG = False
PID = os.getpid()
HANDLE = None
END_MARKER = b"<END>"
CONFIGFILE = str(Path(__file__).parent / 'debug.ini')
DEBUG = str(os.getenv('DEBUG', '0')).lower() in ('1', 'true', 'ok', 'yes', 'on') 
# print(f"DEBUG [debug.py]: {DEBUG}")
# sys.exit(1)
console = None  # type: ignore

# Try to load environment variables
# try:
#     from envdot import load_env  # type: ignore
#     ENVDOT_AVAILABLE = True
#     CONFIG = load_env()
# except:
CONFIG = None

LOG_LEVEL = os.getenv('LOG_LEVEL', "CRITICAL")

#print(f"os.getenv('DEBUG'): {os.getenv('DEBUG')}")
# Check for debug mode in command line arguments
if len(sys.argv) > 1 and any('--debug' == arg for arg in sys.argv):
    print("🐞 Debug mode enabled")
    os.environ['LOGGING'] = "1"
    os.environ.pop('NO_LOGGING', None)
    os.environ['TRACEBACK'] = "1"
    LOG_LEVEL = "DEBUG"
else:
    os.environ['NO_LOGGING'] = "1"

#print(f"os.getenv('DEBUG'): {os.getenv('DEBUG')}")
# Parse exceptions list from environment
exceptions_str = os.getenv('LOG_EXCEPTIONS', 'socket,gntplib,sqlalchemy')
exceptions = [e.strip() for e in exceptions_str.split(',')] if exceptions_str else []

# Setup logging
# import logging

# try:
#     from .custom_logging import get_logger  # type: ignore
# except ImportError:
#     try:
#         from custom_logging import get_logger  # type: ignore
#     except:
#         # Fallback to basic logging
#         def get_logger(name, level=logging.CRITICAL):
#             logger = logging.getLogger(name)
#             logger.setLevel(level)
#             return logger

# for exc in exceptions:
#     logging.getLogger(exc).setLevel(logging.CRITICAL)

# logger = get_logger('pydebugger', level=getattr(logging, LOG_LEVEL.upper(), logging.CRITICAL))

def tprint(*args, **kwargs):
    traceback.print_exc()

# from rich_argparse import RichHelpFormatter, RawDescriptionRichHelpFormatter, _lazy_rich as rr
from typing import ClassVar

# Load config if envdot is not available
if not ENVDOT_AVAILABLE:
    try:
        from .config import CONFIG
        USE_DEFAULT_CONFIG = True
    except Exception as e:
        try:
            from config import CONFIG
            USE_DEFAULT_CONFIG = True
        except:
            # Create a simple config class as fallback
            class SimpleConfig:
                def get_config(self, section, key, default=None):
                    return os.getenv(f"{section}_{key}".upper(), default)
            CONFIG = SimpleConfig()
#print(f"os.getenv('DEBUG'): {os.getenv('DEBUG')}")
# Try to import rich
try:
    from rich import traceback as rich_traceback, console  # type: ignore
    console = console.Console(width=shutil.get_terminal_size()[0])  # type: ignore
    rich_traceback.install(theme='fruity', max_frames=30, width=shutil.get_terminal_size()[0])
    from rich.syntax import Syntax
    from rich import box
    from rich.table import Table
    RICH_AVAILABLE = True
except:
    pass

if not RICH_AVAILABLE:
    class console:
        def print(self, msg):
            print(msg)
#print(f"os.getenv('DEBUG'): {os.getenv('DEBUG')}")
# Try to import CustomRichHelpFormatter
# class CustomRichHelpFormatter(RawDescriptionRichHelpFormatter):
#     """A custom RichHelpFormatter with modified styles."""

#     def __init__(self, prog, epilog=None, width=None, max_help_position=24, indent_increment=2):
#         super().__init__(prog)
#         if epilog is not None:
#             self.epilog = epilog
#         if width is not None:
#             self.width = width
#         self._max_help_position = max_help_position
#         self._indent_increment = indent_increment

#     styles: ClassVar[dict[str, rr.StyleType]] = {
#         "argparse.args": "bold #FFFF00",  # Changed from cyan
#         "argparse.groups": "#AA55FF",   # Changed from dark_orange
#         "argparse.help": "bold #00FFFF",    # Changed from default
#         "argparse.metavar": "bold #FF55FF", # Changed from dark_cyan
#         "argparse.syntax": "underline", # Changed from bold
#         "argparse.text": "white",   # Changed from default
#         "argparse.prog": "bold #00AAFF italic",     # Changed from grey50
#         "argparse.default": "bold", # Changed from italic
#     }

#     def format_help(self):
#         help_text = super().format_help()
#         # Add a newline in front of the usage if not there
#         if not help_text.lstrip().startswith("Usage:"):
#             # Cari posisi Usage
#             idx = help_text.find("Usage:")
#             if idx > 0:
#                 help_text = help_text[:idx] + "\n" + help_text[idx:]
#             elif idx == 0:
#                 help_text = "\n" + help_text
#         elif not help_text.startswith("\n"):
#             help_text = "\n" + help_text
#         return help_text

#     def _rich_fill_text(self, text: rr.Text, width: int, indent: rr.Text) -> rr.Text:
#         # Split per baris, pertahankan baris kosong
#         lines = text.plain.splitlines()
#         return rr.Text("\n").join(
#             indent + rr.Text(line, style=text.style) for line in lines
#         ) + "\n\n"

#     def add_text(self, text):
#         if text is argparse.SUPPRESS or text is None:
#             return
#         if isinstance(text, str):
#             lines = text.strip().splitlines()
#             indent = " " * getattr(self, "_current_indent", 2)
#             if len(indent) < 2:
#                 indent = " " * 2
#             # Detection: If all rows are commands (python, $, or spaces), display all as syntax
#             is_all_code = all(
#                 l.strip().startswith(("python", "$")) or l.startswith("  ") for l in lines if l.strip()
#             )
#             # print(f"Detected all code: {is_all_code}, lines: {lines}")
#             if len(lines) > 0 and (is_all_code or len(lines) > 1):
#                 # If there is a title (the first line is not an order), display the title
#                 if len(lines) > 1 and not (lines[0].strip().startswith(("python", "$")) or lines[0].startswith("  ")):
#                     # print(f"Adding title: {lines[0]}")
#                     self.add_renderable(rr.Text(lines[0], style="#007F74 bold"))
#                     code_lines = lines[1:]
#                 else:
#                     # print("No title detected, using all lines as code.")
#                     code_lines = lines
#                 # Add indentation to all line code
#                 code = "\n".join(f"{indent}{l.strip()}" for l in code_lines)
#                 if code.strip():
#                     self.add_renderable(
#                         Syntax(code, "bash", theme="fruity", line_numbers=False)
#                     )
#                 return
#             else:
#                 text = rr.Text(text, style=self.styles["argparse.text"])
#         super().add_text(text)  # type: ignore

# Try to import SQLAlchemy
try:
    from sqlalchemy import create_engine, Column, Integer, Text, text, func, TIMESTAMP
    from sqlalchemy.orm import sessionmaker, declarative_base
    USE_SQL = True
    Base = declarative_base()
except:
    pass

#print(f"os.getenv('DEBUG') X: {os.getenv('DEBUG')}")

def get_debug_server(ENV='DEBUG_SERVER'):
    """Parse DEBUG_SERVER environment variable"""
    DEBUG_SERVER = []
    debug_server_str = os.getenv(ENV, '')
    
    # #logger.critical(f"debug_server_str: {debug_server_str}")

    if debug_server_str and not str(debug_server_str).lower() in ("1", "true", "ok", "yes", "on"):
        # Parse comma-separated list
        data = [i.strip() for i in re.split(r",|;|\||\.", debug_server_str)]
        items = [str(item).strip() for item in data]
        # #logger.primary(f"items: {items}")
        if items:
            for item in items:
                if item.isdigit():
                    DEBUG_SERVER.append(f"127.0.0.1:{item}")
                elif len(item.split(".")) == 4:
                    DEBUG_SERVER.append(f"{item}:50001")
                elif ":" in item:
                    DEBUG_SERVER.append(item)
                else:
                    DEBUG_SERVER.append('127.0.0.1:50001')
            DEBUG_SERVER = list(set(DEBUG_SERVER))
    elif debug_server_str and str(debug_server_str).lower() in ("1", "true", "ok", "yes", "on"):
        DEBUG_SERVER = ['127.0.0.1:50001']
    # else:
        # DEBUG_SERVER = ['127.0.0.1:50001']

    return DEBUG_SERVER

force = False

def get_width():
    """Get terminal width"""
    return shutil.get_terminal_size()[0]

def get_source(source, lexer='python', theme='fruity', ln=True, tab_size=2, width=None, word_wrap=True, no_print=False, **kwargs):
    """Display source code with syntax highlighting"""
    if width is None:
        width = get_width()

    if RICH_AVAILABLE:
        if not no_print:
            console.print(  # type: ignore
                Syntax(  # type: ignore
                    inspect.getsource(source),
                    lexer,
                    theme=theme,
                    line_numbers=ln or kwargs.get('line_numbers', False),
                    tab_size=tab_size,
                    code_width=width,
                    word_wrap=word_wrap
                )
            )
        else:
            return Syntax(  # type: ignore
                    inspect.getsource(source),
                    lexer,
                    theme=theme,
                    line_numbers=ln or kwargs.get('line_numbers', False),
                    tab_size=tab_size,
                    code_width=width,
                    word_wrap=word_wrap
                )
    else:
        if not no_print:
            print("display source does not support, please consider installing 'rich' before!")
        else:
            return "display source does not support, please consider installing 'rich' before!"

def serve(host='0.0.0.0', port=50001, on_top=False):
    """Start UDP debug server"""
    END_MARKER = b'<END>'
    # #logger.debug(f"END_MARKER: {END_MARKER}, TYPE: {type(END_MARKER)}")
    on_top = str(os.getenv('DISPLAY_ON_TOP', str(on_top))).lower() in ('true', '1', 'yes')
    print(f"on_top: {on_top}")
    # #logger.debug(f"ON_TOP: {on_top}, TYPE: {type(on_top)}")

    def receive_message(server_socket):
        """Receive message from UDP socket"""
        full_message = b''
        buffer_size = int(os.getenv('BUFFER_SIZE', '4096'))

        while True:
            try:
                chunk, _ = server_socket.recvfrom(buffer_size)
            except socket.timeout:
                return b''

            if END_MARKER in chunk:
                full_message += chunk.replace(END_MARKER, b'')
                break
            full_message += chunk
        return full_message

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((host, port))
    server_socket.settimeout(1.0)

    try:
        console.print(f"[bold #AAAAFF]Debug server started[/] [bold #00FFFF]{host}[/]:[bold #FFFF00]{port}[/]. [bold #FF557F]Waiting for messages...[/]")  # type: ignore
    except Exception:
        # console.log(e)  # type: ignore
        print(f"Debug server started {host}:{port}. Waiting for messages...")

    try:
        while True:
            msg = receive_message(server_socket)

            if msg:
                if CONFIG and hasattr(CONFIG, 'get_config'):
                    if str(CONFIG.get_config('display', 'raise', on_top)).lower() in ('1', 'true', 'yes') or on_top:
                        showme_no_delay()

                if hasattr(msg, 'decode'):
                    msg = msg.decode(errors='replace')

                if RICH_AVAILABLE:
                    console.print(msg)  # type: ignore
                else:
                    print(msg)

                # print("=" * get_width())
                sep = os.getenv("DEBUG_SEP", None) or os.getenv("PYDEBUGGER_SEP", '─')
                print(sep * get_width())


    except KeyboardInterrupt:
        try:
            console.print("[bold #FF5555]Server shutdown ...[/]")  # type: ignore
        except:
            print("Server shutdown ...")
    finally:
        server_socket.close()
        try:
            console.print("[bold #FFFF00]Socket closed, server terminated gracefully.[/]")  # type: ignore
        except Exception as e:
            print("Socket closed, server terminated gracefully.")
        os.kill(PID, signal.SIGTERM)

def set_detach(width=700, height=400, x=10, y=50, monitor_index=0, center=False, buffer_column=9000, buffer_row=77, on_top=True):
    """Set console window position and size (Windows only)"""
    if sys.platform != 'win32':
        return False

    try:
        from dcmd import dcmd
        setting = dcmd()
        setting.setBuffer(buffer_row, buffer_column)

        # Take all monitors (left, top, right, bottom)
        monitors = win32api.EnumDisplayMonitors()
        if monitor_index >= len(monitors):
            monitor_index = 0

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
    except:
        return False

def showme_no_delay():
    """Show console window without delay (Windows only)"""
    if not sys.platform == 'win32':
        return False

    global HANDLE
    if not HANDLE:
        return False

    # Save the currently active window
    current_foreground = ctypes.windll.user32.GetForegroundWindow()

    # Raise window target
    ctypes.windll.user32.SetForegroundWindow(HANDLE)

    # Immediately return focus
    if current_foreground and current_foreground != HANDLE:
        ctypes.windll.user32.SetForegroundWindow(current_foreground)

    return True

def cleanup(filename, dry_run=False, verbose=False):
    """Remove debug() calls from Python file"""

    if verbose or dry_run:
        print("=== CLEANUP FUNCTION - SMART DEBUG REMOVAL ===")
        print(f"Processing: {filename}")

    # Check if file exists
    if not os.path.exists(filename):
        # #logger.error(f"File {filename} not found!")
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
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S%f')
    backup_name = f"{name_without_ext}_{timestamp}{ext}"
    backup_path = os.path.join(file_dir, backup_name)
    shutil.copyfile(filename, backup_path)
    if verbose or dry_run:
        print(f"Backup: {backup_name}")

    # Read original file
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except UnicodeDecodeError:
        with open(filename, 'r', encoding='latin1') as f:
            lines = f.readlines()

    if verbose or dry_run:
        print(f"\nOriginal file: {len(lines)} lines")

    # Process lines - SMART REMOVAL
    clean_lines = []
    removed_lines = []

    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        original_line = line
        should_keep = True

        # KEEP these patterns (DON'T remove)
        keep_patterns = [
            r'from\s+.*debug',
            r'import\s+.*debug',
            r'def\s+debug\s*\(',
            r'class\s+.*debug',
            r'#.*debug',
            r'""".*debug.*"""',
            r"'''.*debug.*'''",
            r'debug\s*=',
            r'\.debug\s*=',
            r'".*debug.*"',
            r"'.*debug.*'",
        ]

        # Check if line should be kept
        for pattern in keep_patterns:
            if re.search(pattern, stripped, re.IGNORECASE):
                should_keep = True
                break
        else:
            # REMOVE these patterns (debug function calls)
            remove_patterns = [
                r'^\s*debug\s*\(',
                r'^\s*debug\s*\([^)]*\)\s*$',
                r'^\s*debug\s*\([^)]*\).*#.*$',
                r'^\s*debug\s*\(.*?\)\s*$',
            ]

            for pattern in remove_patterns:
                if re.search(pattern, stripped, re.IGNORECASE):
                    should_keep = False
                    removed_lines.append((i, stripped))
                    if verbose or dry_run:
                        print(f"REMOVING line {i}: {repr(stripped)}")
                    break

        if should_keep:
            clean_lines.append(original_line)

    if verbose or dry_run:
        print(f"\nAfter cleaning: {len(clean_lines)} lines")
        print(f"Removed: {len(removed_lines)} debug call lines")

        if len(removed_lines) == 0:
            print("\n⚠️  WARNING: No debug calls found to remove!")

    # Prepare content
    clean_content = ''.join(clean_lines)
    original_content = ''.join(lines)

    # Determine output filenames
    if "_debug" in name_without_ext:
        clean_filename = name_without_ext.replace("_debug", "") + ext
        clean_path = os.path.join(file_dir, clean_filename)
        original_path = None
    else:
        clean_filename = f"{name_without_ext}_release{ext}"
        clean_path = os.path.join(file_dir, clean_filename)
        original_path = os.path.join(file_dir, name_without_ext + '_debug' + ext)

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

    # Verify the files are different
    if verbose or dry_run:
        print(f"\n=== VERIFICATION ===")
        try:
            with open(clean_path, 'r', encoding='utf-8') as f:
                written_clean = f.read()

            print(f"Original size: {len(original_content)} chars, {len(lines)} lines")
            print(f"Clean size: {len(written_clean)} chars, {len(clean_lines)} lines")
            print(f"Difference: {len(lines) - len(clean_lines)} lines removed")

            if written_clean == original_content:
                print("❌ FILES ARE IDENTICAL - No debug calls were removed")
            else:
                print("✅ FILES ARE DIFFERENT - Debug calls successfully removed!")

        except Exception as e:
            print(f"Error during verification: {e}")

if USE_SQL:
    class DebugDB(Base):  # type: ignore
        __tablename__ = 'debug'

        id = Column(Integer, primary_key=True, autoincrement=True)  # type: ignore
        created = Column(TIMESTAMP, server_default=func.now())  # type: ignore
        message = Column(Text)  # type: ignore
        tag = Column(Text, server_default="debug")  # type: ignore

#print(f"os.getenv('DEBUG') X: {os.getenv('DEBUG')}")

class MultiOrderedDict(OrderedDict):
    def __setitem__(self, key, value):
        if isinstance(value, list) and key in self:
            self[key].extend(value)
        else:
            super().__setitem__(key, value)

#print(f"os.getenv('DEBUG') X: {os.getenv('DEBUG')}")
class debugger(object):

    def __init__(self, defname = None, debug = None, FILENAME=None):
        self.FILENAME = os.getenv("DEBUG_FILENAME", FILENAME)
        self.debug = debug or DEBUG
        self.defname = defname

    @classmethod
    def create_db(cls, username=None, password=None, hostname=None, dbname=None, dbtype=None):
        """Create database connection and tables"""
        if not USE_SQL:
            return None

        username = username or os.getenv('DB_USERNAME', 'debug_admin')
        password = password or os.getenv('DB_PASSWORD', '')
        hostname = hostname or os.getenv('DB_HOSTNAME', '127.0.0.1')
        dbname = dbname or os.getenv('DB_DBNAME', 'pydebugger')
        dbtype = dbtype or os.getenv('DB_TYPE', 'postgresql')

        password_encoded = quote_plus(password)

        engine_config = f'{dbtype}://{username}:{password_encoded}@{hostname}/{dbname}'
        engine = create_engine(  # type: ignore
            engine_config,
            echo=str(os.getenv('DEBUG_SQL_ECHO', '0')).lower() in ['1', 'true', 'yes']
        )

        while True:
            try:
                Base.metadata.create_all(engine)
                break
            except:
                time.sleep(1)

        Session = sessionmaker(bind=engine)  # type: ignore
        session = Session()

        return session

    @classmethod
    def debug_server_client(cls, msg, host=None, port=None, debug_server=[]):
        """Send message to debug server"""
        # #logger.alert(f"host: {host}")  # type: ignore
        # #logger.alert(f"port: {port}")  # type: ignore

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        buffer_size = int(os.getenv('BUFFER_SIZE', '4096'))

        def send_message(message, client_socket, host, port):
            """Send message in chunks with end marker"""
            total_sent = 0
            END_MARKER = '<END>'

            while total_sent < len(message):
                chunk = message[total_sent:total_sent + buffer_size]
                if not hasattr(chunk, 'decode'):
                    client_socket.sendto(chunk.encode(), (host, int(port)))
                else:
                    client_socket.sendto(chunk, (host, int(port)))
                total_sent += buffer_size

            client_socket.sendto(END_MARKER.encode(), (host, int(port)))

        # print(f"get_debug_server(): {get_debug_server()}, type: {type(get_debug_server())}")
        for i in get_debug_server():
            host, port = [i.strip() for i in i.split(':')]
            try:
                if not hasattr(msg, 'decode'):
                    send_message(msg.encode('utf-8'), client_socket, host, int(port))
                else:
                    send_message(msg, client_socket, host, int(port))
            except:
                print(traceback.format_exc())

        client_socket.close()

    @classmethod
    def get_len(cls, objects):
        """Get length of object"""
        if isinstance(objects, (list, tuple, dict)):
            return len(objects)
        else:
            return len(str(objects))

    @classmethod
    def insert_db(cls, message, username=None, password=None, hostname=None, dbname=None, tag='debug'):
        """Insert debug message to database"""
        tag = os.getenv('DEBUG_TAG', os.getenv('DEBUG_APP', 'debug'))
        if not USE_SQL:
            return False

        try:
            session = cls.create_db()
            if not session:
                return False

            new_data = DebugDB(message=message, tag=tag)
            session.add(new_data)
            session.commit()
            session.close()
            return True
        except Exception as e:
            if tprint:
                tprint()
            else:
                tprint()
                # #logger.exception(e)
            return False

    @classmethod
    def format_value(cls, key, value, lexer='python', theme='fruity', ln=True, tab_size=2, width=None, word_wrap=True):
        """Format value for display"""
        if width is None:
            width = get_width()

        formatter_keys_str = os.getenv("FORMATTER_KEYS", 'TRACEBACK')
        SOURCE_MUST_FORMATTED = re.split(r"[ ,#:;]", formatter_keys_str)

        try:
            if hasattr(value, 'decode'):
                value = value.decode()
            value = str(value)
        except Exception as e:
            if tprint:
                tprint()
            else:
                tprint()
                # #logger.exception(e)

        if key.upper() in SOURCE_MUST_FORMATTED:
            if key.lower() == 'traceback':
                lexer = 'pytb'
            if RICH_AVAILABLE:
                return Syntax(value, lexer, theme=theme, line_numbers=ln, tab_size=tab_size, code_width=width, word_wrap=word_wrap)  # type: ignore
        elif key.lower() == 'traceback':
            lexer = 'pytb'
            if RICH_AVAILABLE:
                return Syntax(value, lexer, theme=theme, line_numbers=ln, tab_size=tab_size, code_width=width, word_wrap=word_wrap)  # type: ignore

        try:
            return f"[bold #00FFFF]{value}[/]"
        except:
            return value
        return value

    @classmethod
    def process_kwargs(cls, kwargs, formatlist, lexer, theme, ln, tab_size, width, word_wrap, arrow, use_table):
        formatlist_table = ""

        if not isinstance(kwargs, dict):
            return ""

        for i in kwargs:
            if str(i) in ["cls", "clear"]:
                clear = True
                continue

            # #logger.emergency(f"RICH_AVAILABLE: {RICH_AVAILABLE}")  # type: ignore

            try:
                if kwargs.get(i) == '' or kwargs.get(i) is None:
                    try:
                        formatlist += f"[#00FFFF on #FF00FF]{i}[/]{arrow}"
                    except:
                        formatlist += str(i) + arrow
                else:
                    value = kwargs.get(i)
                    # SEMUA OBJECT DENGAN KEY -> tampilkan key: value -> TYPE -> LEN
                    try:
                        formatlist += f"[#000000 on #FFFF00]{i}:[/] {cls.format_value(i, value, lexer, theme, ln, tab_size, width, word_wrap)}{arrow}[bold #FF557F]TYPE:[/] [#FFFFFF on #0000FF]{str(type(value))}[/]{arrow}[white on #AA00FF]LEN:[/][bold #AAAAFF]{str(cls.get_len(value))}[/]{arrow}"
                        if use_table:
                            formatlist_table += f"[#000000 on #FFFF00]{i}:[/] {cls.format_value(i, value, lexer, theme, ln, tab_size, width, word_wrap)}{arrow}[bold #FF557F]TYPE:[/] [#FFFFFF on #0000FF]{str(type(value))}[/]"
                    except:
                        formatlist += str(i) + ": " + str(value) + arrow + "TYPE: " + str(type(value)) + arrow + "LEN: " + str(cls.get_len(value)) + arrow
            except Exception as e:
                if tprint:
                    tprint()
                else:
                    tprint()
                    # #logger.exception("ERROR in printlist")

                try:
                    cls.debug_server_client(traceback.format_exc())
                except:
                    print("Send traceback ERROR [290]")

        return formatlist, formatlist_table

    @classmethod
    def printlist(cls, simple=False, defname=None, debug=None, host=None, port=None, FILENAME='', print_function_parameters=False, source=False, lexer='python', theme='fruity', ln=True, tab_size=2, width=None, word_wrap=True, caller_frame_index=2, positional_args=None, detected_class=None, detected_line=None, show=True, **kwargs):
        """Format and print debug information"""

        if width is None:
            width = get_width()

        formatlist = ''
        formatlist_table = ''
        main_display_table = ''
        args = ''
        clear = False
        values = []
        pydebugger_style = str(os.getenv('PYDEBUGGER_STYLE', '')).lower() or str(os.getenv('DEBUG_STYLE', '')).lower()
        use_table = (pydebugger_style == 'table')
        sep = os.getenv("DEBUG_SEP", None) or os.getenv("PYDEBUGGER_SEP", '─')

        frame = inspect.currentframe()
        if frame:
            args, _, _, values = inspect.getargvalues(frame)  # type: ignore

        debug = debug or DEBUG

        try:
            color_random = ['#AAFF00', '#FFFF00', '#FFFFFF', '#00FFFF', '#AA55FF']
            arrow = "[bold #AAFF00] -> [/]"
        except:
            color_random = ['', '', '', '', '']
            arrow = ' -> '

        if print_function_parameters:
            for i in args:  # type: ignore
                if i == 'cls':
                    continue

                try:
                    formatlist += f"[white on #0000FF]{i}:[/] [bold {color_random[args.index(i) % len(color_random)]}]{values[i]}[/]{arrow}"  # type: ignore
                except:
                    formatlist += str(i) + ": " + str(values[i]) + arrow  # type: ignore

            if not defname:
                defname = str(inspect.stack()[caller_frame_index][3])

            linenumbers = str(inspect.stack()[caller_frame_index][2])
            FILENAME = FILENAME or sys.argv[0]

            try:
                formatlist = f"[bold #FFFFFF]{datetime.strftime(datetime.now(), '%Y:%m:%d~%H:%M:%S:%f')}[/] [#00FFFF on #FF0000]{defname}{arrow}[/]{formatlist} \[[bold #00FF00]{FILENAME}[/]] \[[bold #FFFF00]{linenumbers}[/]] "
            except:
                formatlist = f"{datetime.strftime(datetime.now(), '%Y:%m:%d~%H:%M:%S:%f')} {defname}{arrow}{formatlist} [{FILENAME}] [{linenumbers}] "

            if debug:
                print(formatlist)
            if get_debug_server():
                cls.debug_server_client(formatlist)

        # Handle positional arguments (string tanpa key)
        if positional_args:
            for arg in positional_args:
                if isinstance(arg, str):
                    try:
                        formatlist += f'[#FFFF00]"{arg}"[/]{arrow}'
                    except:
                        formatlist += f'"{arg}"{arrow}'

            # Add "Start ..." for positional string arguments
            try:
                formatlist += f"[{color_random[int(random.random()*4)]} on #000000]Start ... [/]"
            except:
                formatlist += "Start ... " + arrow

        # #logger.alert(f"get_debug_server(): {get_debug_server()}")

        if kwargs:
            # def process_kwargs(cls, kwargs, formatlist, lexer, theme, ln, tab_size, width, word_wrap, arrow, use_table):
            formatlist, formatlist_table = cls.process_kwargs(kwargs, formatlist, lexer, theme, ln, tab_size, width, word_wrap, arrow, use_table)

        defname_parent = ''
        the_class = detected_class or ''  # Use detected class from debug()

        # Get caller frame info (only if not provided)
        if not detected_line:
            caller_frame = inspect.stack()[caller_frame_index]
            defname = defname or str(caller_frame[3])
            linenumbers = str(caller_frame[2])
            FILENAME = FILENAME or caller_frame[1]
        else:
            # Use provided info from debug()
            linenumbers = str(detected_line)
            # defname already set

        if defname == "<module>":
            defname = (os.path.basename(FILENAME or sys.argv[0])) + arrow

        defparent_name = ''
        # Build parent call chain (optional, might skip for now)
        if len(inspect.stack()) > caller_frame_index + 1 and not simple==True:
            for h in inspect.stack()[caller_frame_index + 1:]:
                # print(f"h = {h}")
                # print(f"h[3] = {h[3]}")
                if isinstance(h[2], int):
                    if not h[3] == '<module>':
                        # if RICH_AVAILABLE and not str(os.getenv('NO_RICH', '0')).lower() in ('1', 'true', 'ok', 'yes', 'on'):
                        try:
                            defname_parent += f"[#FFFFFF on #AA0000]{h[3]}[/][bold #00FFFF]\[[/][#AA007F on #FFFFFF]{str(h[2])}[/][bold #00FFFF]][/]{arrow}"
                            defparent_name += str(h[3])
                        except:
                            defname_parent += f"{h[3]}{arrow}"
                            defparent_name += str(h[3])
        else:
            h = inspect.stack()[caller_frame_index + 1:][0]
            # print(f"h: {h}")
            try:
                defname_parent += f"[#FFFFFF on #AA0000]{h[3]}[/][bold #00FFFF]\[[/][#AA007F on #FFFFFF]{str(h[2])}[/][bold #00FFFF]][/]{arrow}"
                if h[3] == '<module>':
                    defname_parent += ""
                    defparent_name += ""
                else:
                    defparent_name += str(h[3])
            except:
                defname_parent += f"{h[3]}{arrow}"
                defparent_name += str(h[3])

        # print(f"defname_parent: {defname_parent}")
        FILENAME = FILENAME or sys.argv[0]

        # Format display based on class and function
        # if the_class:
        try:
            if use_table:
                os.setenv('LAST_CLASS', the_class)  # type: ignore
                # If inside a class, show: ClassName -> method -> ... [method:file] [line]
                main_display_table = f" {defname_parent[:-7]} ──> " if defparent_name else f"[#00FFFF on #FF0000]{defname}[/] ──> "
            class_name = f"[#FFFFFF on #55007F]{the_class}[/]{arrow}" if the_class else ''
            main_display = f" {class_name}{defname_parent[:-7]} ──> " if defparent_name else f" [#FFFFFF on #55007F]{the_class}[/]{arrow}{defname}"
            detail_display = f"[#FFFFFF on #005500]{defname}[/]: [bold #00AA00 italic]{FILENAME}[/]"
        except:
            main_display = f"{the_class}{arrow}{defname_parent if defname_parent[:-7] + ' ──> ' else defname}"

            detail_display = f"{defname}:{FILENAME}"
        # else:
        #     try:
        #         if use_table:
        #             main_display_table = f" {defname_parent if not defname == defparent_name else ''}[#00FFFF on #FF0000]{defname}[/]"
        #         main_display = f" [#00FFFF on #FF0000]{defname}[/]"
        #         detail_display = f"[#FF0000 on #FFFFFF]{defname}[/]: [bold #00AA00 italic]{FILENAME}[/]"
        #     except:
        #         main_display = defname

        #         detail_display = FILENAME

        # Apply colors to detail display
        try:
            detail_display_colored = f"[bold #00FF00]{detail_display}[/]"  # type: ignore
        except:
            detail_display_colored = detail_display

        try:
            if use_table:
                formatlist_table = f"{main_display_table}{arrow}{formatlist_table}"
            try:
                formatlist = f"[#000000 on #00FFFF]{datetime.strftime(datetime.now(), '%Y:%m:%d~%H:%M:%S:%f')}[/]{main_display}{formatlist}[{detail_display_colored}][bold #00FFFF]\[[/][#FFFFFF on #AA007F]{str(linenumbers)}[/][bold #00FFFF]][/] [bold #FF5500]PID:[/][#FFFFFF on #000000]{PID}[/]"
            except:
                pass
        except:
            formatlist = f"{datetime.strftime(datetime.now(), '%Y:%m:%d~%H:%M:%S:%f')} {main_display}{formatlist} [{detail_display_colored}] [{linenumbers}] PID:{PID}"

        debug_enabled = str(os.getenv("DEBUG", DEBUG)).lower() in ('1', 'true', 'ok', 'yes', 'on')

        if debug_enabled or debug:
            if RICH_AVAILABLE and not str(os.getenv('NO_RICH', '0')).lower() in ('1', 'true', 'ok', 'yes', 'on') and use_table and show:
                try:

                    timestamp = datetime.strftime(datetime.now(), '%Y:%m:%d~%H:%M:%S:%f')
                    # class_method = f"{the_class} | {defname}" if the_class else defname

                    # # Build content
                    # content_parts = []
                    # if positional_args:
                    #     for arg in positional_args:
                    #         if isinstance(arg, str):
                    #             content_parts.append(f'"{arg}"')
                    #     if content_parts:
                    #         content_parts.append("Start ...")

                    # if kwargs:
                    #     for key in kwargs:
                    #         if key not in ["cls", "clear", "debug", "host", "port", "defname"]:
                    #             value = kwargs.get(key)
                    #             content_parts.append(f"{key}: {value} -> TYPE: {type(value).__name__} -> LEN: {cls.get_len(value)}")

                    # content = " -> ".join(content_parts) if content_parts else ""

                    # Create table with proportional columns
                    tbl = Table.grid(padding=(0, 1), pad_edge=False, expand=True)  # type: ignore
                    tbl.add_column(justify="left", style="#000000 on #00FFFF", no_wrap=True, width=25)  # Timestamp
                    tbl.add_column(justify="left", style="#FFFFFF on #55007F", no_wrap=False,)  # Class | Method
                    tbl.add_column(justify="left", style="white", overflow="fold", ratio=60)  # Content
                    tbl.add_column(justify="left", style="#FFFFFF on #AA007F", no_wrap=True)  # Line
                    tbl.add_column(justify="right", style="#AAAAFF on #000000", no_wrap=True)  # PID

                    tbl.add_row(timestamp, " " + f"{the_class if the_class else '-' * len(os.getenv('LAST_CLASS', ''))}", formatlist_table, f" {linenumbers:02}", f" {PID}")  # type: ignore
                    tbl.add_row("", "", f" [bold #00FF00]{detail_display}[/]", "", "")

                    if source:
                        frame_globals = caller_frame[0].f_globals  # type: ignore
                        if defname in frame_globals and inspect.isfunction(frame_globals[defname]):  # type: ignore
                            tbl.add_row(timestamp, " " + f"{the_class if the_class else '-' * len(os.getenv('LAST_CLASS', ''))}", get_source(no_print=True), f" {linenumbers:02}", f" {PID}")  # type: ignore
                            tbl.add_row("", "", f" [bold #00FF00]{detail_display}[/]", "", "")

                    console.print(tbl)  # type: ignore

                except Exception as e:
                    print(f"[TABLE ERROR] {e}")
                    traceback.print_exc()
                    print(formatlist)

            elif RICH_AVAILABLE and not str(os.getenv('NO_RICH', '0')).lower() in ('1', 'true', 'ok', 'yes', 'on') and show:
                console.print(formatlist)  # type: ignore
                if sep: print(sep*get_width())
            else:
                if show:
                    print(formatlist)
                    if sep: print(sep*get_width())

            if source and show:
                frame_globals = caller_frame[0].f_globals  # type: ignore
                if defname in frame_globals and inspect.isfunction(frame_globals[defname]):  # type: ignore
                    get_source(frame_globals[defname], lexer, theme, ln, tab_size, width, word_wrap)  # type: ignore

        # print(f"get_debug_server(): {get_debug_server()}")
        if get_debug_server():
            if clear:
                formatlist = 'cls'
            cls.debug_server_client(formatlist, host, port)

        return formatlist

    @classmethod
    def db_log(cls, tag=None):
        """Monitor database logs in real-time"""
        if not USE_SQL:
            print("SQL support not available")
            return

        session = cls.create_db()
        if not session:
            print("Cannot create database session")
            return

        last_id_first = None
        if tag is None:
            tag = ''
        tag = tag.strip()

        try:
            if tag:
                result = session.query(DebugDB.id).filter(DebugDB.tag == tag).order_by(DebugDB.id.desc()).first()
            else:
                result = session.query(DebugDB.id).order_by(DebugDB.id.desc()).first()

            if result:
                last_id_first = result[0]
        except:
            pass

        try:
            while True:
                if last_id_first:  # type: ignore
                    if tag:
                        data = session.query(DebugDB).filter(DebugDB.tag == tag).order_by(DebugDB.id.desc()).first()
                    else:
                        data = session.query(DebugDB).order_by(DebugDB.id.desc()).first()

                    if data:
                        last_id = data.id
                        if not last_id == last_id_first:  # type: ignore
                            if tag:
                                query = session.query(DebugDB).filter(DebugDB.id > last_id_first, DebugDB.id <= last_id, DebugDB.tag == tag).order_by(DebugDB.id)
                            else:
                                query = session.query(DebugDB).filter(DebugDB.id > last_id_first, DebugDB.id <= last_id).order_by(DebugDB.id)

                            count = query.count()
                            limit = count
                            query = query.limit(limit)
                            data_list = query.all()

                            last_id_first = last_id
                            for i in data_list:
                                message = i.message
                                if hasattr(message, 'decode'):
                                    message = message.decode('utf-8')
                                try:
                                    console.print(f"[#5500FF on #FFFFFF]{message} [bold #FF00AA]{i.tag}[/]")  # type: ignore
                                except:
                                    print(message + " " + str(i.tag))
                time.sleep(0.5)

        except KeyboardInterrupt:
            sys.exit(0)

#print(f"os.getenv('DEBUG') X: {os.getenv('DEBUG')}")

def debugme(**kwargs):

    if str(os.getenv('PYDEBUGGER_DEBUG', '0')).lower() in ['1', 'true', 'ok' ,'yes', 'on']:
        kwargs.update({'debug': '1'})
        debugger(kwargs.get('defname', None), debug).printlist(**kwargs)

def debug(*args, defname=None, debug=None, host=None, port=None, tag='debug', 
    print_function_parameters=False, source=False, simple=False, show=True, **kwargs):
    """Main debug function"""
    # print(f"os.getenv('DEBUG') X: {os.getenv('DEBUG')}")
    debug_enabled = str(os.getenv("DEBUG", DEBUG)).lower() in ('1', 'true', 'ok', 'yes', 'on')
    # print(f"debug_enabled: {debug_enabled}")
    debugme(debug_enabled = debug_enabled)
    # print(f"debug: {debug}")
    # print(f"debug_enabled: {debug_enabled}")
    # print(f"get_debug_server(): {get_debug_server()}")

    if not debug and not debug_enabled and not get_debug_server():
        return None

    msg = ''
    tag = os.getenv('DEBUG_TAG', os.getenv('DEBUG_APP', 'debug'))

    # Get caller information HERE, before passing to printlist
    caller_frame = inspect.stack()[1]  # Direct caller of debug()
    caller_locals = caller_frame[0].f_locals

    # Detect class name from caller
    detected_class = None
    if 'self' in caller_locals:
        detected_class = caller_locals['self'].__class__.__name__
    elif 'cls' in caller_locals:
        detected_class = caller_locals['cls'].__name__

    if os.getenv('DEBUG_FRAME'):
        print(f"\n=== DEBUG FUNCTION ===")
        print(f"Caller: {caller_frame[3]} at line {caller_frame[2]}")
        print(f"Caller locals: {list(caller_locals.keys())}")
        print(f"Detected class: {detected_class}")

    # Separate positional args (for plain strings)
    positional_args = list(args) if args else None

    c = debugger(defname, debug)
    # Pass detected class and caller info
    msg = c.printlist(
        simple=simple,
        defname=defname or caller_frame[3],
        debug=debug,
        host=host,
        port=port,
        FILENAME=caller_frame[1],
        print_function_parameters=print_function_parameters,
        source=source,
        caller_frame_index=1,  # From debug() perspective
        positional_args=positional_args,
        detected_class=detected_class,
        detected_line=caller_frame[2],
        show=show,
        **kwargs
    )

    db_active = str(os.getenv('DB_ACTIVE', '0')).lower() in ('1', 'true', 'ok', 'yes', 'on')
    if db_active:
        c.insert_db(msg, tag=tag)

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
        tprint()
        # #logger.exception(e, show = True)  # type: ignore

    return "UNKNOWN VERSION"


def handle_windows():
    """Get window handle for Windows"""
    global HANDLE
    if sys.platform == 'win32':
        HANDLE = ctypes.windll.user32.GetForegroundWindow()


def usage():
    """Create argument parser"""
    try:
        from rchf import CustomRichHelpFormatter  # type: ignore
    except:
        CustomRichHelpFormatter = argparse.RawTextHelpFormatter

    parser = argparse.ArgumentParser(
        prog='debug',
        description='🐍 Run debugger as server, receive debug message with default port is 50001',
        formatter_class=CustomRichHelpFormatter
    )

    # === Global Command ===
    parser.add_argument('-a', '--on-top', action='store_true', help='Always On Top', dest="ON_TOP")
    parser.add_argument('-c', '--cleanup', action='store', help='CleanUp File')
    parser.add_argument('-v', '--version', action='store_true', help='Get version number')

    # === Subcommand: serve ===
    subparsers = parser.add_subparsers(dest='COMMAND', help='Available subCommands')

    serve_parser = subparsers.add_parser('serve', help='Run debug message UDP server', formatter_class=CustomRichHelpFormatter)
    serve_parser.add_argument('--host', default='0.0.0.0', help='Host to bind, default: 0.0.0.0')
    serve_parser.add_argument('--port', type=int, default=50001, help='Port to bind, default: 50001')
    serve_parser.add_argument('-a', '--on-top', action='store_true', help='Always On Top')

    # === Subcommand: log ===
    log_parser = subparsers.add_parser('log', help='Database log inspection', formatter_class=CustomRichHelpFormatter)
    log_parser.add_argument('-l', '--db-log', action='store_true', help='Get Database log')
    log_parser.add_argument('-L', '--db-log-tag', action='store', help='Filter Database log by tag')

    # === Subcommand: cleanup ===
    cleanup_parser = subparsers.add_parser('cleanup', help='Cleanup file', formatter_class=CustomRichHelpFormatter)
    cleanup_parser.add_argument('path', help='Path file to clean')

    # === Subcommand: version ===
    version_parser = subparsers.add_parser('version', help='Print version info')

    # === Subcommand: cleaner ===
    cleaner_parser = subparsers.add_parser('cleaner', help='Cleaner file (comment out/in)', formatter_class=CustomRichHelpFormatter)
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
    """Main entry point"""
    handle_windows()

    try:
        from .cleaner import DebugCleaner  # type: ignore
    except:
        try:
            from cleaner import DebugCleaner  # type: ignore
        except:
            DebugCleaner = None

    # Handle simple port/host arguments
    if len(sys.argv) == 3:
        arg1, arg2 = sys.argv[1], sys.argv[2]

        # Check if arg1 is an IP address
        if len(arg1.split(".")) == 4 and not arg1.replace('.', '').isdigit():
            if arg2.isdigit():
                serve(arg1, int(arg2))
                return
            else:
                serve(arg1, 50001)
                return
        # Check if arg2 is an IP address
        elif len(arg2.split(".")) == 4 and not arg2.replace('.', '').isdigit():
            if arg1.isdigit():
                serve(arg2, int(arg1))
                return
            else:
                serve(arg2, 50001)
                return

    elif len(sys.argv) == 2:
        arg1 = sys.argv[1]
        # Check if it's a port number
        if arg1.isdigit():
            serve(port=int(arg1))
            return
        # Check if it's an IP address
        elif len(arg1.split(".")) == 4:
            serve(arg1, 50001)
            return

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
                tprint()
                # #logger.exception(e)
            sys.exit(0)

    args = parser.parse_args()

    if args.version:
        try:
            console.print(f"[bold #00FFFF]VERSION:[/] [bold #FFFF00]{version()}[/]")  # type: ignore
        except:
            print("VERSION:", version())
        sys.exit()

    if args.COMMAND == 'cleaner':
        if not DebugCleaner:
            print("DebugCleaner module not available")
            return

        manager = DebugCleaner()
        python_files = manager.find_python_files(args.path)

        if not python_files:
            if RICH_AVAILABLE:
                console.print("⚠️ [bold yellow]No Python files found.[/]")  # type: ignore
            else:
                print("⚠️ No Python files found.")
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
        serve(args.host, args.port, args.on_top or args.ON_TOP)

    elif args.COMMAND == 'log':
        if args.db_log:
            debugger.db_log()
        elif args.db_log_tag:
            debugger.db_log(args.db_log_tag)

    elif args.COMMAND == 'cleanup':
        print("CLEANUP ........")
        cleanup(args.path)

    elif args.COMMAND == 'version':
        try:
            console.print(f"[bold #00FFFF]VERSION:[/] [bold #FFFF00]{version()}[/]")  # type: ignore
        except:
            print("VERSION:", version())
        sys.exit()

if __name__ == '__main__':
    if sys.platform == 'win32':
        try:
            kernel32 = ctypes.WinDLL('kernel32')
            handle2 = ctypes.windll.user32.GetForegroundWindow()
            HANDLE = handle2
            try:
                console.print(f"HANDLE: [#FFFFFF on #5500FF]{HANDLE}[/] | PID: [#FFFFFF on #0000FF]{PID}[/]")  # type: ignore
            except:
                print("HANDLE:", HANDLE, "| PID:", PID)
        except:
            print(f"PID: {PID}")
    else:
        print(f"PID: {PID}")

    main()
