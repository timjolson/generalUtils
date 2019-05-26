import logging
from multiprocessing import current_process, managers
import threading
import queue
import sys
import os

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class AcquirerProxy(managers.AcquirerProxy):
    _exposed_ = ('acquire', 'release', '__enter__', '__exit__')


class MPStorage(managers.SyncManager):
    def __init__(self, *args, **kwargs):
        """
        :param(s): accepts same parameters as multiprocessing.managers.BaseManager
        """
        super().__init__(*args, **kwargs)
        self.access = None
        self._storage = dict()

        self.__class__.register(
            'getQueue',
            lambda k, *a, **kw: self._getitem(k, queue.Queue, *a, **kw)
        )
        self.__class__.register(
            'getJoinableQueue',
            lambda k, *a, **kw: self._getitem(k, queue.Queue, *a, **kw),
        )
        self.__class__.register(
            'getEvent',
            lambda k, *a, **kw: self._getitem(k, threading.Event, *a, **kw),
            proxytype=managers.EventProxy
        )
        self.__class__.register(
            'getLock',
            lambda k, *a, **kw: self._getitem(k, threading.Lock, *a, **kw),
            proxytype=AcquirerProxy
        )
        self.__class__.register(
            'getRLock',
            lambda k, *a, **kw: self._getitem(k, threading.RLock, *a, **kw),
            proxytype=AcquirerProxy
        )
        self.__class__.register(
            'getSemaphore',
            lambda k, *a, **kw: self._getitem(k, threading.Semaphore, *a, **kw),
            proxytype=AcquirerProxy
        )
        self.__class__.register(
            'getBoundedSemaphore',
            lambda k, *a, **kw: self._getitem(k, threading.BoundedSemaphore, *a, **kw),
            proxytype=AcquirerProxy
        )
        self.__class__.register(
            'getCondition',
            lambda k, *a, **kw: self._getitem(k, threading.Condition, *a, **kw),
            proxytype=managers.ConditionProxy
        )
        self.__class__.register(
            'getBarrier',
            lambda k, *a, **kw: self._getitem(k, threading.Barrier, *a, **kw),
            proxytype=managers.BarrierProxy
        )
        self.__class__.register(
            'getPool',
            lambda k, *a, **kw: self._getitem(k, pool.Pool, *a, **kw),
            proxytype=managers.PoolProxy
        )
        self.__class__.register(
            'getList',
            lambda k, *a, **kw: self._getitem(k, list, *a, **kw),
            proxytype=managers.ListProxy
        )
        self.__class__.register(
            'getDict',
            lambda k, *a, **kw: self._getitem(k, dict, *a, **kw),
            proxytype=managers.DictProxy
        )
        self.__class__.register(
            'getValue',
            lambda k, *a, **kw: self._getitem(k, managers.Value, *a, **kw),
            proxytype=managers.ValueProxy
        )
        self.__class__.register(
            'getArray',
            lambda k, *a, **kw: self._getitem(k, managers.Array, *a, **kw),
            proxytype=managers.ArrayProxy
        )
        self.__class__.register(
            'getNamespace',
            lambda k, *a, **kw: self._getitem(k, managers.Namespace, *a, **kw),
            proxytype=managers.NamespaceProxy
        )

        self.logger = logging.getLogger(
            '.'.join([__name__, self.__class__.__name__, str(self.address)]))
        self.logger.addHandler(logging.NullHandler())

    def _getitem(self, key, _type, *args, **kwargs):
        if _type not in self._storage.keys():
            self.logger.info(f"Creating dict for type {_type}")
            self._storage[_type] = dict()
        if key not in self._storage[_type].keys():
            self.logger.info(f"Creating {_type} for key '{key}'")
            item = _type(*args, **kwargs)
            self._storage[_type][key] = item
        return self._storage[_type][key]

    def start(self, *args, **kwargs):
        back = sys.stderr
        try:
            self.logger.info("Server starting...")
            sys.stderr = os.devnull
            super().start(*args, **kwargs)
            self.access = 'server'
            sys.stderr = back
            self.logger.info("Server started.")
        except EOFError:
            self.logger.warning("Server already running.")
            super().connect()
            self.access = 'client'
            sys.stderr = back
        finally:
            sys.stderr = back
        return self


if 'redis' in sys.modules:
    import redis
    address = ('localhost', 6379)
    _server = redis.Redis(host=address[0], port=address[1])
    _server.ping()
    _getlock = lambda n, *x, **k: _server.lock(str(n), *x, **k)
else:
    address = ('localhost', 12345)
    authkey = b'localhost:12345.__mp_log_handlers'
    _server = MPStorage(address, authkey=authkey)
    _getlock = lambda n, *x, **k: _server.getRLock(str(n), *x, **k)


class MPStreamHandler(logging.StreamHandler):
    def __init__(self, stream=None):
        if isinstance(_server, MPStorage):
            if _server._state.value == managers.State.INITIAL:
                _server.start()

        if stream is None:
            stream = sys.stderr
        self.stream = stream
        logging.Handler.__init__(self)

    def createLock(self):
        def get_name(stm):
            if hasattr(stm, 'buffer'):
                buffer = stm.buffer
                if hasattr(buffer, 'raw'):
                    raw = buffer.raw
                    if hasattr(raw, 'name'):
                        if isinstance(raw.name, str):
                            return raw.name
                if hasattr(buffer, 'name'):
                    if isinstance(buffer.name, (str, int)):
                        return buffer.name
            if hasattr(stm, 'name'):
                if isinstance(stm.name, (str, int)):
                    return stm.name
            return None

        key = get_name(self.stream)
        try: key = (current_process().pid, int(key))
        except: pass

        if isinstance(key, str):
            key = os.path.abspath(key)

        if key is None:
            key = (current_process().pid, str(self.stream))

        logger.debug(f".MPStreamHandler:{self.stream} makes key {key}")

        self.lock = _getlock(key)

    def flush(self):
        if self.stream and hasattr(self.stream, "flush"):
            self.stream.flush()

    def emit(self, record):
        try:
            msg = self.format(record)
            stream = self.stream
            with self.lock:
                stream.write(msg)
                stream.write(self.terminator)
                self.flush()
        except Exception:
            self.handleError(record)

    def handle(self, record):
        rv = self.filter(record)
        if rv:
            self.emit(record)
        return rv


class MPFileHandler(MPStreamHandler):
    def __init__(self, filename, mode='a', encoding=None, delay=False):
        filename = os.fspath(filename)

        self.baseFilename = os.path.abspath(filename)
        self.mode = mode
        self.encoding = encoding
        self.delay = delay
        if delay:
            logging.Handler.__init__(self)
            self.stream = None
        else:
            MPStreamHandler.__init__(self, self._open())

    def _open(self):
        if not os.path.exists(os.path.dirname(self.baseFilename)):
            os.makedirs(os.path.dirname(self.baseFilename))
        return open(self.baseFilename, self.mode, encoding=self.encoding)

    def createLock(self):
        key = self.baseFilename
        self.lock = _getlock(key)

    def emit(self, record):
        try:
            msg = self.format(record)
            with self.lock:
                if self.stream is None:
                    self.stream = self._open()
                stream = self.stream
                stream.write(msg)
                stream.write(self.terminator)
                self.flush()
        except Exception:
            self.handleError(record)


__all__ = ['MPStreamHandler', 'MPFileHandler', 'MPStorage']
