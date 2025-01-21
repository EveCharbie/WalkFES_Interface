
import numpy as np

from bioptim import (
    BiorbdModel,
    OptimalControlProgram,
    DynamicsList,
    DynamicsFcn,
    BoundsList,
    InitialGuessList,
    ObjectiveList,
    ObjectiveFcn,
    InterpolationType,
    Solver,
    Node,
)

from experimental_data import ExperimentalData


def prepare_ocp(biorbd_model_path: str):
    """
    Let's say swing phase only for now
    """

    # Declaration of generic elements
    n_shooting = [40]
    phase_time = [1.0]

    bio_model = BiorbdModel(biorbd_model_path)

    # Declaration of the objectives
    objective_functions = ObjectiveList()
    objective_functions.add(
        objective=ObjectiveFcn.Lagrange.MINIMIZE_CONTROL,
        key="tau_joints",
        weight=1.0,
    )
    objective_functions.add(
        objective=ObjectiveFcn.Mayer.MINIMIZE_TIME,
        min_bound=0.5,
        max_bound=1.5,
        node=Node.END,
        weight=-0.001,
    )

    # Declaration of the dynamics function used during integration
    dynamics = DynamicsList()
    dynamics.add(DynamicsFcn.TORQUE_DRIVEN_FREE_FLOATING_BASE)

    # Declaration of optimization variables bounds and initial guesses
    # Path constraint
    x_bounds = BoundsList()
    x_initial_guesses = InitialGuessList()

    u_bounds = BoundsList()
    u_initial_guesses = InitialGuessList()

    x_bounds.add(
        "q_roots",
        min_bound=[
            [0.0, -1.0, -0.1],
            [0.0, -1.0, -0.1],
            [0.0, -0.1, -0.1],
            [0.0, -0.1, 2 * np.pi - 0.1],
            [0.0, -np.pi / 4, -np.pi / 4],
            [0.0, -0.1, -0.1],
        ],
        max_bound=[
            [0.0, 1.0, 0.1],
            [0.0, 1.0, 0.1],
            [0.0, 10.0, 0.1],
            [0.0, 2 * np.pi + 0.1, 2 * np.pi + 0.1],
            [0.0, np.pi / 4, np.pi / 4],
            [0.0, np.pi + 0.1, np.pi + 0.1],
        ],
    )
    x_bounds.add(
        "q_joints",
        min_bound=[
            [2.9, -0.05, -0.05],
            [-2.9, -3.0, -3.0],
        ],
        max_bound=[
            [2.9, 3.0, 3.0],
            [-2.9, 0.05, 0.05],
        ],
    )

    x_bounds.add(
        "qdot_roots",
        min_bound=[
            [-0.5, -10.0, -10.0],
            [-0.5, -10.0, -10.0],
            [5.0, -100.0, -100.0],
            [0.5, 0.5, 0.5],
            [0.0, -100.0, -100.0],
            [0.0, -100.0, -100.0],
        ],
        max_bound=[
            [0.5, 10.0, 10.0],
            [0.5, 10.0, 10.0],
            [10.0, 100.0, 100.0],
            [20.0, 20.0, 20.0],
            [-0.0, 100.0, 100.0],
            [-0.0, 100.0, 100.0],
        ],
    )
    x_bounds.add(
        "qdot_joints",
        min_bound=[
            [0.0, -100.0, -100.0],
            [0.0, -100.0, -100.0],
        ],
        max_bound=[
            [-0.0, 100.0, 100.0],
            [-0.0, 100.0, 100.0],
        ],
    )

    x_initial_guesses.add(
        "q_roots",
        initial_guess=[
            [0.0, 0.0],
            [0.0, 0.0],
            [0.0, 0.0],
            [0.0, 2 * np.pi],
            [0.0, 0.0],
            [0.0, np.pi],
        ],
        interpolation=InterpolationType.LINEAR,
    )
    x_initial_guesses.add(
        "q_joints",
        initial_guess=[
            [2.9, 0.0],
            [-2.9, 0.0],
        ],
        interpolation=InterpolationType.LINEAR,
    )

    x_initial_guesses.add(
        "qdot_roots",
        initial_guess=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        interpolation=InterpolationType.CONSTANT,
    )
    x_initial_guesses.add(
        "qdot_joints",
        initial_guess=[0.0, 0.0],
        interpolation=InterpolationType.CONSTANT,
    )

    u_bounds.add("tau_joints", min_bound=[-100, -100], max_bound=[100, 100], interpolation=InterpolationType.CONSTANT)

    return OptimalControlProgram(
        bio_model=bio_model,
        n_shooting=n_shooting,
        phase_time=phase_time,
        dynamics=dynamics,
        x_bounds=x_bounds,
        u_bounds=u_bounds,
        x_init=x_initial_guesses,
        u_init=u_initial_guesses,
        objective_functions=objective_functions,
        use_sx=False,
    )


if __name__ == "__main__":

    biorbd_model_path = "data/VIF_04_tau.bioMod"
    file_path = "data/VIF_04_Cond0007_processed6.c3d"

    exp_data = ExperimentalData(file_path=file_path, biorbd_model_path=biorbd_model_path)
    exp_data.find_event_timestamps()

    ocp = prepare_ocp(biorbd_model_path=biorbd_model_path)

    # --- Solve the ocp --- #
    solver = Solver.IPOPT(show_online_optim=True)
    sol = ocp.solve(solver=solver)

    # --- Show results --- #
    # sol.graphs()
    sol.animate()
