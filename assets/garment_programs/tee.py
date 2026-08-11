""" Panels for a straight upper garment (T-shirt)
    Note that the code is very similar to Bodice. 
"""
import numpy as np
import pygarment as pyg

from assets.garment_programs.base_classes import BaseBodicePanel


def _measurement_value(design, key):
    value = design['measurement_shirt'][key]
    return float(value['v'] if isinstance(value, dict) else value)


def _measurement_widths(body, design):
    """Return front/back half-panel widths at the hem and upper torso."""
    front_bottom = _measurement_value(design, 'hem_width') / 2
    front_body = body['waist'] - body['waist_back_width']
    back_bottom = front_bottom * body['waist_back_width'] / front_body

    # GarmentIQ back width is sampled at 95% panel height and chest at 70%.
    back_top = (
        _measurement_value(design, 'back_width') / 2
        - 0.05 * back_bottom
    ) / 0.95
    front_top = (
        _measurement_value(design, 'chest')
        - 0.3 * (front_bottom + back_bottom)
    ) / 0.7 - back_top
    if min(front_top, back_top, front_bottom, back_bottom) <= 0:
        raise ValueError('Measured Shirt dimensions produce a non-positive panel width')
    return front_bottom, back_bottom, front_top, back_top


class TorsoFrontHalfPanel(BaseBodicePanel):
    """Half of a simple non-fitted upper garment (e.g. T-Shirt)
    
        Fits to the bust size
    """
    def __init__(self, name, body, design) -> None:
        """ Front = True, provides the adjustments necessary for the front panel
        """
        super().__init__(name, body, design)

        full_design = design
        design = design['shirt']

        if 'measurement_shirt' in full_design:
            b_width, _, self.width, _ = _measurement_widths(
                body, full_design)
        else:
            # width
            m_width = design['width']['v'] * body['bust']
            b_width = design['flare']['v'] * m_width

            # sizes
            body_width = (body['bust'] - body['back_width']) / 2
            frac = body_width / body['bust']
            self.width = frac * m_width
            b_width = frac * b_width

        sh_tan = np.tan(np.deg2rad(body['_shoulder_incl']))
        shoulder_incl = sh_tan * self.width
        if 'measurement_shirt' in full_design:
            # The flat measurement ends at the highest retained shoulder point,
            # after the neckline has removed the center portion.
            neck_half = _measurement_value(full_design, 'neck_width') / 2
            length = (
                _measurement_value(full_design, 'front_length')
                - sh_tan * (self.width - neck_half)
            )
        else:
            length = design['length']['v'] * body['waist_line']

            # length in the front panel is adjusted due to shoulder inclination
            # for the correct sleeve fitting
            fb_diff = (frac - (0.5 - frac)) * body['bust']
            length = length - sh_tan * fb_diff

        self.edges = pyg.EdgeSeqFactory.from_verts(
            [0, 0], 
            [-b_width, 0], 
            [-self.width, length], 
            [0, length + shoulder_incl], 
            loop=True
        )

        # Interfaces
        self.interfaces = {
            'outside':  pyg.Interface(self, self.edges[1]),   
            'inside': pyg.Interface(self, self.edges[-1]),
            'shoulder': pyg.Interface(self, self.edges[-2]),
            'bottom': pyg.Interface(self, self.edges[0], ruffle=self.width / ((body['waist'] - body['waist_back_width']) / 2)),
            
            # Reference to the corner for sleeve and collar projections
            'shoulder_corner': pyg.Interface(self, [self.edges[-3], self.edges[-2]]),
            'collar_corner': pyg.Interface(self, [self.edges[-2], self.edges[-1]])
        }

        # default placement
        self.translate_by([0, body['height'] - body['head_l'] - length - shoulder_incl, 0])

    def get_width(self, level):
        return super().get_width(level) + self.width - self.body['shoulder_w'] / 2


class TorsoBackHalfPanel(BaseBodicePanel):
    """Half of a simple non-fitted upper garment (e.g. T-Shirt)
    
        Fits to the bust size
    """
    def __init__(self, name, body, design) -> None:
        """ Front = True, provides the adjustments necessary for the front panel
        """
        super().__init__(name, body, design)

        full_design = design
        design = design['shirt']
        if 'measurement_shirt' in full_design:
            _, b_width, _, self.width = _measurement_widths(
                body, full_design)
        else:
            # account for ease in basic measurements
            m_width = design['width']['v'] * body['bust']
            b_width = design['flare']['v'] * m_width

            # sizes
            body_width = body['back_width'] / 2
            frac = body_width / body['bust']
            self.width = frac * m_width
            b_width = frac * b_width

        shoulder_incl = (np.tan(np.deg2rad(body['_shoulder_incl']))) * self.width
        if 'measurement_shirt' in full_design:
            # Match the front side seam; the back shoulder may be higher due
            # to its independently measured upper width.
            front_width = _measurement_widths(body, full_design)[2]
            neck_half = _measurement_value(full_design, 'neck_width') / 2
            front_shoulder = np.tan(np.deg2rad(body['_shoulder_incl'])) * (
                front_width - neck_half
            )
            length = (
                _measurement_value(full_design, 'front_length')
                - front_shoulder
            )
        else:
            length = design['length']['v'] * body['waist_line']

        self.edges = pyg.EdgeSeqFactory.from_verts(
            [0, 0], 
            [-b_width, 0], 
            [-self.width, length], 
            [0, length + shoulder_incl], 
            loop=True
        )

        # Interfaces
        self.interfaces = {
            'outside':  pyg.Interface(self, self.edges[1]),   
            'inside': pyg.Interface(self, self.edges[-1]),
            'shoulder': pyg.Interface(self, self.edges[-2]),
            'bottom': pyg.Interface(self, self.edges[0], ruffle=self.width / (body['waist_back_width'] / 2)),
            
            # Reference to the corner for sleeve and collar projections
            'shoulder_corner': pyg.Interface(self, [self.edges[-3], self.edges[-2]]),
            'collar_corner': pyg.Interface(self, [self.edges[-2], self.edges[-1]])
        }

        # default placement
        self.translate_by([0, body['height'] - body['head_l'] - length - shoulder_incl, 0])

    def get_width(self, level):
        return super().get_width(level) + self.width - self.body['shoulder_w'] / 2
