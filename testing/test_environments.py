import matplotlib.pyplot as plt
import pytest
import torch

from gfn.envs import HyperGrid
from gfn.envs.env import NonValidActionsError
from gfn.envs.utils import build_grid, get_flat_grid


def test_hypergrid():
    env = HyperGrid(ndim=2, height=3)
    print(env)

    print("\nInstantiating a linear batch of initial states")
    states = env.reset(batch_shape=3)
    print("States:", states)

    print("\nTrying the step function starting from 3 instances of s_0")
    actions = torch.tensor([0, 1, 2], dtype=torch.long)
    states = env.step(states, actions)
    print("After one step:", states)
    actions = torch.tensor([2, 0, 1], dtype=torch.long)
    states = env.step(states, actions)
    print("After two steps:", states)
    actions = torch.tensor([2, 0, 1], dtype=torch.long)
    states = env.step(states, actions)
    print("After three steps:", states)
    try:
        actions = torch.tensor([2, 0, 1], dtype=torch.long)
        states = env.step(states, actions)
    except NonValidActionsError:
        print("NonValidActionsError raised as expected because of invalid actions")
    print(states)
    print("Final rewards:", env.reward(states))

    print("\nTrying the backward step function starting from a batch of random states")

    print("\nInstantiating a two-dimensional batch of random states")
    states = env.reset(batch_shape=(2, 3), random_init=True)
    print("States:", states)
    while not all(states.is_initial_state.view(-1)):
        actions = torch.randint(0, env.n_actions - 1, (2, 3), dtype=torch.long)
        print("Actions: ", actions)
        try:
            states = env.backward_step(states, actions)
            print("States:", states)
        except NonValidActionsError:
            print("NonValidActionsError raised as expected because of invalid actions")


@pytest.mark.parametrize("ndim", [2, 3, 4])
def test_states_get_and_set(ndim: int):
    env = HyperGrid(ndim=ndim, height=8)

    states = env.reset(batch_shape=(2, 3), random_init=True)
    print("States:", states)
    print("\nTesting subscripting with boolean tensors")

    selections = torch.randint(0, 2, (2, 3), dtype=torch.bool)
    print("Selections:", selections)
    print("States[selections]:", states[selections])
    selections = torch.randint(0, 2, (2,), dtype=torch.bool)
    print("Selections:", selections)
    print("States[selections]:", states[selections])

    states = env.reset(batch_shape=(2, 3))
    states_2 = env.reset(batch_shape=1, random_init=True)
    states[0, 2] = states_2
    print("States:", states)


def test_get_flat_grid(plot=False):
    env = HyperGrid(height=4, ndim=3)
    grid = get_flat_grid(env)
    print("Shape of the grid: ", grid.batch_shape, grid.state_shape)
    print(grid)
    print("All rewards: ", env.reward(grid))

    env = HyperGrid(height=8, ndim=2)
    grid = build_grid(env)
    flat_grid = get_flat_grid(env)
    print("Shape of the grid: ", grid.batch_shape, grid.state_shape)
    rewards = env.reward(grid)

    Z = rewards.sum()

    if Z != env.reward(flat_grid).sum():
        raise ValueError("Something is wrong")

    if plot:
        plt.imshow(rewards)
        plt.colorbar()
        plt.show()

    print(env.get_states_indices(grid))
    print(env.get_states_indices(flat_grid))

    print(env.reward(grid))
    print(env.reward(flat_grid))
