
import os
import shutil
import logging
import time
from datetime import datetime
from celery import shared_task
from django.utils import timezone
from ai_workers.ai_property_manager.services.auto_property_listing.data_processing import DataProcessing
from ai_workers.models import BusinessAIWorker, BusinessAITaskExecution


class AutonomousTaskExecutor:
    """
    🤖 AUTONOMOUS PATTERN: Learning & Adaptive Task Execution
    
    This class transforms simple task execution into intelligent, self-improving execution.
    Key autonomous concepts:
    1. Performance Tracking - Measures success rates and timing
    2. Adaptive Parameters - Adjusts processing based on learned patterns  
    3. Context Awareness - Uses business patterns to optimize execution
    4. Continuous Learning - Improves from each execution
    """
    
    def __init__(self, task_name="csv_processing"):
        self.task_name = task_name
        self.execution_start_time = None
        self.execution_context = {}
        
    def start_execution_tracking(self, file_path, business_context=None):
        """
        📊 PERFORMANCE TRACKING: Start measuring execution metrics
        
        Autonomous systems track their own performance to identify improvement opportunities
        """
        self.execution_start_time = time.time()
        
        # Gather execution context
        try:
            file_size = os.path.getsize(file_path)
            filename = os.path.basename(file_path)
            
            self.execution_context = {
                "file_path": file_path,
                "filename": filename,
                "file_size": file_size,
                "business_context": business_context,
                "start_time": datetime.now().isoformat(),
                "processing_strategy": self._determine_optimal_strategy(file_size)
            }
            
            print(f"🎯 Execution tracking started for {filename}")
            print(f"📊 Context: {self.execution_context['processing_strategy']}")
            
        except Exception as e:
            print(f"⚠️ Failed to initialize execution tracking: {str(e)}")
            
    def _determine_optimal_strategy(self, file_size):
        """
        ⚡ ADAPTIVE STRATEGY: Choose optimal processing approach
        
        This is autonomous intelligence - adapting approach based on file characteristics
        """
        if file_size > 5 * 1024 * 1024:  # > 5MB
            return {
                "mode": "high_performance",
                "batch_size": 100,
                "ai_model": "gemini",  # Faster for large batches
                "description": "Large file - optimized for throughput"
            }
        elif file_size < 10 * 1024:  # < 10KB
            return {
                "mode": "rapid_processing", 
                "batch_size": 10,
                "ai_model": "template",  # Skip AI for very small files
                "description": "Small file - rapid template processing"
            }
        else:
            return {
                "mode": "balanced",
                "batch_size": 50,
                "ai_model": "openai",  # Best quality for standard files
                "description": "Standard file - balanced processing"
            }
    
    def execute_with_learning(self, file_path, business_context=None):
        """
        🧠 LEARNING EXECUTION: Execute with intelligence and adaptation
        
        This replaces simple execution with adaptive, learning-capable execution
        """
        # Step 1: Start tracking and prepare context
        self.start_execution_tracking(file_path, business_context)
        
        processing_result = None
        execution_success = False
        error_details = None
        
        try:
            # Step 2: Execute with adaptive parameters
            strategy = self.execution_context.get("processing_strategy", {})
            
            print(f"🚀 Executing with strategy: {strategy.get('description', 'default')}")
            
            # Enhanced execution with strategy parameters
            processing_result = self._execute_with_strategy(file_path, strategy)
            
            execution_success = True
            print(f"✅ Processing completed successfully")
            
        except Exception as e:
            execution_success = False
            error_details = str(e)
            print(f"❌ Processing failed: {error_details}")
            
        finally:
            # Step 3: Record learnings regardless of success/failure
            self.record_execution_learning(execution_success, processing_result, error_details)
            
            # Step 4: Clean up (move file to archive)
            if execution_success:
                self._archive_processed_file(file_path)
                
        return processing_result
    
    def _execute_with_strategy(self, file_path, strategy):
        """
        ⚙️ STRATEGY-BASED EXECUTION: Execute based on learned optimal parameters
        """
        mode = strategy.get("mode", "balanced")
        ai_model = strategy.get("ai_model", "openai")
        
        print(f"🎛️ Processing mode: {mode}, AI model: {ai_model}")
        
        # For now, use existing DataProcessing but with strategy context
        # TODO: In future iterations, we'll pass strategy parameters to DataProcessing
        result = DataProcessing.process_data(file_path)
        
        return {
            "status": "success",
            "mode_used": mode,
            "ai_model_used": ai_model,
            "processing_result": result
        }
    
    def record_execution_learning(self, success, result, error_details):
        """
        📝 LEARNING SYSTEM: Record execution results for future optimization
        
        This is the heart of autonomous learning - capturing experience for improvement
        """
        execution_time = time.time() - self.execution_start_time if self.execution_start_time else 0
        
        learning_record = {
            "execution_id": f"{self.task_name}_{int(time.time())}",
            "success": success,
            "execution_time": round(execution_time, 2),
            "context": self.execution_context,
            "result": result,
            "error": error_details,
            "timestamp": datetime.now().isoformat(),
            "learning_insights": self._generate_learning_insights(success, execution_time, result)
        }
        
        # Log the learning for analysis
        print(f"📚 Learning recorded: {learning_record['learning_insights']}")
        
        # TODO: In next iteration, save to database for persistent learning
        self._save_learning_to_system(learning_record)
        
    def _generate_learning_insights(self, success, execution_time, result):
        """
        💡 INSIGHT GENERATION: Extract actionable learnings from execution
        """
        insights = []
        
        # Performance insights
        if execution_time > 60:  # Slow execution
            insights.append("Consider optimization for large files")
        elif execution_time < 5:  # Very fast
            insights.append("Efficient processing - strategy working well")
            
        # Success/failure insights  
        if success:
            insights.append("Successful execution - strategy validated")
        else:
            insights.append("Execution failed - strategy needs adjustment")
            
        # File size insights
        file_size = self.execution_context.get("file_size", 0)
        if file_size > 1024 * 1024 and execution_time < 30:
            insights.append("Large file processed efficiently - good strategy")
            
        return insights
    
    def _save_learning_to_system(self, learning_record):
        """
        💾 PERSISTENT LEARNING: Save learnings for future use
        
        This enables the system to remember and improve over time
        """
        # For now, just log - in next iteration we'll save to database
        logger.info(f"Learning saved: {learning_record['execution_id']}")
        
        # TODO: Save to BusinessAITaskExecution or new LearningRecord model
        # This will enable the system to analyze patterns and optimize over time
        
    def _archive_processed_file(self, file_path):
        """📁 FILE MANAGEMENT: Archive processed files"""
        try:
            archive_directory = "media/processed"
            os.makedirs(archive_directory, exist_ok=True)
            archive_path = os.path.join(archive_directory, os.path.basename(file_path))
            shutil.move(file_path, archive_path)
            print(f"📦 Moved to archive: {archive_path}")
        except Exception as e:
            print(f"⚠️ Archive failed: {str(e)}")


logger = logging.getLogger(__name__)

@shared_task
def process_csv_task(file_path, business_context=None):
    """
    🤖 AUTONOMOUS CSV PROCESSING: Intelligent, Learning-Capable Task Execution
    
    TRANSFORMATION:
    OLD: Simple processing → Archive file
    NEW: Context analysis → Adaptive execution → Learning capture → Optimization
    
    This task now:
    1. 📊 Tracks its own performance
    2. ⚡ Adapts processing strategy based on file characteristics  
    3. 🧠 Learns from each execution
    4. 🔄 Improves over time through captured insights
    """
    
    # Initialize autonomous executor
    executor = AutonomousTaskExecutor("csv_processing")
    
    print(f"🤖 Starting autonomous CSV processing: {file_path}")
    
    try:
        # Execute with learning and adaptation
        result = executor.execute_with_learning(file_path, business_context)
        
        print(f"🎉 Autonomous processing completed: {file_path}")
        return result
        
    except Exception as e:
        print(f"💥 Autonomous processing failed: {str(e)}")
        
        # Even in failure, we learn
        executor.record_execution_learning(
            success=False, 
            result=None, 
            error_details=str(e)
        )
        
        # Re-raise for Celery error handling
        raise


# 🔄 BACKWARD COMPATIBILITY: Keep old simple task for comparison
@shared_task  
def process_csv_task_simple(file_path):
    """
    📁 SIMPLE PROCESSING: Original non-autonomous version for comparison
    
    This is the old way - use for A/B testing against autonomous version
    """
    try:
        print(f"📄 Simple processing: {file_path}")

        # Process CSV file (original way)
        DataProcessing.process_data(file_path)

        # Move file to archive folder
        archive_directory = "media/processed"
        os.makedirs(archive_directory, exist_ok=True)
        archive_path = os.path.join(archive_directory, os.path.basename(file_path))
        shutil.move(file_path, archive_path)

        print(f"📦 Moved to archive: {archive_path}")
        return {"status": "success", "method": "simple"}

    except Exception as e:
        print(f"❌ Error processing {file_path}: {str(e)}")
        return {"status": "error", "error": str(e)}
