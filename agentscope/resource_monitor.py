"""
Resource monitoring utilities for tracking system usage during LLM calls.

This module provides tools to monitor CPU, memory, and GPU utilization.
"""
import psutil
from typing import Optional

# Try to import GPU monitoring library
try:
    import pynvml
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False


class ResourceMonitor:
    """
    Monitor system resources during LLM inference.
    
    Tracks:
        - CPU usage (percentage)
        - Memory usage (MB)
        - GPU utilization (if available)
    
    Usage:
        with tracer.start_as_current_span("llm_call") as span:
            ResourceMonitor.capture(span)
            # ... make LLM call ...
    """
    
    _gpu_initialized = False
    
    @classmethod
    def _init_gpu(cls):
        """Initialize GPU monitoring if available."""
        if GPU_AVAILABLE and not cls._gpu_initialized:
            try:
                pynvml.nvmlInit()
                cls._gpu_initialized = True
            except Exception:
                pass  # GPU monitoring is optional
    
    @classmethod
    def capture(cls, span, include_gpu: bool = True):
        """
        Capture current resource usage and attach to span.
        
        Args:
            span: OpenTelemetry span to attach metrics to
            include_gpu: Whether to attempt GPU monitoring (default True)
        """
        # CPU usage (average over 0.1 second interval)
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            span.set_attribute("system.cpu_percent", round(cpu_percent, 1))
        except Exception:
            pass  # CPU monitoring is optional
        
        # Memory usage (process RSS in MB)
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024
            span.set_attribute("system.memory_mb", round(memory_mb, 1))
        except Exception:
            pass  # Memory monitoring is optional
        
        # GPU utilization (if available)
        if include_gpu and GPU_AVAILABLE:
            cls._capture_gpu(span)
    
    @classmethod
    def _capture_gpu(cls, span):
        """
        Capture GPU metrics and attach to span.
        
        Args:
            span: OpenTelemetry span to attach metrics to
        """
        try:
            cls._init_gpu()
            
            if cls._gpu_initialized:
                # Get first GPU device (index 0)
                handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                
                # GPU utilization percentage
                util = pynvml.nvmlDeviceGetUtilizationRates(handle)
                span.set_attribute("system.gpu_utilization", round(util.gpu, 1))
                
                # GPU memory usage
                mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                gpu_mem_used_mb = mem_info.used / 1024 / 1024
                gpu_mem_total_mb = mem_info.total / 1024 / 1024
                
                span.set_attribute("system.gpu_memory_used_mb", round(gpu_mem_used_mb, 1))
                span.set_attribute("system.gpu_memory_total_mb", round(gpu_mem_total_mb, 1))
                
        except Exception:
            # GPU monitoring is optional, fail silently
            pass
    
    @classmethod
    def get_current_usage(cls, include_gpu: bool = True) -> dict:
        """
        Get current resource usage as a dictionary.
        
        Args:
            include_gpu: Whether to include GPU metrics (default True)
        
        Returns:
            Dictionary containing resource metrics
        """
        metrics = {}
        
        # CPU
        try:
            metrics['cpu_percent'] = round(psutil.cpu_percent(interval=0.1), 1)
        except Exception:
            pass
        
        # Memory
        try:
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            metrics['memory_mb'] = round(memory_mb, 1)
        except Exception:
            pass
        
        # GPU
        if include_gpu and GPU_AVAILABLE:
            try:
                cls._init_gpu()
                if cls._gpu_initialized:
                    handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                    util = pynvml.nvmlDeviceGetUtilizationRates(handle)
                    metrics['gpu_utilization'] = round(util.gpu, 1)
                    
                    mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                    metrics['gpu_memory_used_mb'] = round(mem_info.used / 1024 / 1024, 1)
                    metrics['gpu_memory_total_mb'] = round(mem_info.total / 1024 / 1024, 1)
            except Exception:
                pass
        
        return metrics
    
    @classmethod
    def cleanup(cls):
        """Cleanup GPU monitoring resources."""
        if cls._gpu_initialized and GPU_AVAILABLE:
            try:
                pynvml.nvmlShutdown()
                cls._gpu_initialized = False
            except Exception:
                pass
