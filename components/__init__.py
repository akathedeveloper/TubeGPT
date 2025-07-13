"""
TubeGPT Components Package

This package contains all the UI and functional components for the TubeGPT application.
"""

from .ui_components import UIComponents
from .auth_component import AuthComponent
from .video_component import VideoComponent
from .chat_component import ChatComponent
from .analytics_component import AnalyticsComponent

__all__ = [
    'UIComponents',
    'AuthComponent', 
    'VideoComponent',
    'ChatComponent',
    'AnalyticsComponent'
]

__version__ = '2.0.0'
