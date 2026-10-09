"""
SHARED - picks the right model file for a variant.

    variant.config == 'A'  ->  phase2A_asbuilt_flatslab_model.AsBuiltFlatSlabModel
    variant.config == 'B'  ->  phase2B_proposed_beamslab_model.ProposedBeamSlabModel
"""
import importlib
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def model_class(config):
    if _ROOT not in sys.path:
        sys.path.insert(0, _ROOT)
    if config == "A":
        return importlib.import_module("phase2A_asbuilt_flatslab_model").AsBuiltFlatSlabModel
    if config == "B":
        return importlib.import_module("phase2B_proposed_beamslab_model").ProposedBeamSlabModel
    raise ValueError(config)
