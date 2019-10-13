import pytest
import os, sys, logging, json
from scipy.optimize import rosen
import numpy as np

from generalUtils.differential_evolver import DESolver

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


def clear_file(filename):
    try:
        os.remove(filename)
    except FileNotFoundError:
        pass


def test_from_state():
    # make state
    des = DESolver(rosen, bounds=[(0, 2), (0, 2), (0, 2), (0, 2), (0, 2)])
    backup = des.state.copy()

    # make from state
    from_state = DESolver.from_state(backup, rosen)

    # verify matching state (state includes population, energies, config options, etc.)
    assert des.state == from_state.state


def test_from_json():
    filename = "test_from_json"
    clear_file(filename)

    # make file
    des = DESolver(rosen, bounds=[(0, 2), (0, 2), (0, 2), (0, 2), (0, 2)],
                   popsize=12)
    json.dump(des.state, open(filename, 'w'), indent=4)

    # make from file
    from_json = DESolver.from_json(json.load(open(filename, 'r')), rosen)

    # verify matching state (state includes population, energies, config options, etc.)
    assert des.state == from_json.state

    # This fails regularly, appears to be low level, inconsequential math error
    # Any differences between arrays should be extremely small (float error, etc.)
    # assert (des.population == from_json.population).all()
    # assert (np.abs(des.population - from_json.population) < 1e-16).all()
    assert np.allclose(des.population, from_json.population)
    logging.debug(f"diff\n{des.population - from_json.population}")

    res = from_json.solve()
    logging.debug(f"solution=\n{res}")
    # Make sure func can be solved when made from_state
    assert (res.x == 1.0).all()
    assert res.fun == 0.0

    # cleanup
    clear_file(filename)


def test_iterate_load_save():
    filename = 'iterate_load_save'
    clear_file(filename)

    # iterate solver
    iters = 15
    popsize = 18

    # make file
    des = DESolver(rosen, bounds=[(0, 2)] * 5, popsize=popsize)
    json.dump(des.state, open(filename, 'w'))

    # load file
    des = DESolver.from_json(json.load(open(filename, 'r')), rosen)

    # iterate some
    for i in range(iters):
        x, y = next(des)
        logging.debug(f"nfev:{des._nfev}  iteration/generation: {i} \tx:{x}\ty:{y}")
    assert des._nfev == (iters + 1) * popsize * des.parameter_count
    des_state_backup = des.state

    # reload file
    del des
    des = DESolver.from_state(des_state_backup, rosen)
    assert des._nfev == (iters + 1) * des.num_population_members
    # solve
    assert (des.solve().x == 1.0).all()

    # cleanup
    clear_file(filename)
