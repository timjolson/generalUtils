from multiprocessing import Lock
import logging
from .general_utils import ensure_file
from time import time


class Logger():
    """class logs messages to a file, uses locks to prevent garbling.
    Written by Tim Olson - tim.lsn@gmail.com

    obj = Logger(filename, logger_name, print_out, level, clear, format_string)
        filename (string): The file will be created relative to the calling location.
            '..' may be used within 'filename' to ascend the directory tree.
        logger_name (string): name of logger (associated with files and level)
        print_out (bool): whether to print entries as they're logged
        level (int): logger's level, e.g. logging.DEBUG
        clear (float or None): clears all but the last 'clear' seconds of logs.
                Default of None keeps all data.
        format_string (str): format string passed direct into logging.Formatter.
                NOTE: the clearing functions only support default format for now.

    .log(message, level) Saves data to the Logger's file
        message (any): information to save
        level (int): information's log level, default logging.DEBUG

    #TODO: maybe make subdirectory for each day of logs automatically?
    """

    locks = dict()

    def __init__(self, filename, logger_name='default',
                 print_out=False, level=logging.INFO, clear=None,
                 format_string='%(asctime)s::%(name)s::%(levelname)s:: %(message)s',
                 _is_recorder=False
                 ):
        
        self.print_out = print_out
        
        self.file = ensure_file(filename)
        
        if self.file.fullpath not in Logger.locks.keys():
            Logger.locks.update({self.file.fullpath:Lock()})
        Logger.locks.update({'print':Lock()})
        
        self.logger_name = logger_name
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(level)
        self.level = level
        
        if self.logger.hasHandlers():
            if not self.file.filename in [h.baseFilename for h in self.logger.handlers]:
                self.fh = logging.FileHandler(self.file.fullpath)
                self.fh.setFormatter(logging.Formatter(format_string))
                self.logger.addHandler(self.fh)
        else:
            self.fh = logging.FileHandler(self.file.fullpath)
            self.fh.setFormatter(logging.Formatter(format_string))
            self.logger.addHandler(self.fh)

        if clear is not None:
            self.clear_log(clear)

        if not _is_recorder:
            self.log('Log started at level {}:INFO={},DEBUG={}'.format(
                self.level, logging.INFO, logging.DEBUG),
                logging.INFO)
    
    def log(self, message, level=logging.DEBUG):
        with Logger.locks[self.file.fullpath]:
            self.logger.log(level, message)
        if self.print_out and level>=self.logger.level:
            with Logger.locks['print']:
                print('{}::{}'.format(self.logger_name,message))

    def clear_log(self, time_to_keep=0.0, timestamp_delim='::', timestamp_fmt='default'):
        import datetime
        if time_to_keep <= 0.0:
            with Logger.locks[self.file.fullpath]:
                with open(self.file.fullpath, 'w') as f:
                    f.close()
        else:
            with Logger.locks[self.file.fullpath]:
                with open(self.file.fullpath, 'r') as f:
                    lines = f.readlines()
                with open(self.file.fullpath, 'w') as f:
                    f.close()

                save = []
                keep = time() - time_to_keep  # go backwards in time
                if timestamp_fmt == 'default':
                    for line in lines:
                        timestamp = line.split(timestamp_delim)[0]
                        try:
                            t = datetime.datetime.strptime(timestamp, logging.Formatter.default_time_format+',%f')
                        except ValueError:
                            print('{}::Timestamp format not yet supported. This data will not be removed \'{}\''.\
                                  format(self.logger_name,line))
                            save.append(line)
                        else:
                            t = t.timestamp()
                            if t >= keep:
                                save.append(line)
                    with open(self.file.fullpath, 'w') as f:
                        f.writelines(save)

                else:
                    raise Exception('Deconstructing other time formats not yet implemented')


class Recorder(Logger):
    """class logs strictly data to a file, subclass of Logger.
        Written by Tim Olson - tim.lsn@gmail.com
    
    obj = Recorder(filename)
        filename (string): see Logger for more info
        
    .log(message) Saves data to the Logger's file if currently recording
        message (any): information to save

    .start_recording() record incoming data to the file
    .stop_recording() do not record data until recording is started again
    
    #TODO: maybe make subdirectory for each day of logs automatically?
    """

    i = 0  # for unique logger names in backend
    
    def __init__(self, filename):
        super().__init__(
            filename,
            level=logging.DEBUG,
            format_string='%(message)s',
            logger_name='Recorder {}{}{}'.format(Recorder.i,Recorder.i**2,Recorder.i*-1),
            _is_recorder=True
            )
        Recorder.i += 1

        self.fh.terminator = ''
        self.save = True

    def log(self, msg):
        if self.save:
            buf = ''
            for m in msg.items():
                buf += '{},{};'.format(m[0],m[1])
            super().log(buf+'\n', logging.INFO)

    def start_recording(self):
        self.save = True

    def stop_recording(self):
        self.save = False


class LogAndRecord():
    """intended as a superclass. Attaches a logger and/or recorder to a
    subclass for ease of use.
        Written by Tim Olson - tim.lsn@gmail.com

    Usage: make subclass, pass arguments to LogAndRecord, use .log(),
        .record(), .clear_log(), .start_recording(), .stop_recording

        Keyword arguments to LogAndRecord can be:
            record_file (filename string, see Logger): file to record data to
                when using .record(data). A Recorder object is created to
                handle the file.
            logger (Logger object): attach a Logger directly for use with
                .log(msg, level), and .clear_log(N)

    EXAMPLE SUBCLASS:
    class SubClass(LogAndRecord):
        def __init__(self, parameters,..., **logrecord):
            # init stuff
            LogRecord.__init__(self, **logrecord)
            # init more stuff
            self.log('Instance of SubClass created', logging.INFO)

        def log_and_record(self, data):
            self.log('data = '.format(data),level=10)
            self.record(data)

        def start_fresh(self, time_to_keep):
            self.clear_log(time_to_keep)
            self.start_recording()
    """

    def __init__(self, **kwargs):
        self.logger, self.recorder = None, None
        if 'logger' in kwargs.keys() and kwargs['logger'] is not None:
            self.logger = kwargs['logger']
            self.log = self.logger.log
            self.clear_log = self.logger.clear_log

        if 'record_file' in kwargs.keys() and kwargs['record_file'] is not None:
            self.recorder = Recorder(kwargs['record_file'])
            self.record = self.recorder.log
            self.log('Recording to {}'.format(kwargs['record_file']), logging.INFO)
            self.stop_recording = self.recorder.stop_recording
            self.start_recording = self.recorder.start_recording

    def log(self, *args, **kwargs):
        """Placeholder"""
        pass

    def record(self, *args, **kwargs):
        """Placeholder"""
        pass

    def clear_log(self, *args, **kwargs):
        """Placeholder"""
        pass

    def start_recording(self):
        """Placeholder"""
        pass

    def stop_recording(self):
        """Placeholder"""
        pass


__all__ = ['Logger', 'Recorder', 'LogAndRecord']
