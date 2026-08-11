"""Small helpers for absolute garment measurements.

The style configuration remains normalized; these optional blocks only replace
the body-relative size inputs when a caller supplies measured dimensions.
"""
from copy import deepcopy


def block(design, name):
    value = design.get(name)
    return value if isinstance(value, dict) else None


def value(design, name, key, default=None):
    values = block(design, name)
    if values is None or key not in values:
        return default
    raw = values[key]
    return float(raw.get('v', raw) if isinstance(raw, dict) else raw)


def with_lower_measurements(body, design, name):
    """Copy ``body`` with measured waist/hip circumferences overlaid.

    Front/back proportions are preserved because the flat measurement only
    gives a complete circumference, while existing panels need both halves.
    """
    values = block(design, name)
    if values is None:
        return body
    result = deepcopy(body)
    for total_key, back_key in (
        ('waist', 'waist_back_width'),
        ('hips', 'hip_back_width'),
    ):
        if total_key not in values:
            continue
        raw = values[total_key]
        total = float(raw.get('v', raw) if isinstance(raw, dict) else raw)
        old_total = float(body[total_key])
        back_fraction = float(body[back_key]) / old_total
        result.params[total_key] = total
        result.params[back_key] = total * back_fraction
    return result


def set_total(body, total_key, back_key, total):
    """Set a complete circumference while retaining its front/back split."""
    fraction = float(body[back_key]) / float(body[total_key])
    body.params[total_key] = float(total)
    body.params[back_key] = float(total) * fraction
    return body
