# plotting.py

from stack import calculate_stack


def generate_force_curve(
    stack,
    max_force,
    step,
    preload_turns=0.0,
    adjuster_pitch=0.0,
):
    forces = []
    collar_lengths = []
    spring_compressions = []

    force = 0.0

    while force <= max_force:
        result = calculate_stack(
            applied_force=force,
            stack=stack,
            preload_turns=preload_turns,
            adjuster_pitch=adjuster_pitch,
        )

        forces.append(force)
        collar_lengths.append(result.calculated_collar_length)
        spring_compressions.append(result.total_spring_compression)

        force += step

    return {
        "forces": forces,
        "collar_lengths": collar_lengths,
        "spring_compressions": spring_compressions,
    }


def draw_force_curve(
    figure,
    canvas,
    stack,
    selected_load,
    preload_turns=0.0,
    adjuster_pitch=0.0,
    comparison_stacks=None,
):
    if comparison_stacks is None:
        comparison_stacks = {}

    max_force = max(selected_load * 1.5, 500)
    step = max_force / 100

    figure.clear()
    ax = figure.add_subplot(111)

    # Current config
    current_curve = generate_force_curve(
        stack=stack,
        max_force=max_force,
        step=step,
        preload_turns=preload_turns,
        adjuster_pitch=adjuster_pitch,
    )

    ax.plot(
        current_curve["collar_lengths"],
        current_curve["forces"],
        linewidth=2,
        label="Current",
    )

    selected_result = calculate_stack(
        applied_force=selected_load,
        stack=stack,
        preload_turns=preload_turns,
        adjuster_pitch=adjuster_pitch,
    )

    ax.scatter(
        [selected_result.calculated_collar_length],
        [selected_load],
        s=60,
    )

    ax.annotate(
        f"{selected_load:.1f} lb\n{selected_result.calculated_collar_length:.3f} in",
        xy=(selected_result.calculated_collar_length, selected_load),
        xytext=(10, 10),
        textcoords="offset points",
    )

    # Saved comparison configs
    for name, comparison_stack in comparison_stacks.items():
        curve = generate_force_curve(
            stack=comparison_stack,
            max_force=max_force,
            step=step,
            preload_turns=preload_turns,
            adjuster_pitch=adjuster_pitch,
        )

        ax.plot(
            curve["collar_lengths"],
            curve["forces"],
            linewidth=1.5,
            label=name,
        )

    ax.set_xlabel("Calculated Collar-to-Collar Length [in]")
    ax.set_ylabel("Applied Force [lb]")
    ax.set_title("Spring Stack Collar Length vs Force")
    ax.grid(True)
    ax.invert_xaxis()
    ax.legend()

    canvas.draw()