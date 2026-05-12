from stack import basic_stack_calculation


def generate_force_curve(
    springs,
    max_force,
    step,
    preload_turns=0.0,
    adjuster_pitch=0.0
):
    forces = []
    stack_lengths = []
    total_compressions = []

    force = 0.0

    while force <= max_force:
        result = basic_stack_calculation(
            force=force,
            springs=springs,
            preload_turns=preload_turns,
            adjuster_pitch=adjuster_pitch
        )

        forces.append(force)
        stack_lengths.append(result["total_length"])
        total_compressions.append(result["total_compression"])

        force += step

    return {
        "forces": forces,
        "stack_lengths": stack_lengths,
        "total_compressions": total_compressions
    }