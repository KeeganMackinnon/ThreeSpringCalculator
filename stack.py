# stack.py

from models import SpringStack, SpringResult, StackResult


def equivalent_series_rate(springs):
    return 1 / sum(1 / spring.rate for spring in springs)


def preload_from_turns(preload_turns, adjuster_pitch):
    """
    Converts preload adjuster turns into linear displacement.

    Example:
        4 turns * 0.050 in/turn = 0.200 in preload
    """
    return preload_turns * adjuster_pitch


def preload_force_from_displacement(preload_displacement, springs):
    """
    Converts preload displacement into preload force.

    Simple model:
        preload force = equivalent spring rate * preload displacement
    """
    k_eq = equivalent_series_rate(springs)
    return k_eq * preload_displacement


def calculate_stack(
    applied_force,
    stack: SpringStack,
    preload_turns=0.0,
    adjuster_pitch=0.0,
):
    springs = stack.springs()

    preload_displacement = preload_from_turns(
        preload_turns=preload_turns,
        adjuster_pitch=adjuster_pitch,
    )

    preload_force = preload_force_from_displacement(
        preload_displacement=preload_displacement,
        springs=springs,
    )

    total_force = applied_force + preload_force

    spring_results = []
    total_spring_compression = 0.0
    total_spring_length = 0.0

    for spring in springs:
        compression = total_force / spring.rate
        max_compression = spring.max_compression()

        stopped = False

        if max_compression is not None and compression >= max_compression:
            compression = max_compression
            stopped = True

        compressed_length = spring.free_length - compression

        spring_results.append(
            SpringResult(
                name=spring.name,
                rate=spring.rate,
                free_length=spring.free_length,
                compression=compression,
                compressed_length=compressed_length,
                max_compression=max_compression,
                stopped=stopped,
            )
        )

        total_spring_compression += compression
        total_spring_length += compressed_length

    total_coupler_length = stack.total_coupler_length()

    calculated_collar_length = total_spring_length + total_coupler_length

    if stack.measured_collar_length is not None:
        collar_length_error = stack.measured_collar_length - calculated_collar_length
    else:
        collar_length_error = None

    return StackResult(
        applied_force=applied_force,
        preload_turns=preload_turns,
        adjuster_pitch=adjuster_pitch,
        preload_displacement=preload_displacement,
        preload_force=preload_force,
        total_force=total_force,

        total_spring_compression=total_spring_compression,
        total_spring_length=total_spring_length,
        total_coupler_length=total_coupler_length,
        calculated_collar_length=calculated_collar_length,

        measured_collar_length=stack.measured_collar_length,
        collar_length_error=collar_length_error,

        spring_results=spring_results,
    )