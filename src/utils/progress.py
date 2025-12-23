#!/usr/bin/env python3
"""
Progress indicator utility for CLI operations
Provides animated spinners for better UX during long-running tasks
"""
import sys
import threading
import time
from typing import Optional


class Spinner:
    """
    Animated spinner for CLI progress indication
    
    Usage:
        with Spinner("Processing image..."):
            # Long-running operation
            process_image()
    """
    
    # Spinner animation frames
    FRAMES = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    
    def __init__(self, message: str = "Processing...", stream=None):
        """
        Initialize spinner
        
        Args:
            message: Message to display alongside spinner
            stream: Output stream (defaults to sys.stderr)
        """
        self.message = message
        self.stream = stream or sys.stderr
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._frame_index = 0
        
    def _animate(self):
        """Animation loop running in separate thread"""
        while not self._stop_event.is_set():
            frame = self.FRAMES[self._frame_index % len(self.FRAMES)]
            # Write spinner frame and message
            self.stream.write(f'\r{frame} {self.message}')
            self.stream.flush()
            self._frame_index += 1
            time.sleep(0.1)
    
    def start(self):
        """Start the spinner animation"""
        if self._thread is None or not self._thread.is_alive():
            self._stop_event.clear()
            self._thread = threading.Thread(target=self._animate, daemon=True)
            self._thread.start()
        return self
    
    def stop(self, final_message: Optional[str] = None):
        """
        Stop the spinner animation
        
        Args:
            final_message: Optional message to display after stopping
        """
        if self._thread and self._thread.is_alive():
            self._stop_event.set()
            self._thread.join()
            
            # Clear the spinner line
            self.stream.write('\r' + ' ' * (len(self.message) + 3) + '\r')
            
            # Print final message if provided
            if final_message:
                self.stream.write(final_message + '\n')
            
            self.stream.flush()
    
    def __enter__(self):
        """Context manager entry"""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop()
        return False
    
    def update_message(self, new_message: str):
        """
        Update the spinner message while running
        
        Args:
            new_message: New message to display
        """
        self.message = new_message
