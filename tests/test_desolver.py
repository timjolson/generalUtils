import pytest
import os, sys, logging, json
from scipy.optimize import rosen
import numpy as np
import time
from tqdm import tqdm

from generalUtils.differential_evolver import DESolver

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


def clear_file(filename):
    try:
        os.remove(filename)
    except FileNotFoundError:
        pass


def test_state():
    # make state
    des = DESolver(rosen, bounds=[(0, 2), (0, 2), (0, 2), (0, 2), (0, 2)])
    backup = des.state.copy()

    # make from state
    from_state = DESolver.from_state(backup, rosen)

    # verify matching state (state includes population, energies, config options, etc.)
    assert des.state == from_state.state


def test_from_state():
    filename = "test_from_test"
    clear_file(filename)

    # make file
    des = DESolver(rosen, bounds=[(0, 2), (0, 2), (0, 2), (0, 2), (0, 2)],
                   popsize=12)
    json.dump(des.state, open(filename, 'w'), indent=4)

    # make from file
    from_state = DESolver.from_state(json.load(open(filename, 'r')), rosen)

    # verify matching state (state includes population, energies, config options, etc.)
    assert des.state == from_state.state

    # This fails regularly, appears to be low level, inconsequential math error
    # Any differences between arrays should be extremely small (float error, etc.)
    # assert (des.population == from_state.population).all()
    # assert (np.abs(des.population - from_state.population) < 1e-16).all()
    assert np.allclose(des.population, from_state.population)
    logging.debug(f"diff\n{des.population - from_state.population}")

    res = from_state.solve()
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
    des = DESolver.from_state(json.load(open(filename, 'r')), rosen)

    # iterate some
    for i in range(iters):
        x, y = next(des)
        logging.debug(f"nfev:{des._nfev}  iteration/generation: {i} \tx:{x}\ty:{y}")
    assert des._nfev == iters * popsize * des.parameter_count + 1
    des_state_backup = des.state

    # reload file
    del des
    des = DESolver.from_state(des_state_backup, rosen)
    assert des._nfev == iters * des.num_population_members + 1
    # solve
    assert (des.solve().x == 1.0).all()

    # cleanup
    clear_file(filename)


def test_tqdm():
    des = DESolver(lambda x: [rosen(x), time.sleep(.05)][0],
                   bounds=[(0, 2), (0, 2), (0, 2), (0, 2), (0, 2)],
                   popsize=2, maxiter=2, maxfun=30, p_bars=True)
    des.solve()
    assert des.pbar_feval.n == 30
    assert des.pbar_gen_mutations.n == 0
    assert np.isclose(des.pbar_gens.n, 2.0)

    des = DESolver(lambda x: [rosen(x), time.sleep(.07)][0],
                   bounds=[(0, 2), (0, 2), (0, 2), (0, 2), (0, 2)],
                   popsize=2, maxiter=1, maxfun=30, p_bars=True)
    des.solve()
    assert des.pbar_feval.n == 20
    assert des.pbar_gen_mutations.n == 0
    assert np.isclose(des.pbar_gens.n, 1.0)

    des = DESolver(lambda x: [rosen(x), time.sleep(.07)][0],
                   bounds=[(0, 2), (0, 2), (0, 2), (0, 2), (0, 2)],
                   popsize=2, maxiter=2, p_bars=True)
    des.solve()
    assert des.pbar_feval.n == 30
    assert des.pbar_gen_mutations.n == 0
    assert np.isclose(des.pbar_gens.n, 2.0)

    des = DESolver(lambda x: [rosen(x), time.sleep(.07)][0],
                   bounds=[(0, 2), (0, 2), (0, 2), (0, 2), (0, 2)],
                   popsize=2, maxfun=23, p_bars=True)
    des.solve()
    assert des.pbar_feval.n == 23
    assert des.pbar_gen_mutations.n == 3
    assert np.isclose(des.pbar_gens.n, 1.0 + 3 / 10)

    des = DESolver(lambda x: [rosen(x), time.sleep(.07)][0],
                   bounds=[(0, 2), (0, 2), (0, 2), (0, 2), (0, 2)],
                   popsize=2, maxiter=1, p_bars=True)
    des.solve()
    assert des.pbar_feval.n == 20
    assert des.pbar_gen_mutations.n == 0
    assert np.isclose(des.pbar_gens.n, 1.0)


def test_tqdm_resume():
    des = DESolver(lambda x: [rosen(x), time.sleep(.07)][0],
                   bounds=[(0, 2), (0, 2), (0, 2), (0, 2), (0, 2)],
                   popsize=2, maxiter=1, p_bars=True)
    des.solve()
    assert des.pbar_feval.n == 20
    assert des.pbar_gen_mutations.n == 0
    assert np.isclose(des.pbar_gens.n, 1.0)

    des = DESolver.from_state(des.state, rosen)
    assert des._nfev == 20
    assert des.pbar_feval.n == 20
    assert des.pbar_gen_mutations.n == 0
    assert des.pbar_gens.n == 1.0

    x, y = next(des)
    assert des._nfev == 30
    assert des.pbar_feval.n == 30
    assert des.pbar_gen_mutations.n == 0
    assert np.isclose(des.pbar_gens.n, 2.0)


def test_tqdm_resume_interrupted():
    des = DESolver(lambda x: [rosen(x), time.sleep(.07)][0],
                   bounds=[(0, 2), (0, 2), (0, 2), (0, 2), (0, 2)],
                   popsize=2, maxfun=23, p_bars=True)
    des.solve()
    assert des.pbar_feval.n == 23
    assert des.pbar_gen_mutations.n == 3
    assert np.isclose(des.pbar_gens.n, 1.0 + 3 / 10)

    print('from_state')
    state = des.state.copy()
    state['options']['maxfun'] = 40
    des = DESolver.from_state(state, rosen)
    assert des._nfev == 23
    assert des.pbar_feval.n == 23
    assert des.pbar_gen_mutations.n == 3
    assert np.isclose(des.pbar_gens.n, 1.0 + 3 / 10)

    x, y = next(des)
    assert des._nfev == 33
    assert des.pbar_feval.n == 33
    assert des.pbar_gen_mutations.n == 3
    assert np.isclose(des.pbar_gens.n, 2.0+3/10)

    with pytest.raises(StopIteration):
        x, y = next(des)
    assert des._nfev == 41
    assert des.pbar_feval.n == 41
    assert des.pbar_gen_mutations.n == 1
    assert np.isclose(des.pbar_gens.n, 3.0+1/10)
