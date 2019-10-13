import os
import numpy as np
import logging
from scipy.optimize._differentialevolution import DifferentialEvolutionSolver


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

    def __init__(self, func, bounds, *args, **kwargs):
        # store things needed to remake from a loaded file
        self.seed = kwargs.get('seed', None)
        self.workers = kwargs.get('workers', 1)
        self.mutation = kwargs.get('mutation', (0.5, 1))

        super().__init__(func, bounds, *args, **kwargs)

    @classmethod
    def from_state(cls, state, func, args=(), callback=None):
        """

        :param state:
        :param func:
        :param args:
        :param callback:
        :return:
        """
        obj = cls(func, args=args, init=state['pop'], callback=callback, **state['options'])

        # Update from file
        obj.population_energies[:] = state['nrg'][:]
        obj._nfev = state['nfev']
        return obj

    @classmethod
    def from_json(cls, state, func, args=(), callback=None):
        # Fix json formatting
        state['options']['mutation'] = cls.__fix_mutation(state['options']['mutation'])

        return cls.from_state(state, func, args, callback)

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
                workers=self.workers
            ),
            pop=self.X.tolist(), nrg=self.population_energies.tolist()
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
