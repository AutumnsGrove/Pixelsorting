"""
Progress management for Gradio interface.

This module provides utilities to replace tqdm progress bars with Gradio progress
for use in the web interface.
"""

from typing import Optional, Callable, Any
import gradio as gr
from functools import wraps


class ProgressManager:
    """
    Manages progress reporting for the Gradio interface.
    
    This class provides a way to track progress across different processing steps
    and report it to the Gradio interface.
    """
    
    def __init__(self, progress: Optional[gr.Progress] = None):
        """
        Initialize the progress manager.
        
        Args:
            progress: Gradio progress tracker instance
        """
        self.progress = progress
        self.current_step = 0
        self.total_steps = 0
        self.step_weights = {}
        
    def set_steps(self, step_weights: dict):
        """
        Set the processing steps and their relative weights.
        
        Args:
            step_weights: Dictionary mapping step names to their weights (0.0-1.0)
        """
        self.step_weights = step_weights
        self.total_steps = len(step_weights)
        self.current_step = 0
        
    def start_step(self, step_name: str, description: str = ""):
        """
        Start a new processing step.
        
        Args:
            step_name: Name of the step
            description: Description to show in progress
        """
        if self.progress is None:
            return
            
        if step_name in self.step_weights:
            # Calculate cumulative progress up to this step
            cumulative_progress = sum(
                weight for name, weight in self.step_weights.items()
                if list(self.step_weights.keys()).index(name) < list(self.step_weights.keys()).index(step_name)
            )
            
            self.progress(cumulative_progress, desc=description or f"Processing {step_name}...")
    
    def update_step(self, step_name: str, progress_within_step: float, description: str = ""):
        """
        Update progress within the current step.
        
        Args:
            step_name: Name of the current step
            progress_within_step: Progress within step (0.0-1.0)
            description: Description to show in progress
        """
        if self.progress is None:
            return
            
        if step_name in self.step_weights:
            # Calculate cumulative progress up to this step
            cumulative_progress = sum(
                weight for name, weight in self.step_weights.items()
                if list(self.step_weights.keys()).index(name) < list(self.step_weights.keys()).index(step_name)
            )
            
            # Add progress within current step
            step_weight = self.step_weights[step_name]
            current_progress = cumulative_progress + (step_weight * progress_within_step)
            
            self.progress(current_progress, desc=description or f"Processing {step_name}...")
    
    def complete_step(self, step_name: str, description: str = ""):
        """
        Mark a step as complete.
        
        Args:
            step_name: Name of the completed step
            description: Description to show in progress
        """
        if self.progress is None:
            return
            
        self.update_step(step_name, 1.0, description)


def progress_wrapper(progress_manager: Optional[ProgressManager], step_name: str):
    """
    Decorator to wrap functions with progress tracking.
    
    Args:
        progress_manager: Progress manager instance
        step_name: Name of the step for progress tracking
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if progress_manager:
                progress_manager.start_step(step_name)
            
            result = func(*args, **kwargs)
            
            if progress_manager:
                progress_manager.complete_step(step_name)
                
            return result
        return wrapper
    return decorator


class GradioProgressReporter:
    """
    A replacement for tqdm that reports to Gradio progress instead.
    """
    
    def __init__(self, total: int, desc: str = "", progress_manager: Optional[ProgressManager] = None, step_name: str = ""):
        """
        Initialize the progress reporter.
        
        Args:
            total: Total number of iterations
            desc: Description for the progress
            progress_manager: Progress manager instance
            step_name: Name of the current step
        """
        self.total = total
        self.desc = desc
        self.progress_manager = progress_manager
        self.step_name = step_name
        self.current = 0
        
    def update(self, n: int = 1):
        """
        Update the progress by n steps.
        
        Args:
            n: Number of steps to advance
        """
        self.current += n
        if self.progress_manager and self.step_name:
            progress_ratio = self.current / self.total if self.total > 0 else 1.0
            self.progress_manager.update_step(self.step_name, progress_ratio, self.desc)
    
    def __enter__(self):
        """Enter context manager."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager."""
        if self.progress_manager and self.step_name:
            self.progress_manager.complete_step(self.step_name, f"{self.desc} - Complete")
        
    def __iter__(self):
        """Iterator interface."""
        for i in range(self.total):
            yield i
            self.update(1)


def gradio_trange(total: int, desc: str = "", progress_manager: Optional[ProgressManager] = None, step_name: str = ""):
    """
    Gradio-compatible replacement for tqdm.trange.
    
    Args:
        total: Total number of iterations
        desc: Description for the progress
        progress_manager: Progress manager instance
        step_name: Name of the current step
        
    Returns:
        Iterator with progress tracking
    """
    reporter = GradioProgressReporter(total, desc, progress_manager, step_name)
    return reporter


def gradio_tqdm(iterable, desc: str = "", progress_manager: Optional[ProgressManager] = None, step_name: str = ""):
    """
    Gradio-compatible replacement for tqdm.tqdm.
    
    Args:
        iterable: Iterable to track progress for
        desc: Description for the progress
        progress_manager: Progress manager instance
        step_name: Name of the current step
        
    Returns:
        Iterator with progress tracking
    """
    total = len(iterable) if hasattr(iterable, '__len__') else None
    reporter = GradioProgressReporter(total or 0, desc, progress_manager, step_name)
    
    for i, item in enumerate(iterable):
        yield item
        reporter.update(1)