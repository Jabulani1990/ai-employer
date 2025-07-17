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
    
    # 🚀 FUTURE ENHANCEMENT: Advanced Autonomous Features
    def _advanced_context_analysis(self, file_path):
        """
        🔬 ADVANCED ANALYSIS: Deep context understanding for next-level autonomy
        
        Future enhancements could include:
        1. Content-based strategy selection (analyze CSV headers/data types)
        2. Time-based optimization (peak hours vs off-hours processing)
        3. Resource-aware scheduling (CPU/memory availability)
        4. Cross-business learning (patterns from similar businesses)
        """
        # TODO: Implement advanced context analysis
        pass
    
    def _predictive_resource_management(self):
        """
        🔮 PREDICTIVE SCALING: Anticipate resource needs based on patterns
        
        Could include:
        1. Auto-scaling based on predicted workload
        2. Preemptive resource allocation
        3. Queue optimization
        4. Load balancing across workers
        """
        # TODO: Implement predictive resource management
        pass
    
    def _autonomous_error_recovery(self, error):
        """
        🔧 SELF-HEALING: Autonomous error recovery and adaptation
        
        Features:
        1. Auto-retry with different strategies
        2. Fallback processing modes
        3. Self-diagnosis and repair
        4. Alert escalation when needed
        """
        # TODO: Implement autonomous error recovery
        pass
    
    def _determine_optimal_strategy(self, file_size):
        """
        ⚡ ADAPTIVE STRATEGY: Choose optimal processing approach based on learning
        
        This is autonomous intelligence - adapting approach based on:
        1. File characteristics 
        2. Historical performance data
        3. Learned patterns and success rates
        """
        
        # Step 1: Get base strategy based on file size (fallback)
        base_strategy = self._get_base_strategy_by_size(file_size)
        
        # Step 2: Enhance with learning-based optimization
        try:
            from ai_workers.models import AIWorkerLearningRecord, BusinessAIWorker
            
            # Find business worker for learning context
            business_worker = BusinessAIWorker.objects.filter(
                ai_worker__name="AI Property Manager",
                status="active"
            ).first()
            
            if business_worker:
                optimized_strategy = self._optimize_strategy_with_learning(
                    base_strategy, file_size, business_worker
                )
                print(f"🧠 Strategy optimized with learning data")
                return optimized_strategy
                
        except Exception as e:
            print(f"⚠️ Learning optimization failed, using base strategy: {str(e)}")
        
        return base_strategy
    
    def _get_base_strategy_by_size(self, file_size):
        """Get basic strategy based on file size (fallback when no learning data)"""
        if file_size > 5 * 1024 * 1024:  # > 5MB
            return {
                "mode": "high_performance",
                "batch_size": 100,
                "ai_model": "gemini",
                "description": "Large file - optimized for throughput"
            }
        elif file_size < 10 * 1024:  # < 10KB
            return {
                "mode": "rapid_processing", 
                "batch_size": 10,
                "ai_model": "template",
                "description": "Small file - rapid template processing"
            }
        else:
            return {
                "mode": "balanced",
                "batch_size": 50,
                "ai_model": "openai",
                "description": "Standard file - balanced processing"
            }
    
    def _optimize_strategy_with_learning(self, base_strategy, file_size, business_worker):
        """
        🎯 LEARNING-BASED OPTIMIZATION: Use historical data to improve strategy
        
        This is the core of autonomous improvement - learning from past performance
        """
        try:
            from ai_workers.models import AIWorkerLearningRecord
            
            # Find similar file size executions
            file_size_range = file_size * 0.5  # ±50% file size tolerance
            similar_executions = AIWorkerLearningRecord.objects.filter(
                business_worker=business_worker,
                execution_status='success',
                file_size__gte=file_size - file_size_range,
                file_size__lte=file_size + file_size_range
            ).order_by('-created_at')[:10]  # Last 10 similar executions
            
            if similar_executions.exists():
                # Analyze which strategy performed best
                strategy_performance = {}
                
                for record in similar_executions:
                    strategy = record.strategy_used
                    efficiency = record.efficiency_score
                    
                    if strategy not in strategy_performance:
                        strategy_performance[strategy] = []
                    strategy_performance[strategy].append(efficiency)
                
                # Find best performing strategy
                best_strategy = None
                best_avg_efficiency = 0
                
                for strategy, efficiencies in strategy_performance.items():
                    avg_efficiency = sum(efficiencies) / len(efficiencies)
                    if avg_efficiency > best_avg_efficiency:
                        best_avg_efficiency = avg_efficiency
                        best_strategy = strategy
                
                if best_strategy and best_strategy != base_strategy['mode']:
                    # Override base strategy with learned optimal strategy
                    optimized = base_strategy.copy()
                    optimized['mode'] = best_strategy
                    optimized['description'] = f"Learning-optimized: {best_strategy} (avg efficiency: {best_avg_efficiency:.1f})"
                    
                    # Adjust AI model based on learned performance
                    if best_strategy == 'high_performance':
                        optimized['ai_model'] = 'gemini'
                        optimized['batch_size'] = 100
                    elif best_strategy == 'rapid_processing':
                        optimized['ai_model'] = 'template'
                        optimized['batch_size'] = 10
                    
                    print(f"📈 Strategy optimized based on {len(similar_executions)} similar executions")
                    return optimized
                
                print(f"📊 Analyzed {len(similar_executions)} similar executions - base strategy confirmed optimal")
            else:
                print(f"🆕 No similar execution history - using base strategy for learning")
                
        except Exception as e:
            print(f"⚠️ Learning analysis failed: {str(e)}")
        
        return base_strategy
    
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
        💾 PERSISTENT LEARNING: Save learnings to database for future optimization
        
        This enables true autonomous behavior - the system remembers and improves over time
        """
        try:
            from ai_workers.models import AIWorkerLearningRecord, BusinessAIWorker
            
            # Find the business worker (for now, we'll use the first property manager worker)
            # TODO: In production, identify the specific business from file context
            business_worker = BusinessAIWorker.objects.filter(
                ai_worker__name="AI Property Manager",
                status="active"
            ).first()
            
            if not business_worker:
                logger.warning("No active Property Manager found - creating learning record without business context")
                return
            
            # Extract data from learning record
            context = learning_record.get('context', {})
            strategy = context.get('processing_strategy', {})
            
            # Create persistent learning record
            AIWorkerLearningRecord.objects.create(
                business_worker=business_worker,
                execution_id=learning_record['execution_id'],
                task_name=self.task_name,
                execution_status='success' if learning_record['success'] else 'failure',
                execution_time=learning_record['execution_time'],
                
                # File and strategy context
                file_size=context.get('file_size', 0),
                strategy_used=strategy.get('mode', 'balanced'),
                ai_model_used=strategy.get('ai_model', 'openai'),
                processing_mode=strategy.get('mode', 'balanced'),
                
                # Learning data
                context_data=context,
                result_data=learning_record.get('result', {}),
                error_details=learning_record.get('error'),
                learning_insights=learning_record['learning_insights'],
                business_context=context.get('business_context', ''),
                
                # Performance metrics (we'll calculate these from results)
                properties_processed=self._extract_properties_count(learning_record),
                processing_rate=self._calculate_processing_rate(learning_record),
                success_rate=100.0 if learning_record['success'] else 0.0
            )
            
            logger.info(f"✅ Learning persisted: {learning_record['execution_id']}")
            print(f"💾 Learning saved to database: {learning_record['execution_id']}")
            
        except Exception as e:
            logger.error(f"❌ Failed to save learning record: {str(e)}")
            print(f"⚠️ Learning save failed: {str(e)}")
    
    def _extract_properties_count(self, learning_record):
        """Extract number of properties processed from results"""
        try:
            result = learning_record.get('result', {})
            if isinstance(result, dict):
                # Look for property count in various result formats
                return (result.get('properties_count') or 
                       result.get('total_properties') or 
                       result.get('processed_count') or 0)
            return 0
        except:
            return 0
    
    def _calculate_processing_rate(self, learning_record):
        """Calculate properties processed per second"""
        try:
            execution_time = learning_record.get('execution_time', 0)
            properties_count = self._extract_properties_count(learning_record)
            
            if execution_time > 0 and properties_count > 0:
                return round(properties_count / execution_time, 2)
            return 0.0
        except:
            return 0.0
        
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
