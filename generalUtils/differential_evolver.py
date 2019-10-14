from scipy.optimize._differentialevolution import DifferentialEvolutionSolver, np
from scipy.optimize.optimize import _status_message
from tqdm import tqdm
import os, sys, termios, select


class DESolver(DifferentialEvolutionSolver):
    __doc__ = str(DifferentialEvolutionSolver.__doc__) + \
    """
    Custom Methods:
    .from_state(state_object, func, args, callback)
        returns DESolver object created from dict `state_object`
    .from_json(json_dict_state, func, args, callback)
        returns DESolver object created from a json structure
    
    Custom Properties:
    X - copy of population
    Y - copy of function results (ordered same as population)
    y - best result (lowest energy)
    """

    def __init__(self, func, bounds, args=(), p_bars=False, **kwargs):
        # store things needed to remake from a loaded file
        self.seed = kwargs.get('seed', None)
        self.workers = kwargs.get('workers', 1)
        self.mutation = kwargs.get('mutation', (0.5, 1))
        self.p_bars = p_bars
        self._inited = kwargs.pop('_inited', False)
        nrg = kwargs.pop('nrg', None)
        nfev = kwargs.pop('nfev', 0)
        kwargs.setdefault('polish', False)

        if p_bars is False:
            super().__init__(func, bounds, args, **kwargs)
            if nrg is not None:
                self.population_energies[:] = nrg[:]
            if nfev != 0:
                self._nfev = nfev
            return

        # wrap func with pbar updates
        def _func(parameters):
            rv = func(parameters)
            if self._inited is False:  # nfev does not get updated by initial population filling
                self._nfev += 1
            if self.p_bars is True:
                self.pbar_feval.update()
                self.pbar_gen_mutations.update()
                self.pbar_gens.update(1 / self.pbar_gen_mutations.total)
                if self.pbar_gen_mutations.n == self.pbar_gen_mutations.total:
                    self.pbar_gen_mutations.reset(self.num_population_members)
            return rv

        super().__init__(_func, bounds, *args, **kwargs)

        if nrg is not None:
            self.population_energies[:] = nrg[:]
        if nfev != 0:
            self._nfev = nfev

        if not np.isfinite(self.maxfun):  # no max fun
            if not np.isfinite(self.maxiter):  # no max fun, no max iter/gen
                maxfeval = np.inf
            else:  # no max fun, max iter/gen
                maxfeval = (self.maxiter + 1) * self.num_population_members
        else:  # max fun
            if not np.isfinite(self.maxiter):  # max fun, no max iter/gen
                maxfeval = self.maxfun
            else:  # max fun, max iter/gen
                maxfeval = min(
                    (self.maxiter + 1) * self.num_population_members,  # dictated by generations
                    self.maxfun  # dictated by maxfun
                )

        mut_initial = (self._nfev % self.num_population_members)
        if self._nfev >= self.num_population_members*2:  # first gen complete
            gen_initial = (self._nfev - self.num_population_members) / self.num_population_members
            mut_total = self.num_population_members
        # elif self._nfev >= self.num_population_members:  # initial pop calculated
        else:
            gen_initial = self._nfev / (self.num_population_members * 2)
            mut_total = self.num_population_members * 2

        self.pbar_feval = tqdm(
            initial=self._nfev, total=maxfeval,
            leave=True, ncols=80, desc='FuncEval',
            bar_format='{desc}: {percentage:.2f}%|{bar}| {n}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}{postfix}]')
        self.pbar_gens = tqdm(
            initial=gen_initial, total=self.maxiter,
            leave=True, ncols=80, desc='Generation',
            bar_format='{desc}: {percentage:.2f}%|{bar}| {n:.2f}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}{postfix}]')
        self.pbar_gen_mutations = tqdm(
            initial=mut_initial, total=mut_total,
            leave=True, ncols=80, desc='Mutation',
            bar_format='{desc}: {percentage:.2f}%|{bar}| {n}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}{postfix}]')

    def _calculate_population_energies(self, population):
        rv = super()._calculate_population_energies(population)
        if self._inited is False:
            self._nfev -= self.num_population_members - 1
            self._inited = True
        return rv

    def solve(self):
        try:
            res = super().solve()
        except KeyStop as e:
            self._nfev -= 1
            raise
        else:
            if res.message == _status_message['maxiter']:
                self._nfev -= 1
            elif res.message == _status_message['maxfev']:
                self._nfev -= 1
            elif res.message == _status_message['success']:
                self._nfev -= 1
        if self.p_bars:
            self.pbar_feval.close()
            self.pbar_gens.close()
            self.pbar_gen_mutations.close()
        return res

    @classmethod
    def from_state(cls, state, func, args=(), callback=None):
        state['options']['mutation'] = cls.__fix_mutation(state['options']['mutation'])
        obj = cls(func, args=args, init=state['pop'].copy(),
                  callback=callback, _inited=state['_inited'],
                  nrg=state['nrg'][:], nfev=state['nfev'],
                  **state['options'])

        return obj

    @staticmethod
    def __fix_bounds(bounds):
        return [(bounds[0][i], bounds[1][i]) for i in range(len(bounds[0]))]

    @staticmethod
    def __fix_mutation(mutation):
        if isinstance(mutation, list):
            return tuple(mutation)
        else:
            return mutation

    @property
    def state(self):
        return dict(
            nfev=self._nfev, best_x=self.x.tolist(), best_y=self.y,
            options=dict(
                popsize=self.num_population_members,
                bounds=self.__fix_bounds(self.limits),
                maxiter=self.maxiter,
                maxfun=self.maxfun,
                mutation=self.mutation,
                recombination=self.cross_over_probability,
                tol=self.tol, atol=self.atol,
                strategy=self.strategy,
                seed=self.seed,
                polish=self.polish,
                disp=self.disp,
                updating=self._updating,
                workers=self.workers,
                p_bars=self.p_bars
            ),
            pop=self.X.tolist(),
            nrg=self.population_energies.tolist(),
            _inited=self._inited
        )

    @property
    def X(self):
        """
        The current population without internal scaling
        """
        return self._scale_parameters(self.population).copy()

    @property
    def Y(self):
        """
        The current population energies
        """
        return self.population_energies.copy()

    @property
    def y(self):
        """
        The current best energy
        """
        return self.population_energies[0]


class KeyStop(Exception):
    pass


class keyboard_detection:
    """
    Use in a with statement to enable the appropriate terminal mode to detect keyboard presses
    without blocking for input.  Used this way, the with statement puts a boolean detection
    function in the target variable.  The resulting function can be called any number of times
    until a keypress is detected.  Sample code:

    with keyboard_detection() as key_pressed:
        while not key_pressed():
            sys.stdout.write('.')
            sys.stdout.flush()
            sleep(0.5)
    print 'done'

    Upon exiting the with code block, the terminal is reverted to its calling (normal) state.
    The sys.stdout.flush() is important when in the keyboard detection mode; otherwise, text
    output won't be seen.
    """

    def __enter__(self):
        # save the terminal settings
        self.fd = sys.stdin.fileno()
        self.new_term = termios.tcgetattr(self.fd)
        self.old_term = termios.tcgetattr(self.fd)

        # new terminal setting unbuffered
        self.new_term[3] = (self.new_term[3] & ~termios.ICANON & ~termios.ECHO)

        # switch to unbuffered terminal
        termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.new_term)

        return self.query_keyboard

    def __exit__(self, type, value, traceback):
        # swith to normal terminal
        termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.old_term)

    def query_keyboard(self, keys=list((b'q', b'\x1b'))):
        dr, dw, de = select([sys.stdin], [], [], 0)
        key = None
        if dr:
            key = os.read(sys.stdin.fileno(), 1)
        return key in keys
