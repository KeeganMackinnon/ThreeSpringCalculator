from spring import Spring


def equivalent_series_rate(springs):
    return 1 / sum(1 / spring.rate for spring in springs)


def preload_from_turns(preload_turns, adjuster_pitch):
    """
    Converts preload adjuster turns into linear preload displacement.

    preload_turns: number of turns on the preload collar
    adjuster_pitch: linear movement per turn

    Example:
        4 turns * 0.050 in/turn = 0.200 in preload
    """
    return preload_turns * adjuster_pitch


def preload_force_from_displacement(preload_displacement, springs):
    """
    Converts stack preload displacement into preload force.

    For springs in series:
        F_preload = k_eq * x_preload
    """
    k_eq = equivalent_series_rate(springs)
    return k_eq * preload_displacement


def basic_stack_calculation(
    force,
    springs,
    preload_turns=0.0,
    adjuster_pitch=0.0
):
    results = []
    total_compression = 0
    total_length = 0

    preload_displacement = preload_from_turns(
        preload_turns,
        adjuster_pitch
    )

    preload_force = preload_force_from_displacement(
        preload_displacement,
        springs
    )

    total_force = force + preload_force

    for spring in springs:
        compression = total_force / spring.rate

        if spring.max_compression is not None:
            compression = min(compression, spring.max_compression)

        compressed_length = spring.free_length - compression

        results.append({
            "name": spring.name,
            "compression": compression,
            "compressed_length": compressed_length,
            "stopped": spring.max_compression is not None and compression >= spring.max_compression
        })

        total_compression += compression
        total_length += compressed_length

    return {
        "applied_force": force,
        "preload_turns": preload_turns,
        "adjuster_pitch": adjuster_pitch,
        "preload_displacement": preload_displacement,
        "preload_force": preload_force,
        "total_force": total_force,
        "spring_results": results,
        "total_compression": total_compression,
        "total_length": total_length
    }