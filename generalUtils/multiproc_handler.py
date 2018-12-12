import multiprocessing as mp

# https://pymotw.com/2/multiprocessing/basics.html
from time import sleep
from .structset import StructSet
from .logger_recorder import LogAndRecord
import logging


class MultiProcHandler(LogAndRecord):
    '''class provides an interface for parallel processing for ease of use.
    Written by Tim Olson - tim.lsn@gmail.com
    
    obj = Multi_Proc(mgr, locks, logger)
        mgr = multiprocessing.Manager() object *CREATE ONLY ONE OF THESE*
            If None provided, one will be created
        locks (list): list of lock names for child processes to use
        logger (Logger object): optional keyword, Logger object
    '''

    def __init__(self, mgr=None, locks=['print'], **logrecord):
        """See Multi_Proc doc"""
        assert isinstance(locks, list), 'provide a list of lock names'
        
        import queue as q
        self.queue = q

        LogAndRecord.__init__(self, **logrecord)

        MultiProcHandler.mgr = mgr if mgr else mp.Manager()
        MultiProcHandler.procs = dict()
        MultiProcHandler.locks = dict()
        MultiProcHandler.log_q = mp.Queue()
        MultiProcHandler.print_q = mp.Queue()
        for k in set(locks):
            self.locks.update({k:self.mgr.Lock()})
        if 'print' not in self.locks: self.locks.update({'print':self.mgr.Lock()})
        
        # self.logger = logger
        # if self.logger is not None:
        #     self.log = self.logger.log
        self.log('Multi_Proc instance created', logging.INFO)
    
    def add_process(self, func):
        """Adds a function to Multi_Proc object and starts it as another process.
        If a process/function by the same name is running, logs it without starting duplicate.
        func = (function, daemon, args)
        func = (function, daemon)
        func = (function,)

        func is passed the locks, log queue, and print queue of the Multi_Proc object
            in a Struct as the first parameter.
        """
        assert isinstance(func, tuple), 'provide tuple'
        name = func[0].__name__ # function name is key in dictionaries
        
        # procs is not empty
        if bool(self.procs):
            # to_add is already in procs
            if name in self.procs.keys():
                # don't start another
                self.log('Process \'{}\' already running'.format(name), logging.INFO)
                return
        
        mpargs = StructSet(locks=self.locks, log_q=self.log_q, print_q=self.print_q)
        
        # if the function has an arguments dict
        if len(func)==3:
            self.procs.update(
                    {name:mp.Process(name=name, target=func[0], args=(mpargs, func[2]))}
                )
        # does not have arguments dict
        elif len(func)<3:
            self.procs.update(
                    {name:mp.Process(name=name, target=func[0], args=(mpargs,))}
                )
        # no arguments or daemon
        else:
            self.log('add_process(func) : func tuple not correct length')
            raise Exception('add_process(func) : func tuple not correct length')
        
        # store daemon setting
        self.procs[name].daemon = False if len(func)==1 else func[1]
        
        # begin the process
        self.procs[name].start()
        # log
        self.log('Process \'{name}\' at PID {PID} started{dae}'.format(
                name=name, PID=self.procs[name].pid,
                dae=(' as daemon' if self.procs[name].daemon else '')
                ),
            logging.INFO
        )

    def remove_inactive(self):
        '''Removes and logs ended processes from the Multi_Proc object's 'procs' dict.'''
        active = mp.active_children()
        inactive = [name for name in self.procs.keys() if self.procs[name] not in active]
        with self.locks['print']:
            for name in inactive:
                self.log('Process \'{name}\' at PID {PID} ended'.format(
                    name=name, PID=self.procs[name].pid),
                    logging.INFO
                )
                self.procs.pop(name)
        
        del active, inactive
    
    def loop(self, ignore=list()):
        '''Returns status bool = False if no more processes are running, True otherwise.
        Any process name in ignore[] will be irrelevant to the function's logic.
        ignore = [name1, name2, ...]'''
        assert type(ignore)== list, 'provide a list of process name strings to treat as daemons'
        
        try: record = self.log_q.get(False)
        except self.queue.Empty: pass
        else: self.log(record)
        
        try: p = self.print_q.get(False)
        except self.queue.Empty: pass
        else:
            with self.locks['print']:
                print(p)
        
        self.remove_inactive() # remove finished
        _procs = dict(self.procs) # make a new dict to filter
        
        # filter out daemons
        for k, v in self.procs.items():
            if v.daemon is True:
                try:
                    _procs.pop(k)
                except KeyError:
                    pass
        
        # filter out ignored
        if ignore:
            for k in ignore:
                try:
                    _procs.pop(k)
                except KeyError:
                    pass
        
        # return whether dict is empty or not
        return bool(_procs)
    
    def cleanup(self, wait_for_daemons=False):
        '''Terminate()s any remaining processes, with option to wait for daemons 
        to finish or terminate() them immediately.'''
        assert type(wait_for_daemons)== type(True), 'wait_for_daemons must be True/False'
        self.log(
            'Cleaning up processes{}'.format(', waiting for daemons' if wait_for_daemons else ''),
            logging.INFO
            )
        
        # end process, regardless of daemon
        if not wait_for_daemons:
            self.log(
                'Terminating ALL processes',
                logging.DEBUG
            )
            for k, v in self.procs.items():
                v.terminate()
        
        self.log(
            'Joining processes',
            logging.DEBUG
            )
        # wait for all but daemons to end
        for k, v in self.procs.items():
            v.join()
        
        # allow for logging of process ends
        sleep(0.3)
        self.remove_inactive()
        
        self.log('Shutting down Manager',logging.DEBUG)
        self.mgr.shutdown()
        self.log('Manager shutdown',logging.DEBUG)
    

__all__ = ['MultiProcHandler']
