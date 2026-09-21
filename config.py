from pathlib import Path
from configparser import ConfigParser
import json
import os
from rich.theme import Theme
from rich.console import Console
import shutil
import cmdw
from functools import wraps


# Metaclass untuk mengonversi metode instance menjadi classmethod
class ClassMethodMeta(type):
    def __new__(mcs, name, bases, attrs):
        attrs['_config_instance'] = None  # tidak pakai configset lagi

        # Fungsi pembungkus untuk mengubah method menjadi classmethod
        def make_classmethod(method):
            @wraps(method)
            def classmethod_wrapper(cls, *args, **kwargs):
                return method(cls._config_instance, *args, **kwargs)
            return classmethod(classmethod_wrapper)

        # Ambil semua method dari base class dan attrs, lalu jadikan classmethod
        for base in bases:
            for attr_name, attr_value in base.__dict__.items():
                if callable(attr_value) and not attr_name.startswith('__'):
                    attrs[attr_name] = make_classmethod(attr_value)
        for attr_name, attr_value in attrs.copy().items():
            if callable(attr_value) and not attr_name.startswith('__'):
                attrs[attr_name] = make_classmethod(attr_value)

        return super().__new__(mcs, name, bases, attrs)

    def __getattr__(cls, name):
        if hasattr(cls, '_data') and name in cls._data:
            return cls._data[name]
        raise AttributeError(f"type object '{cls.__name__}' has no attribute '{name}'")

    def __setattr__(cls, name, value):
        if hasattr(cls, '_data') and name in cls._data:
            cls._data[name] = value
            if hasattr(cls, '_config_file'):
                with open(cls._config_file, "w") as f:
                    json.dump(cls._data, f, indent=4)
        else:
            super().__setattr__(name, value)


class CONFIG(metaclass=ClassMethodMeta):
    _config_file = Path.cwd() / 'debug.json' if (Path.cwd() / 'debug.json').is_file() else Path(__file__).parent / "debug.json"
    _config_ini_file = Path.cwd() / 'debug.ini' if (Path.cwd() / 'debug.ini').is_file() else Path(__file__).parent / "debug.ini"

    parser = ConfigParser()
    if _config_ini_file.is_file():
        parser.read(_config_ini_file)

    @classmethod
    def get_config(cls, section, key, fallback=None):
        return cls.parser.get(section, key, fallback=fallback) if cls.parser.has_option(section, key) else fallback

    @classmethod
    def get_config_as_list(cls, section, key, fallback=None):
        if cls.parser.has_option(section, key):
            return [x.strip() for x in cls.parser.get(section, key).split(",") if x.strip()]
        return fallback if fallback is not None else []

    severity_theme = Theme({
        "emergency": "#FFFFFF on #ff00ff",
        "emerg": "#FFFFFF on #ff00ff",
        "alert": "white on #005500",
        "ale": "white on #005500",
        "aler": "white on #005500",
        'critical': "white on #0000FF",
        'criti': "white on #0000FF",
        'crit': "white on #0000FF",
        "error": "white on red",
        "err": "white on red",
        "warning": "black on #FFFF00",
        "warni": "black on #FFFF00",
        "warn": "black on #FFFF00",
        'notice': "black on #55FFFF",
        'notic': "black on #55FFFF",
        'noti': "black on #55FFFF",
        "info": "bold #AAFF00",
        "debug": "black on #FFAA00",
        "deb": "black on #FFAA00",
        "unknown": "white on #FF00FF"
    })

    console = Console(theme=severity_theme)

    # Semua default config dari script awal tetap ada di sini
    _data_default = {
        'MAX_WIDTH': shutil.get_terminal_size()[0] if shutil.get_terminal_size() else cmdw.getWidth() or 120,
        'CONFIGFILE': str(_config_ini_file),
        'DEBUG': '127.0.0.1',
        'DEBUG_SERVER': '514',
        'DEBUGGER_SERVER': '127.0.0.1',
        'DEBUG_HOST': '7000',
        'DEBUG_PORT': 1,
        'VERSION': "TracebackLogger",
        'BUFFER_SIZE': "1",
        'LOG_FILE': os.path.join(str(Path(__file__).parent), "traceback.log"),
        'ON_TOP': 0,
        'USE_SQL': 0,
        'DB_TYPE': '',
        'DB_NAME': 'ctraceback',
        'DB_USERNAME': '',
        'DB_PASSWORD': '',
        'DB_HOST': '',
        'DB_PORT': '',
        'DB_LOG': False,
        'TO_SYSLOG': False,
        'TO_FILE': False,
        'TO_DB': False,
        'SYSLOG_HOST': '127.0.0.1',
        'SYSLOG_PORRT': '514',

        'USE_RABBITMQ': True,
        'RABBITMQ_HOST': '127.0.0.1',
        'RABBITMQ_PORT': 5672,
        'RABBITMQ_USERNAME': 'guest',
        'RABBITMQ_PASSWORD': 'guest',
        'RABBITMQ_EXCHANGE_NAME': 'ctraceback',
        'RABBITMQ_EXCHANGE_TYPE': 'ctraceback',
        'RABBITMQ_MAX_LENGTH': 100,
        'RABBITMQ_DURABLE': False,
        'RABBITMQ_ACK': False,
        'RABBITMQ_ROUTING_KEY': ['ctraceback.error', 'ctraceback.100'],
        'RABBITMQ_CONSUMER_TAG': 'all',

        'USE_KAFKA': False,
        'KAFKA_BOOTSTRAP_SERVER': '127.0.0.1',
        'KAFKA_PORT': 5672,
        'KAFKA_USERNAME': 'guest',
        'KAFKA_PASSWORD': 'guest',
        'KAFKA_TOPIC_NAME': 'log',
        'KAFKA_GROUP_ID': 'ctraceback',
        'KAFKA_MAX_LENGTH': 100,

        'USE_PULSAR': False,
        'PULSAR_HOST': '192.168.100.2',
        'PULSAR_PORT': 6650,
        'PULSAR_PORT_API': 8080,
        'PULSAR_USERNAME': 'pulsar',
        'PULSAR_PASSWORD': 'pulsar',
        'PULSAR_TENANT': 'ctraceback_tenant',
        'PULSAR_NAMESPACE': 'ctraceback_namespace',
        'PULSAR_TOPIC': 'ctraceback_topic',
        'PULSAR_SUB': 'ctraceback_sub',
        'PULSAR_MAX_LENGTH': 100,
        'PULSAR_AUTH_TOKEN': '',
        'PULSAR_VERBOSE': '',
        'PULSAR_ADMIN_ROLES': [],
        'PULSAR_ALLOWED_CLUSTERS': ['standalone'],
        'PULSAR_RETENTION_TIME_IN_MINUTES': 10080,
        'PULSAR_RETENTION_SIZE_IN_MB': 100,
        'PULSAR_CONSUMER_TYPE': 'Shared',
        'PULSAR_BATCHING': False,
        'PULSAR_BATCHING_MAX_PUBLISH_DELAY_MS': False,
        'PULSAR_COMPRESSION_TYPE': 'LZ4',
    }

    def __init__(self):
        # mulai dari default
        self._data = self._data_default.copy()

        # override dengan JSON kalau ada
        if self._config_file.exists():
            with open(self._config_file, "r") as f:
                self._data.update(json.load(f))

        # override dengan INI kalau ada
        self._data.update({
            'MAX_WIDTH': self.get_config('terminal', 'width', self._data['MAX_WIDTH']),
            'DEBUG': self.get_config('syslog', 'host', self._data['DEBUG']),
            'DEBUG_SERVER': self.get_config('syslog', 'port', self._data['DEBUG_SERVER']),
            'DEBUGGER_SERVER': self.get_config('server', 'host', self._data['DEBUGGER_SERVER']),
            'DEBUG_HOST': self.get_config('server', 'port', self._data['DEBUG_HOST']),
            'DEBUG_PORT': int(self.get_config('server', 'active', str(self._data['DEBUG_PORT']))),
            'VERSION': self.get_config('tag', 'name', self._data['VERSION']),
            'BUFFER_SIZE': self.get_config('rich', 'show_local', self._data['BUFFER_SIZE']),
            'LOG_FILE': self.get_config('file', 'name', self._data['LOG_FILE']),
            'ON_TOP': int(self.get_config('on_top', 'active', str(self._data['ON_TOP']))),
            'USE_SQL': int(self.get_config('db', 'active', str(self._data['USE_SQL']))),
            'DB_TYPE': self.get_config('db', 'type', self._data['DB_TYPE']),
            'DB_NAME': self.get_config('db', 'name', self._data['DB_NAME']),
            'DB_USERNAME': self.get_config('db', 'username', self._data['DB_USERNAME']),
            'DB_PASSWORD': self.get_config('db', 'password', self._data['DB_PASSWORD']),
            'DB_HOST': self.get_config('db', 'HOST', self._data['DB_HOST']),
            'DB_PORT': self.get_config('db', 'PORT', self._data['DB_PORT']),
            'DB_LOG': self.get_config('db', 'LOG', self._data['DB_LOG']),
            'TO_SYSLOG': self.get_config('syslog', 'active', self._data['TO_SYSLOG']),
            'TO_FILE': self.get_config('file', 'active', self._data['TO_FILE']),
            'TO_DB': self.get_config('db', 'active', self._data['TO_DB']),
            'SYSLOG_HOST': self.get_config('syslog', 'host', self._data['SYSLOG_HOST']),
            'SYSLOG_PORRT': self.get_config('syslog', 'port', self._data['SYSLOG_PORRT']),

            'USE_RABBITMQ': self.get_config('rabbitmq', 'active', str(self._data['USE_RABBITMQ'])) in ['1', 'true', 'True', 'TRUE'],
            'RABBITMQ_HOST': self.get_config('rabbitmq', 'host', self._data['RABBITMQ_HOST']),
            'RABBITMQ_PORT': self.get_config('rabbitmq', 'port', self._data['RABBITMQ_PORT']),
            'RABBITMQ_USERNAME': self.get_config('rabbitmq', 'username', self._data['RABBITMQ_USERNAME']),
            'RABBITMQ_PASSWORD': self.get_config('rabbitmq', 'password', self._data['RABBITMQ_PASSWORD']),
            'RABBITMQ_EXCHANGE_NAME': self.get_config('rabbitmq', 'exchange_name', self._data['RABBITMQ_EXCHANGE_NAME']),
            'RABBITMQ_EXCHANGE_TYPE': self.get_config('rabbitmq', 'exchange_type', self._data['RABBITMQ_EXCHANGE_TYPE']),
            'RABBITMQ_MAX_LENGTH': self.get_config('rabbitmq', 'max_length', self._data['RABBITMQ_MAX_LENGTH']),
            'RABBITMQ_DURABLE': self.get_config('rabbitmq', 'durable', self._data['RABBITMQ_DURABLE']),
            'RABBITMQ_ACK': self.get_config('rabbitmq', 'ack', self._data['RABBITMQ_ACK']),
            'RABBITMQ_ROUTING_KEY': self.get_config_as_list('rabbitmq', 'routing_key', self._data['RABBITMQ_ROUTING_KEY']),
            'RABBITMQ_CONSUMER_TAG': self.get_config('rabbitmq', 'consumer_tag', self._data['RABBITMQ_CONSUMER_TAG']),

            'USE_KAFKA': self.get_config('kafka', 'active', str(self._data['USE_KAFKA'])) in ['1', 'true', 'True', 'TRUE'],
            'KAFKA_BOOTSTRAP_SERVER': self.get_config('kafka', 'host', self._data['KAFKA_BOOTSTRAP_SERVER']),
            'KAFKA_PORT': self.get_config('kafka', 'port', self._data['KAFKA_PORT']),
            'KAFKA_USERNAME': self.get_config('kafka', 'username', self._data['KAFKA_USERNAME']),
            'KAFKA_PASSWORD': self.get_config('kafka', 'password', self._data['KAFKA_PASSWORD']),
            'KAFKA_TOPIC_NAME': self.get_config('kafka', 'topic', self._data['KAFKA_TOPIC_NAME']),
            'KAFKA_GROUP_ID': self.get_config('kafka', 'group', self._data['KAFKA_GROUP_ID']),
            'KAFKA_MAX_LENGTH': self.get_config('kafka', 'max_length', self._data['KAFKA_MAX_LENGTH']),

            'USE_PULSAR': self.get_config('pulsar', 'active', str(self._data['USE_PULSAR'])) in ['1', 'true', 'True', 'TRUE'],
            'PULSAR_HOST': self.get_config('pulsar', 'host', self._data['PULSAR_HOST']),
            'PULSAR_PORT': self.get_config('pulsar', 'port', self._data['PULSAR_PORT']),
            'PULSAR_PORT_API': self.get_config('pulsar', 'port_api', self._data['PULSAR_PORT_API']),
            'PULSAR_USERNAME': self.get_config('pulsar', 'username', self._data['PULSAR_USERNAME']),
            'PULSAR_PASSWORD': self.get_config('pulsar', 'password', self._data['PULSAR_PASSWORD']),
            'PULSAR_TENANT': self.get_config('pulsar', 'tenant', self._data['PULSAR_TENANT']),
            'PULSAR_NAMESPACE': self.get_config('pulsar', 'namespace', self._data['PULSAR_NAMESPACE']),
            'PULSAR_TOPIC': self.get_config('pulsar', 'topic', self._data['PULSAR_TOPIC']),
            'PULSAR_SUB': self.get_config('pulsar', 'sub', self._data['PULSAR_SUB']),
            'PULSAR_MAX_LENGTH': self.get_config('pulsar', 'max_length', self._data['PULSAR_MAX_LENGTH']),
            'PULSAR_AUTH_TOKEN': self.get_config('pulsar', 'token', self._data['PULSAR_AUTH_TOKEN']),
            'PULSAR_VERBOSE': self.get_config('pulsar', 'verbose', self._data['PULSAR_VERBOSE']),
            'PULSAR_ADMIN_ROLES': self.get_config_as_list('pulsar', 'admin_roles', self._data['PULSAR_ADMIN_ROLES']),
            'PULSAR_ALLOWED_CLUSTERS': self.get_config_as_list('pulsar', 'allowed_clusters', self._data['PULSAR_ALLOWED_CLUSTERS']),
            'PULSAR_RETENTION_TIME_IN_MINUTES': self.get_config('pulsar', 'retention_time_in_minutes', self._data['PULSAR_RETENTION_TIME_IN_MINUTES']),
            'PULSAR_RETENTION_SIZE_IN_MB': self.get_config('pulsar', 'retention_size_in_mb', self._data['PULSAR_RETENTION_SIZE_IN_MB']),
            'PULSAR_CONSUMER_TYPE': self.get_config('pulsar', 'consumer_type', self._data['PULSAR_CONSUMER_TYPE']),
            'PULSAR_BATCHING': self.get_config('pulsar', 'batching', self._data['PULSAR_BATCHING']),
            'PULSAR_BATCHING_MAX_PUBLISH_DELAY_MS': self.get_config('pulsar', 'batching_max_publish_delay', self._data['PULSAR_BATCHING_MAX_PUBLISH_DELAY_MS']),
            'PULSAR_COMPRESSION_TYPE': self.get_config('pulsar', 'compression_type', self._data['PULSAR_COMPRESSION_TYPE']),
        })

    def __repr__(self):
        return f"{self.__class__.__name__}({self._data})"

    def __getattr__(self, name):
        if name in self._data:
            return self._data[name]
        elif self._config_file.exists() and not name in self._data and name in self._data_default:
            self.__setattr__(name, '')
            return self._data[name]
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    @classmethod
    def set(cls, key, value):
        key = str(key).upper()
        cls.console.print(f"[bold #FFFF00]Write/Set config[/] [bold #00FFFF]{key}[/] [bold #FFAAFF]-->[/] [bold ##00AAFF]{value if value else ''}[/]")
        if str(value).isdigit():
            value = int(value)
        return CONFIG().__setattr__(key, value)

    def __setattr__(self, name, value):
        if name in {"_config_file", "_data"}:
            super().__setattr__(name, value)
        else:
            self._data[name] = value
            with open(self._config_file, "w") as f:
                json.dump(self._data, f, indent=4)
