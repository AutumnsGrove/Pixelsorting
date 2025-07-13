"""
Custom exception classes for pixel sorting operations.

This module defines specific exception types for different error conditions
that can occur during pixel sorting operations, providing more informative
error messages and better error handling.
"""

from typing import Optional


class PixelSortError(Exception):
    """
    Base exception class for all pixel sorting related errors.
    
    This serves as the base class for all custom exceptions in the
    pixel sorting system, allowing for catch-all error handling.
    """
    pass


class ImageError(PixelSortError):
    """
    Exception raised for image-related errors.
    
    This includes errors in loading, processing, or saving images.
    """
    
    def __init__(self, message: str, image_path: Optional[str] = None):
        """
        Initialize ImageError.
        
        Args:
            message: Error message
            image_path: Optional path to the problematic image
        """
        self.image_path = image_path
        if image_path:
            super().__init__(f"{message} (Image: {image_path})")
        else:
            super().__init__(message)


class ImageNotFoundError(ImageError):
    """
    Exception raised when an image file cannot be found.
    """
    
    def __init__(self, image_path: str):
        """
        Initialize ImageNotFoundError.
        
        Args:
            image_path: Path to the missing image file
        """
        super().__init__(f"Image file not found: {image_path}", image_path)


class ImageLoadError(ImageError):
    """
    Exception raised when an image cannot be loaded or processed.
    """
    
    def __init__(self, message: str, image_path: Optional[str] = None, 
                 original_error: Optional[Exception] = None):
        """
        Initialize ImageLoadError.
        
        Args:
            message: Error message
            image_path: Optional path to the problematic image
            original_error: Optional original exception that caused this error
        """
        self.original_error = original_error
        if original_error:
            full_message = f"{message}. Original error: {str(original_error)}"
        else:
            full_message = message
        super().__init__(full_message, image_path)


class NetworkError(ImageError):
    """
    Exception raised for network-related errors when loading remote images.
    """
    
    def __init__(self, url: str, original_error: Optional[Exception] = None):
        """
        Initialize NetworkError.
        
        Args:
            url: URL that failed to load
            original_error: Optional original network exception
        """
        self.original_error = original_error
        message = f"Failed to load image from URL: {url}"
        if original_error:
            message += f". Network error: {str(original_error)}"
        super().__init__(message, url)


class ConfigurationError(PixelSortError):
    """
    Exception raised for configuration-related errors.
    
    This includes invalid parameter values, missing required settings,
    or incompatible configuration combinations.
    """
    
    def __init__(self, message: str, parameter: Optional[str] = None, 
                 value: Optional[any] = None):
        """
        Initialize ConfigurationError.
        
        Args:
            message: Error message
            parameter: Optional name of the problematic parameter
            value: Optional value that caused the error
        """
        self.parameter = parameter
        self.value = value
        
        if parameter and value is not None:
            full_message = f"{message} (Parameter: {parameter}, Value: {value})"
        elif parameter:
            full_message = f"{message} (Parameter: {parameter})"
        else:
            full_message = message
            
        super().__init__(full_message)


class InvalidParameterError(ConfigurationError):
    """
    Exception raised when a parameter has an invalid value.
    """
    
    def __init__(self, parameter: str, value: any, expected: str):
        """
        Initialize InvalidParameterError.
        
        Args:
            parameter: Name of the invalid parameter
            value: The invalid value
            expected: Description of expected value
        """
        message = f"Invalid value for {parameter}: got {value}, expected {expected}"
        super().__init__(message, parameter, value)


class MissingParameterError(ConfigurationError):
    """
    Exception raised when a required parameter is missing.
    """
    
    def __init__(self, parameter: str):
        """
        Initialize MissingParameterError.
        
        Args:
            parameter: Name of the missing parameter
        """
        message = f"Required parameter missing: {parameter}"
        super().__init__(message, parameter)


class ProcessingError(PixelSortError):
    """
    Exception raised for errors during pixel sorting processing.
    
    This includes errors in interval generation, pixel sorting,
    or image reconstruction.
    """
    
    def __init__(self, message: str, processing_stage: Optional[str] = None,
                 original_error: Optional[Exception] = None):
        """
        Initialize ProcessingError.
        
        Args:
            message: Error message
            processing_stage: Optional name of the processing stage where error occurred
            original_error: Optional original exception that caused this error
        """
        self.processing_stage = processing_stage
        self.original_error = original_error
        
        if processing_stage:
            full_message = f"{message} (Stage: {processing_stage})"
        else:
            full_message = message
            
        if original_error:
            full_message += f". Original error: {str(original_error)}"
            
        super().__init__(full_message)


class IntervalGenerationError(ProcessingError):
    """
    Exception raised for errors during interval generation.
    """
    
    def __init__(self, interval_function: str, message: str, 
                 original_error: Optional[Exception] = None):
        """
        Initialize IntervalGenerationError.
        
        Args:
            interval_function: Name of the interval function that failed
            message: Error message
            original_error: Optional original exception that caused this error
        """
        self.interval_function = interval_function
        full_message = f"Interval generation failed with function '{interval_function}': {message}"
        super().__init__(full_message, "interval_generation", original_error)


class SortingError(ProcessingError):
    """
    Exception raised for errors during pixel sorting.
    """
    
    def __init__(self, sorting_function: str, message: str,
                 original_error: Optional[Exception] = None):
        """
        Initialize SortingError.
        
        Args:
            sorting_function: Name of the sorting function that failed
            message: Error message
            original_error: Optional original exception that caused this error
        """
        self.sorting_function = sorting_function
        full_message = f"Pixel sorting failed with function '{sorting_function}': {message}"
        super().__init__(full_message, "sorting", original_error)


class FunctionNotFoundError(PixelSortError):
    """
    Exception raised when a requested function (interval or sorting) is not found.
    """
    
    def __init__(self, function_type: str, function_name: str, available_functions: list):
        """
        Initialize FunctionNotFoundError.
        
        Args:
            function_type: Type of function (e.g., "interval", "sorting")
            function_name: Name of the requested function
            available_functions: List of available function names
        """
        self.function_type = function_type
        self.function_name = function_name
        self.available_functions = available_functions
        
        available_str = ", ".join(available_functions)
        message = (f"Unknown {function_type} function '{function_name}'. "
                  f"Available functions: {available_str}")
        super().__init__(message)


class OutputError(PixelSortError):
    """
    Exception raised for errors during output operations.
    
    This includes errors in saving processed images or creating output directories.
    """
    
    def __init__(self, message: str, output_path: Optional[str] = None,
                 original_error: Optional[Exception] = None):
        """
        Initialize OutputError.
        
        Args:
            message: Error message
            output_path: Optional path where output was attempted
            original_error: Optional original exception that caused this error
        """
        self.output_path = output_path
        self.original_error = original_error
        
        if output_path:
            full_message = f"{message} (Output path: {output_path})"
        else:
            full_message = message
            
        if original_error:
            full_message += f". Original error: {str(original_error)}"
            
        super().__init__(full_message)


class DirectoryCreationError(OutputError):
    """
    Exception raised when output directories cannot be created.
    """
    
    def __init__(self, directory_path: str, original_error: Exception):
        """
        Initialize DirectoryCreationError.
        
        Args:
            directory_path: Path to the directory that couldn't be created
            original_error: Original filesystem exception
        """
        message = f"Failed to create output directory: {directory_path}"
        super().__init__(message, directory_path, original_error)


class ImageSaveError(OutputError):
    """
    Exception raised when processed images cannot be saved.
    """
    
    def __init__(self, output_path: str, original_error: Exception):
        """
        Initialize ImageSaveError.
        
        Args:
            output_path: Path where the image save was attempted
            original_error: Original save exception
        """
        message = f"Failed to save image to: {output_path}"
        super().__init__(message, output_path, original_error)


# Convenience functions for common error patterns

def raise_image_not_found(image_path: str) -> None:
    """
    Raise ImageNotFoundError with consistent message format.
    
    Args:
        image_path: Path to the missing image
        
    Raises:
        ImageNotFoundError: Always raises this exception
    """
    raise ImageNotFoundError(image_path)


def raise_invalid_parameter(parameter: str, value: any, expected: str) -> None:
    """
    Raise InvalidParameterError with consistent message format.
    
    Args:
        parameter: Name of the invalid parameter
        value: The invalid value
        expected: Description of expected value
        
    Raises:
        InvalidParameterError: Always raises this exception
    """
    raise InvalidParameterError(parameter, value, expected)


def raise_function_not_found(function_type: str, function_name: str, 
                           available_functions: list) -> None:
    """
    Raise FunctionNotFoundError with consistent message format.
    
    Args:
        function_type: Type of function
        function_name: Name of the requested function
        available_functions: List of available functions
        
    Raises:
        FunctionNotFoundError: Always raises this exception
    """
    raise FunctionNotFoundError(function_type, function_name, available_functions)


# Exception handling utilities

def handle_image_error(func):
    """
    Decorator to handle common image errors and convert them to custom exceptions.
    
    Args:
        func: Function to wrap
        
    Returns:
        Wrapped function that converts standard exceptions to custom ones
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError as e:
            # Extract image path from args or kwargs if possible
            image_path = args[0] if args else kwargs.get('image_path', 'unknown')
            raise ImageNotFoundError(str(image_path)) from e
        except (OSError, IOError) as e:
            image_path = args[0] if args else kwargs.get('image_path', 'unknown')
            raise ImageLoadError(f"Failed to load image: {str(e)}", str(image_path), e) from e
        except Exception as e:
            # Re-raise custom exceptions as-is
            if isinstance(e, PixelSortError):
                raise
            # Convert other exceptions to generic processing errors
            raise ProcessingError(f"Unexpected error in {func.__name__}: {str(e)}", 
                                func.__name__, e) from e
    
    return wrapper


def handle_processing_error(stage: str):
    """
    Decorator to handle processing errors for specific stages.
    
    Args:
        stage: Name of the processing stage
        
    Returns:
        Decorator function
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except PixelSortError:
                # Re-raise custom exceptions as-is
                raise
            except Exception as e:
                raise ProcessingError(f"Error in {stage}: {str(e)}", stage, e) from e
        return wrapper
    return decorator