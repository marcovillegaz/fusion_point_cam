"""MPC Image Processing Package

A modular pipeline for processing fusion point camera images.
"""

__version__ = "0.1.0"

from .classes.imagePipeline import ImagePipeline
from . import utils
from . import analysis

__all__ = ["ImagePipeline", "utils", "analysis"]
