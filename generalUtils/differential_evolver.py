from scipy.optimize._differentialevolution import DifferentialEvolutionSolver, np
from scipy.optimize.optimize import _status_message
from tqdm import tqdm
from .keyboard_detection import KeyStop, keyboard_detection
import os, sys, termios, select


class DESolver(DifferentialEvolutionSolver):
    __doc__ = str(DifferentialEvolutionSolver.__doc__) + \
    """
    Custom Properties:
    state - kwargs dict to resume with DESolver(func, **state)
    X - copy of population
    Y - copy of function results (ordered same as population)
    y - best result (lowest energy)
    """

    def __init__(self, func, bounds, args=(), p_bars=False, **kwargs):
        # store things needed to remake from a loaded file
        self.seed = kwargs.get('seed', None)
        self.workers = kwargs.get('workers', 1)
        self.mutation = tuple(kwargs.get('mutation', (0.5, 1)))
        self.p_bars = p_bars
        nrg = kwargs.pop('nrg', None)
        nfev = kwargs.pop('nfev', 0)
        kwargs.setdefault('polish', False)

        if p_bars is False:
            super().__init__(func, bounds, args, **kwargs)
            if nrg is not None:
                self.population_energies[:] = nrg[:]
            if nfev != 0:
                self._nfev = nfev
            self._inited = nfev >= self.num_population_members
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
        self._inited = nfev >= self.num_population_members

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

    @staticmethod
    def __fix_mutation(mutation):
        return tuple(mutation)

    @property
    def state(self):
        return dict(
            nfev=self._nfev,
            popsize=int(self.num_population_members/self.parameter_count),
            bounds=self.limits.T.tolist(),
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
            p_bars=self.p_bars,
            init=self.X.tolist(),
            nrg=self.population_energies.tolist()
        )

    @property
    def X(self):
        """The current population without internal scaling"""
        return self._scale_parameters(self.population)

    @property
    def Y(self):
        """The current population energies"""
        return self.population_energies.copy()

    @property
    def y(self):
        """The current best energy"""
        return self.population_energies[0]
