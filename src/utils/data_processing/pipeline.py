"""
Processing pipeline for orchestrating data processing operations.
"""
from typing import List, Dict, Any, Optional, Callable
from .base import BaseProcessor, ProcessingResult


class ProcessingPipeline(BaseProcessor):
    """Orchestrates multiple processing steps in sequence."""
    
    def __init__(self, name: str = "ProcessingPipeline"):
        super().__init__(name)
        self.steps: List[tuple] = []  # List of (processor, condition_func)
        self.error_handling = 'continue'  # 'continue', 'stop', 'collect'
        self.collect_errors = True
        self.results: List[ProcessingResult] = []
    
    def add_step(self, processor: BaseProcessor, condition: Optional[Callable[[Any], bool]] = None):
        """
        Add a processing step to the pipeline.
        
        Args:
            processor: The processor to execute
            condition: Optional function to determine if step should run
        """
        self.steps.append((processor, condition))
        return self
    
    def set_error_handling(self, mode: str):
        """Set error handling mode: 'continue', 'stop', or 'collect'."""
        if mode not in ['continue', 'stop', 'collect']:
            raise ValueError("Error handling mode must be 'continue', 'stop', or 'collect'")
        self.error_handling = mode
        return self
    
    def process(self, data: Any) -> Any:
        """Execute all pipeline steps."""
        current_data = data
        self.results.clear()
        
        for i, (processor, condition) in enumerate(self.steps):
            try:
                # Check condition if provided
                if condition and not condition(current_data):
                    self.logger.debug(f"Skipping step {i+1}: {processor.name} (condition not met)")
                    continue
                
                # Execute processor
                self.logger.debug(f"Executing step {i+1}: {processor.name}")
                
                # Handle list vs single item processing
                if isinstance(current_data, list):
                    # Check if processor can handle lists (has list-specific methods)
                    processor_class = processor.__class__.__name__
                    if processor_class in ['DuplicateFilter', 'RatingFilter', 'RatingSorter', 'FieldSorter', 
                                          'TextFilter', 'RangeFilter', 'NullFilter', 'MultiFieldSorter', 
                                          'TextSorter', 'LengthSorter']:
                        # These processors expect lists
                        result_data = processor.process(current_data)
                    else:
                        # Individual item processors - process each item
                        result_data = []
                        for item in current_data:
                            try:
                                result = processor.process(item)
                                if result is not None:
                                    result_data.append(result)
                            except Exception as e:
                                self.logger.warning(f"Error processing item in {processor.name}: {e}")
                                continue
                    current_data = result_data
                else:
                    # Single item processing
                    result_data = processor.process(current_data)
                    current_data = result_data
                
                # Create result object
                result = ProcessingResult(current_data, success=True)
                result.set_metadata('step', i+1)
                result.set_metadata('processor', processor.name)
                self.results.append(result)
                
                current_data = result_data
                
            except Exception as e:
                error_msg = f"Error in step {i+1} ({processor.name}): {e}"
                self.logger.error(error_msg)
                
                # Create error result
                result = ProcessingResult(current_data, success=False, errors=[error_msg])
                result.set_metadata('step', i+1)
                result.set_metadata('processor', processor.name)
                self.results.append(result)
                
                # Handle error based on mode
                if self.error_handling == 'stop':
                    raise
                elif self.error_handling == 'collect':
                    # Continue but collect errors
                    continue
                # 'continue' mode - just continue to next step
        
        return current_data
    
    def get_results(self) -> List[ProcessingResult]:
        """Get all processing results with metadata."""
        return self.results
    
    def get_errors(self) -> List[str]:
        """Get all errors from processing."""
        errors = []
        for result in self.results:
            errors.extend(result.errors)
        return errors
    
    def clear_steps(self):
        """Clear all processing steps."""
        self.steps.clear()
        return self


class BatchProcessingPipeline(ProcessingPipeline):
    """Pipeline for processing batches of items."""
    
    def __init__(self, name: str = "BatchProcessingPipeline"):
        super().__init__(name)
        self.batch_size = 100
        self.progress_callback: Optional[Callable[[int, int], None]] = None
    
    def set_batch_size(self, size: int):
        """Set batch size for processing."""
        self.batch_size = size
        return self
    
    def set_progress_callback(self, callback: Callable[[int, int], None]):
        """Set callback for progress updates (current, total)."""
        self.progress_callback = callback
        return self
    
    def process(self, data: List[Any]) -> List[Any]:
        """Process items in batches."""
        if not isinstance(data, list):
            raise ValueError("BatchProcessingPipeline requires list input")
        
        total_items = len(data)
        processed_items = data.copy()  # Start with original data
        
        # Process each step on the entire list
        for processor, condition in self.steps:
            try:
                # Check condition if provided
                if condition and not condition(processed_items):
                    self.logger.debug(f"Skipping step: {processor.name} (condition not met)")
                    continue
                
                # Execute processor on the entire list
                self.logger.debug(f"Executing step: {processor.name}")
                
                # Check if processor can handle lists directly
                processor_class = processor.__class__.__name__
                if processor_class in ['DuplicateFilter', 'RatingFilter', 'RatingSorter', 'FieldSorter', 
                                      'TextFilter', 'RangeFilter', 'NullFilter', 'MultiFieldSorter', 
                                      'TextSorter', 'LengthSorter']:
                    # These processors expect lists
                    processed_items = processor.process(processed_items)
                else:
                    # Individual item processors - process each item
                    new_items = []
                    for item in processed_items:
                        try:
                            result = processor.process(item)
                            if result is not None:
                                new_items.append(result)
                        except Exception as e:
                            self.logger.warning(f"Error processing item in {processor.name}: {e}")
                            continue
                    processed_items = new_items
                
                # Update progress
                if self.progress_callback:
                    self.progress_callback(total_items, total_items)
                    
            except Exception as e:
                error_msg = f"Error in step {processor.name}: {e}"
                self.logger.error(error_msg)
                
                if self.error_handling == 'stop':
                    raise
                # For other modes, continue with current data
        
        return processed_items


class ConditionalPipeline(ProcessingPipeline):
    """Pipeline with conditional branching."""
    
    def __init__(self, name: str = "ConditionalPipeline"):
        super().__init__(name)
        self.conditional_steps: List[tuple] = []  # List of (condition, pipeline)
    
    def add_conditional_branch(self, condition: Callable[[Any], bool], pipeline: ProcessingPipeline):
        """
        Add a conditional branch to the pipeline.
        
        Args:
            condition: Function that returns True if this branch should be taken
            pipeline: Pipeline to execute if condition is met
        """
        self.conditional_steps.append((condition, pipeline))
        return self
    
    def process(self, data: Any) -> Any:
        """Execute pipeline with conditional branching."""
        current_data = data
        
        # Execute main steps first
        current_data = super().process(current_data)
        
        # Check conditional branches
        for condition, pipeline in self.conditional_steps:
            try:
                if condition(current_data):
                    self.logger.debug(f"Taking conditional branch: {pipeline.name}")
                    current_data = pipeline.process(current_data)
            except Exception as e:
                self.logger.error(f"Error in conditional branch {pipeline.name}: {e}")
                if self.error_handling == 'stop':
                    raise
        
        return current_data


class ParallelPipeline(ProcessingPipeline):
    """Pipeline that can execute steps in parallel (for independent operations)."""
    
    def __init__(self, name: str = "ParallelPipeline"):
        super().__init__(name)
        self.parallel_steps: List[List[tuple]] = []  # List of lists of parallel steps
    
    def add_parallel_step(self, processors: List[BaseProcessor]):
        """
        Add a set of processors that can run in parallel.
        
        Args:
            processors: List of processors to execute in parallel
        """
        self.parallel_steps.append([(processor, None) for processor in processors])
        return self
    
    def process(self, data: Any) -> Any:
        """Execute pipeline with parallel steps."""
        current_data = data
        
        # Execute sequential steps
        for processor, condition in self.steps:
            if condition and not condition(current_data):
                continue
            current_data = processor.process(current_data)
        
        # Execute parallel steps (simplified version - runs sequentially for now)
        # In a real implementation, this would use threading/multiprocessing
        for parallel_group in self.parallel_steps:
            results = []
            for processor, condition in parallel_group:
                if condition and not condition(current_data):
                    continue
                try:
                    result = processor.process(current_data)
                    results.append(result)
                except Exception as e:
                    self.logger.error(f"Error in parallel step {processor.name}: {e}")
                    if self.error_handling == 'stop':
                        raise
            
            # For now, just use the last successful result
            # In a real implementation, you'd merge results appropriately
            if results:
                current_data = results[-1]
        
        return current_data
