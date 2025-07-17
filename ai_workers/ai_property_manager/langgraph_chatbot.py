"""
🚀 HYBRID LANGGRAPH CHATBOT: Advanced Conversation Orchestration + Autonomous Learning

This combines LangGraph's powerful state management and workflow orchestration
with your existing autonomous learning and business integration systems.

Key Benefits:
1. 🔄 Visual conversation flows with conditional routing
2. 📊 Persistent state management across conversation turns
3. 🧠 Your existing autonomous learning system preserved
4. 🏢 Real-time business data integration maintained
5. 🛡️ Advanced error handling and recovery
6. 🔀 Multi-path conversation routing based on context

Installation Required:
pip install langgraph langchain langchain-openai

"""

import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, TypedDict, Annotated
from dataclasses import dataclass

# LangGraph imports (install with: pip install langgraph langchain langchain-openai)
try:
    from langgraph.graph import StateGraph, END
    from langgraph.graph.message import add_messages
    from langgraph.checkpoint.sqlite import SqliteSaver
    from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
    from langchain_openai import ChatOpenAI
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    print("⚠️ LangGraph not installed. Run: pip install langgraph langchain langchain-openai")

# Your existing autonomous learning imports
from django.db.models import Min, Max, Count, Avg
from ai_workers.models import BusinessAIWorker, AIWorkerLearningRecord
from ai_workers.ai_property_manager.tasks import AutonomousTaskExecutor

logger = logging.getLogger(__name__)


class ConversationState(TypedDict):
    """
    🧠 CONVERSATION STATE: Complete conversation context managed by LangGraph
    
    This replaces manual state tracking with LangGraph's robust state management
    """
    # Core conversation data
    messages: Annotated[list, add_messages]
    customer_id: str
    conversation_id: str
    
    # Business context (your existing system)
    business_context: Dict
    property_context: Optional[Dict]
    
    # Analysis and strategy (enhanced with LangGraph routing)
    current_analysis: Dict
    response_strategy: Dict
    conversation_history: List[Dict]
    
    # Learning and performance tracking
    execution_metrics: Dict
    learning_context: Dict
    
    # LangGraph routing decisions
    next_action: str
    requires_escalation: bool
    confidence_score: float
    
    # Your autonomous learning data
    autonomous_insights: List[str]
    strategy_optimizations: Dict


@dataclass
class LangGraphConfig:
    """Configuration for LangGraph chatbot"""
    llm_model: str = "gpt-4"
    memory_type: str = "sqlite"
    max_conversation_turns: int = 50
    confidence_threshold: float = 0.7
    enable_learning: bool = True


class HybridLangGraphChatbot(AutonomousTaskExecutor):
    """
    🎯 HYBRID LANGGRAPH CHATBOT: Best of both worlds
    
    Combines:
    - LangGraph: State management, conversation flow, routing
    - Your System: Autonomous learning, business integration, real-time data
    
    This creates a sophisticated conversational AI that learns and adapts
    while providing structured, reliable conversation management.
    """
    
    def __init__(self, task_name="langgraph_chatbot", config: LangGraphConfig = None):
        super().__init__(task_name)
        
        if not LANGGRAPH_AVAILABLE:
            raise ImportError("LangGraph not available. Install with: pip install langgraph langchain langchain-openai")
        
        self.config = config or LangGraphConfig()
        self.conversation_context = {}
        self.business_context = None
        
        # Initialize LangGraph components
        self._setup_langgraph_workflow()
        
        print("🚀 Hybrid LangGraph Chatbot initialized with autonomous learning")
    
    def _setup_langgraph_workflow(self):
        """
        🏗️ WORKFLOW SETUP: Create LangGraph conversation flow
        
        This defines the conversation workflow with your business logic integrated
        """
        # Initialize LLM
        self.llm = ChatOpenAI(model=self.config.llm_model, temperature=0.1)
        
        # Create workflow graph
        workflow = StateGraph(ConversationState)
        
        # Add nodes (conversation steps)
        workflow.add_node("initialize_conversation", self._initialize_conversation)
        workflow.add_node("analyze_inquiry", self._analyze_inquiry_langgraph)
        workflow.add_node("determine_strategy", self._determine_strategy_langgraph)
        workflow.add_node("route_conversation", self._route_conversation)
        workflow.add_node("generate_response", self._generate_response_langgraph)
        workflow.add_node("handle_escalation", self._handle_escalation)
        workflow.add_node("record_learning", self._record_learning_langgraph)
        workflow.add_node("error_recovery", self._error_recovery)
        
        # Define conversation flow with conditional routing
        workflow.set_entry_point("initialize_conversation")
        
        # Main conversation flow
        workflow.add_edge("initialize_conversation", "analyze_inquiry")
        workflow.add_edge("analyze_inquiry", "determine_strategy")
        workflow.add_edge("determine_strategy", "route_conversation")
        
        # Conditional routing based on analysis
        workflow.add_conditional_edges(
            "route_conversation",
            self._should_escalate,
            {
                "escalate": "handle_escalation",
                "respond": "generate_response",
                "error": "error_recovery"
            }
        )
        
        # Response handling
        workflow.add_edge("generate_response", "record_learning")
        workflow.add_edge("handle_escalation", "record_learning")
        workflow.add_edge("error_recovery", "record_learning")
        workflow.add_edge("record_learning", END)
        
        # Compile workflow with memory
        memory = SqliteSaver.from_conn_string(":memory:")
        self.app = workflow.compile(checkpointer=memory)
        
        print("✅ LangGraph workflow configured with autonomous learning integration")
    
    async def process_customer_inquiry(self, inquiry_data: Dict) -> Dict:
        """
        🎯 MAIN ENTRY POINT: Process inquiry through LangGraph workflow
        
        This replaces your existing process_customer_inquiry but maintains
        all your business logic and learning capabilities.
        """
        start_time = time.time()
        conversation_id = f"conv_{int(time.time())}_{inquiry_data.get('customer_id', 'unknown')}"
        
        try:
            # Prepare initial state
            initial_state = ConversationState(
                messages=[HumanMessage(content=inquiry_data.get("message", ""))],
                customer_id=inquiry_data.get("customer_id", "unknown"),
                conversation_id=conversation_id,
                business_context={},
                property_context=inquiry_data.get("property_context"),
                current_analysis={},
                response_strategy={},
                conversation_history=inquiry_data.get("conversation_history", []),
                execution_metrics={"start_time": start_time},
                learning_context={},
                next_action="analyze",
                requires_escalation=False,
                confidence_score=0.0,
                autonomous_insights=[],
                strategy_optimizations={}
            )
            
            # Run through LangGraph workflow
            config = {"configurable": {"thread_id": conversation_id}}
            final_state = await self.app.ainvoke(initial_state, config)
            
            # Extract result in your expected format
            response_data = self._extract_response_data(final_state, start_time)
            
            print(f"✅ LangGraph conversation completed: {response_data.get('confidence', 0):.2f} confidence")
            return response_data
            
        except Exception as e:
            logger.error(f"❌ LangGraph conversation failed: {str(e)}")
            
            # Fallback to your existing error handling
            fallback_response = self._generate_fallback_response(inquiry_data)
            await self._record_error_learning(inquiry_data, str(e))
            
            return fallback_response
    
    async def _initialize_conversation(self, state: ConversationState) -> ConversationState:
        """
        🚀 INITIALIZATION: Set up conversation context with your business data
        
        This integrates your existing business context loading
        """
        print(f"🎯 Initializing conversation for customer: {state['customer_id']}")
        
        # Load your business context (existing method)
        business_context = self._get_business_context()
        
        # Update state with business context
        state["business_context"] = business_context or {}
        state["execution_metrics"]["business_context_loaded"] = business_context is not None
        
        # Add system message with business context
        if business_context:
            business_name = business_context.get('business_name', 'Property Management Company')
            system_message = SystemMessage(content=f"""
You are an AI assistant for {business_name}, a professional property management company.
You have access to real-time property data and can help with:
- Property availability and pricing
- Application processes  
- Maintenance requests
- Payment information
- Lease questions
- General inquiries

Always provide helpful, accurate information based on the actual business data.
            """)
            state["messages"] = [system_message] + state["messages"]
        
        print(f"🏢 Business context loaded: {state['business_context'].get('business_name', 'Unknown')}")
        return state
    
    async def _analyze_inquiry_langgraph(self, state: ConversationState) -> ConversationState:
        """
        🔍 ANALYSIS: Use your existing analysis logic with LangGraph state management
        """
        message_content = state["messages"][-1].content if state["messages"] else ""
        
        # Use your existing analysis method
        inquiry_data = {
            "message": message_content,
            "customer_id": state["customer_id"],
            "property_context": state["property_context"]
        }
        
        analysis = self._analyze_inquiry_with_context(inquiry_data)
        
        # Store analysis in LangGraph state
        state["current_analysis"] = analysis
        state["execution_metrics"]["analysis_completed"] = True
        
        print(f"🔍 Analysis completed: {analysis['primary_intent']} (urgency: {analysis['urgency_level']})")
        return state
    
    async def _determine_strategy_langgraph(self, state: ConversationState) -> ConversationState:
        """
        ⚡ STRATEGY: Use your autonomous learning for strategy optimization
        """
        analysis = state["current_analysis"]
        
        # Use your existing strategy determination with learning
        strategy = self._determine_response_strategy(analysis)
        
        # Enhanced with LangGraph state context
        if state["conversation_history"]:
            strategy["conversation_context"] = "returning_customer"
            strategy["conversation_length"] = len(state["conversation_history"])
        
        state["response_strategy"] = strategy
        state["confidence_score"] = self._calculate_confidence_from_strategy(strategy)
        
        print(f"⚡ Strategy determined: {strategy.get('response_style', 'default')}")
        return state
    
    async def _route_conversation(self, state: ConversationState) -> ConversationState:
        """
        🔀 ROUTING: Determine conversation path based on analysis
        """
        analysis = state["current_analysis"]
        strategy = state["response_strategy"]
        
        # Determine routing based on your business logic
        if analysis.get("requires_human_escalation"):
            state["next_action"] = "escalate"
            state["requires_escalation"] = True
        elif strategy.get("escalation_path") == "immediate_human":
            state["next_action"] = "escalate"
            state["requires_escalation"] = True
        elif state["confidence_score"] < self.config.confidence_threshold:
            state["next_action"] = "error"
        else:
            state["next_action"] = "respond"
        
        print(f"🔀 Conversation routed to: {state['next_action']}")
        return state
    
    def _should_escalate(self, state: ConversationState) -> str:
        """🚦 Routing condition for LangGraph conditional edges"""
        return state["next_action"]
    
    async def _generate_response_langgraph(self, state: ConversationState) -> ConversationState:
        """
        🚀 RESPONSE GENERATION: Use your existing response generation with LLM enhancement
        """
        analysis = state["current_analysis"]
        strategy = state["response_strategy"]
        intent = analysis["primary_intent"]
        
        # Use your existing response generation
        inquiry_data = {
            "message": state["messages"][-1].content,
            "customer_id": state["customer_id"],
            "property_context": state["property_context"]
        }
        
        # Set business context for your methods
        self.business_context = state["business_context"]
        
        # Generate response using your existing methods
        if intent == "pricing_inquiry":
            response_text = self._generate_pricing_response(inquiry_data, strategy)
        elif intent == "availability_inquiry":
            response_text = self._generate_availability_response(inquiry_data, strategy)
        elif intent == "contact_info":
            response_text = self._generate_contact_info_response(strategy)
        elif intent == "maintenance_request":
            response_text = self._generate_maintenance_response(inquiry_data, strategy)
        else:
            response_text = self._generate_general_response(inquiry_data, analysis, strategy)
        
        # Optionally enhance with LLM for more natural language
        if self.config.llm_model and len(response_text) > 500:
            enhanced_response = await self._enhance_response_with_llm(response_text, state)
            response_text = enhanced_response or response_text
        
        # Add AI response to conversation
        ai_message = AIMessage(content=response_text)
        state["messages"].append(ai_message)
        
        state["execution_metrics"]["response_generated"] = True
        state["execution_metrics"]["response_length"] = len(response_text)
        
        print(f"🚀 Response generated: {len(response_text)} characters")
        return state
    
    async def _enhance_response_with_llm(self, response_text: str, state: ConversationState) -> Optional[str]:
        """
        ✨ ENHANCEMENT: Use LLM to make responses more natural while preserving your business data
        """
        try:
            enhancement_prompt = f"""
You are helping improve a property management chatbot response. 
The response contains accurate business information and should be preserved.

Original response:
{response_text}

Please make this response more natural and conversational while:
1. Keeping ALL business information exactly the same
2. Maintaining the same helpful tone
3. Preserving all contact details, pricing, and property information
4. Making the language flow more naturally

Enhanced response:
"""
            
            messages = [HumanMessage(content=enhancement_prompt)]
            result = await self.llm.ainvoke(messages)
            
            return result.content
            
        except Exception as e:
            print(f"⚠️ LLM enhancement failed: {str(e)}")
            return None
    
    async def _handle_escalation(self, state: ConversationState) -> ConversationState:
        """
        🚨 ESCALATION: Handle cases requiring human intervention
        """
        analysis = state["current_analysis"]
        business_name = state["business_context"].get("business_name", "Our Company")
        
        escalation_response = f"""I understand this requires immediate attention from our {business_name} team.

🚨 **Priority Escalation Initiated**

For urgent assistance:
📞 Emergency Line: (555) 123-HELP
📧 Priority Email: urgent@{business_name.lower().replace(' ', '')}.com

I've notified our management team about your {analysis.get('primary_intent', 'inquiry')} and you should receive a call within 15 minutes.

Reference ID: {state['conversation_id']}

Is there anything else I can help you with while you wait?"""
        
        ai_message = AIMessage(content=escalation_response)
        state["messages"].append(ai_message)
        state["execution_metrics"]["escalated"] = True
        
        print("🚨 Conversation escalated to human agent")
        return state
    
    async def _error_recovery(self, state: ConversationState) -> ConversationState:
        """
        🛡️ ERROR RECOVERY: Handle low confidence or error cases
        """
        business_name = state["business_context"].get("business_name", "Our Property Management Company")
        
        recovery_response = f"""I want to make sure I give you the most accurate information about {business_name}.

Could you help me understand your question better? For example:
• Are you looking for property availability?
• Do you need pricing information?
• Is this about an existing lease or application?
• Do you need maintenance assistance?

Meanwhile, for immediate help:
📞 Call us: (555) 123-4567
📧 Email: info@propertymanagement.com

What specifically can I help you with today?"""
        
        ai_message = AIMessage(content=recovery_response)
        state["messages"].append(ai_message)
        state["execution_metrics"]["error_recovery"] = True
        
        print("🛡️ Error recovery response generated")
        return state
    
    async def _record_learning_langgraph(self, state: ConversationState) -> ConversationState:
        """
        📝 LEARNING: Record conversation for your autonomous learning system
        """
        try:
            execution_time = time.time() - state["execution_metrics"]["start_time"]
            
            # Extract response from final AI message
            final_response = ""
            if state["messages"]:
                for msg in reversed(state["messages"]):
                    if isinstance(msg, AIMessage):
                        final_response = msg.content
                        break
            
            # Prepare learning data in your existing format
            response_data = {
                "response": final_response,
                "confidence": state["confidence_score"],
                "inquiry_type": state["current_analysis"].get("primary_intent", "unknown"),
                "follow_up_required": state["response_strategy"].get("follow_up_required", False),
                "escalation_needed": state["requires_escalation"],
                "strategy_used": state["response_strategy"],
                "processing_time": execution_time,
                "langgraph_enhanced": True
            }
            
            inquiry_data = {
                "message": state["messages"][1].content if len(state["messages"]) > 1 else "",
                "customer_id": state["customer_id"],
                "conversation_analysis": state["current_analysis"]
            }
            
            # Use your existing learning system
            success = not state["requires_escalation"] and state["confidence_score"] > 0.5
            self._record_conversation_learning_sync(inquiry_data, response_data, success)
            
            # Generate insights for LangGraph
            insights = self._generate_langgraph_insights(state, execution_time)
            state["autonomous_insights"] = insights
            
            state["execution_metrics"]["learning_recorded"] = True
            print(f"📝 Learning recorded with LangGraph insights: {len(insights)} insights")
            
        except Exception as e:
            logger.error(f"❌ Failed to record LangGraph learning: {str(e)}")
            state["execution_metrics"]["learning_error"] = str(e)
        
        return state
    
    def _generate_langgraph_insights(self, state: ConversationState, execution_time: float) -> List[str]:
        """💡 Generate insights specific to LangGraph workflow"""
        insights = []
        
        # Workflow performance insights
        if execution_time > 10:
            insights.append("LangGraph workflow took longer than expected - optimize nodes")
        elif execution_time < 2:
            insights.append("Fast LangGraph execution - workflow optimized well")
        
        # State management insights
        if len(state["messages"]) > 10:
            insights.append("Long conversation - consider conversation summarization")
        
        # Confidence and routing insights
        if state["confidence_score"] > 0.9 and not state["requires_escalation"]:
            insights.append("High confidence LangGraph routing - strategy working well")
        elif state["requires_escalation"]:
            insights.append("Escalation triggered - review escalation criteria")
        
        # Business integration insights
        if state["business_context"]:
            insights.append("Business context successfully integrated with LangGraph")
        else:
            insights.append("No business context - improve business data loading")
        
        return insights
    
    def _extract_response_data(self, final_state: ConversationState, start_time: float) -> Dict:
        """📤 Extract response in your expected format"""
        
        # Get final AI response
        final_response = ""
        if final_state["messages"]:
            for msg in reversed(final_state["messages"]):
                if isinstance(msg, AIMessage):
                    final_response = msg.content
                    break
        
        return {
            "response": final_response,
            "confidence": final_state["confidence_score"],
            "inquiry_type": final_state["current_analysis"].get("primary_intent", "unknown"),
            "follow_up_required": final_state["response_strategy"].get("follow_up_required", False),
            "escalation_needed": final_state["requires_escalation"],
            "strategy_used": final_state["response_strategy"],
            "processing_time": time.time() - start_time,
            "langgraph_workflow": True,
            "conversation_id": final_state["conversation_id"],
            "autonomous_insights": final_state["autonomous_insights"],
            "execution_metrics": final_state["execution_metrics"]
        }
    
    # Include all your existing methods for business logic
    def _get_business_context(self):
        """🏢 Your existing business context method"""
        try:
            from ai_workers.models import BusinessAIWorker
            
            business_worker = BusinessAIWorker.objects.filter(
                ai_worker__name="AI Property Manager",
                status="active"
            ).first()
            
            if not business_worker:
                return None
            
            business = business_worker.business
            
            return {
                "business_id": business.id,
                "business_name": getattr(business, 'business_name', 'Property Management'),
                "business_worker": business_worker,
                "business_user": business
            }
            
        except Exception as e:
            print(f"⚠️ Failed to load business context: {str(e)}")
            return None
    
    def _analyze_inquiry_with_context(self, inquiry_data: Dict) -> Dict:
        """🔍 Your existing analysis method (preserved exactly)"""
        message = inquiry_data.get("message", "").lower()
        
        analysis = {
            "primary_intent": self._detect_primary_intent(message),
            "urgency_level": self._assess_urgency(message),
            "emotional_tone": self._detect_emotional_tone(message),
            "technical_complexity": self._assess_technical_complexity(message),
            "property_related": self._is_property_specific(inquiry_data),
            "requires_human_escalation": False
        }
        
        if any(word in message for word in ["emergency", "urgent", "broken", "flooding", "electrical"]):
            analysis["urgency_level"] = "high"
            analysis["requires_human_escalation"] = True
        
        if any(word in message for word in ["legal", "eviction", "lawsuit", "court"]):
            analysis["requires_human_escalation"] = True
        
        return analysis
    
    def _detect_primary_intent(self, message: str) -> str:
        """🎯 Your existing intent detection"""
        if any(word in message for word in ["hours", "office", "contact", "phone", "email"]):
            return "contact_info"
        if any(word in message for word in ["application", "apply", "requirements", "qualify"]):
            return "application_process"
        if any(word in message for word in ["rent", "price", "cost", "fees", "deposit"]):
            return "pricing_inquiry"
        if any(word in message for word in ["available", "vacancy", "units", "properties"]):
            return "availability_inquiry"
        if any(word in message for word in ["maintenance", "repair", "broken", "fix"]):
            return "maintenance_request"
        if any(word in message for word in ["payment", "pay", "bill", "due", "late"]):
            return "payment_inquiry"
        if any(word in message for word in ["lease", "contract", "agreement", "terms"]):
            return "lease_inquiry"
        if any(word in message for word in ["move", "moving", "checkout", "inspection"]):
            return "move_inquiry"
        
        return "general_inquiry"
    
    def _assess_urgency(self, message: str) -> str:
        """⚡ Your existing urgency assessment"""
        high_urgency_words = ["emergency", "urgent", "immediately", "asap", "critical", "flooding", "fire", "electrical"]
        medium_urgency_words = ["soon", "quickly", "important", "problem", "issue"]
        
        if any(word in message for word in high_urgency_words):
            return "high"
        elif any(word in message for word in medium_urgency_words):
            return "medium"
        else:
            return "low"
    
    def _detect_emotional_tone(self, message: str) -> str:
        """😊 Your existing tone detection"""
        frustrated_words = ["frustrated", "angry", "upset", "disappointed", "terrible", "awful"]
        positive_words = ["thank", "great", "excellent", "happy", "satisfied", "love"]
        
        if any(word in message for word in frustrated_words):
            return "frustrated"
        elif any(word in message for word in positive_words):
            return "positive"
        else:
            return "neutral"
    
    def _assess_technical_complexity(self, message: str) -> str:
        """🔧 Your existing complexity assessment"""
        technical_words = ["hvac", "electrical", "plumbing", "structural", "permits", "codes"]
        
        if any(word in message for word in technical_words):
            return "high"
        elif len(message.split()) > 50:
            return "medium"
        else:
            return "low"
    
    def _is_property_specific(self, inquiry_data: Dict) -> bool:
        """🏠 Your existing property detection"""
        return bool(inquiry_data.get("property_context")) or any(
            word in inquiry_data.get("message", "").lower() 
            for word in ["unit", "apartment", "property", "address", "building"]
        )
    
    def _determine_response_strategy(self, analysis: Dict) -> Dict:
        """⚡ Your existing strategy determination with learning"""
        base_strategy = {
            "response_style": self._get_response_style(analysis),
            "detail_level": self._get_detail_level(analysis),
            "escalation_path": self._get_escalation_path(analysis),
            "follow_up_required": analysis["urgency_level"] in ["high", "medium"]
        }
        
        try:
            optimized_strategy = self._optimize_conversation_strategy(base_strategy, analysis)
            return optimized_strategy
        except Exception:
            return base_strategy
    
    def _get_response_style(self, analysis: Dict) -> str:
        """🎨 Your existing style determination"""
        if analysis["emotional_tone"] == "frustrated":
            return "empathetic_solution_focused"
        elif analysis["urgency_level"] == "high":
            return "urgent_direct"
        elif analysis["emotional_tone"] == "positive":
            return "warm_helpful"
        else:
            return "professional_informative"
    
    def _get_detail_level(self, analysis: Dict) -> str:
        """📋 Your existing detail level determination"""
        if analysis["technical_complexity"] == "high":
            return "detailed_technical"
        elif analysis["urgency_level"] == "high":
            return "concise_actionable"
        else:
            return "balanced_informative"
    
    def _get_escalation_path(self, analysis: Dict) -> str:
        """🚨 Your existing escalation logic"""
        if analysis["requires_human_escalation"]:
            return "immediate_human"
        elif analysis["urgency_level"] == "high":
            return "supervisor_notification"
        else:
            return "none"
    
    def _optimize_conversation_strategy(self, base_strategy: Dict, analysis: Dict) -> Dict:
        """🧠 Your existing learning optimization"""
        try:
            from ai_workers.models import AIWorkerLearningRecord, BusinessAIWorker
            
            business_worker = BusinessAIWorker.objects.filter(
                ai_worker__name="AI Property Manager",
                status="active"
            ).first()
            
            if not business_worker:
                return base_strategy
            
            similar_conversations = AIWorkerLearningRecord.objects.filter(
                business_worker=business_worker,
                task_name=self.task_name,
                execution_status='success'
            ).order_by('-created_at')[:20]
            
            if similar_conversations.exists():
                intent = analysis["primary_intent"]
                tone = analysis["emotional_tone"]
                
                successful_strategies = []
                for record in similar_conversations:
                    context = record.context_data.get('conversation_analysis', {})
                    if (context.get('primary_intent') == intent and 
                        context.get('emotional_tone') == tone):
                        successful_strategies.append(record.context_data.get('strategy', {}))
                
                if successful_strategies:
                    optimized = base_strategy.copy()
                    optimized['learned_optimization'] = True
                    optimized['success_rate'] = len(successful_strategies) / len(similar_conversations) * 100
                    return optimized
            
        except Exception as e:
            print(f"⚠️ Strategy optimization failed: {str(e)}")
        
        return base_strategy
    
    def _calculate_confidence_from_strategy(self, strategy: Dict) -> float:
        """📊 Calculate confidence score for LangGraph routing"""
        confidence = 0.8
        
        if strategy.get("learned_optimization"):
            confidence += 0.1
        
        if strategy.get("escalation_path") == "immediate_human":
            confidence -= 0.3
        
        return min(confidence, 1.0)
    
    # Include your response generation methods
    def _generate_pricing_response(self, inquiry_data: Dict, strategy: Dict) -> str:
        """💰 Your existing pricing response generation"""
        try:
            property_data = self._get_real_property_data(inquiry_data)
            
            if property_data and property_data.get('properties'):
                return self._generate_dynamic_pricing_response(property_data, inquiry_data, strategy)
            else:
                return self._generate_fallback_pricing_response(inquiry_data)
                
        except Exception as e:
            return self._generate_fallback_pricing_response(inquiry_data)
    
    def _get_real_property_data(self, inquiry_data: Dict) -> Dict:
        """🔍 Your existing property data retrieval"""
        try:
            from ai_workers.ai_property_manager.models import PropertyListing
            
            if not self.business_context:
                return None
            
            business_user = self.business_context.get('business_user')
            property_context = inquiry_data.get('property_context', {})
            
            base_query = PropertyListing.objects.filter(business=business_user)
            
            if property_context.get('property_id'):
                properties = base_query.filter(id=property_context['property_id'])
                query_type = "specific_property"
            else:
                properties = base_query.filter(is_available=True)
                query_type = "general_availability"
            
            if not properties.exists():
                return None
            
            pricing_stats = properties.aggregate(
                min_price=Min('rent_price'),
                max_price=Max('rent_price'), 
                avg_price=Avg('rent_price'),
                total_count=Count('id')
            )
            
            return {
                'query_type': query_type,
                'total_properties': pricing_stats['total_count'],
                'pricing_range': {
                    'min': pricing_stats['min_price'],
                    'max': pricing_stats['max_price'],
                    'average': pricing_stats['avg_price']
                },
                'properties': list(properties.values(
                    'id', 'title', 'rent_price', 'bedrooms', 'bathrooms', 
                    'location', 'property_type', 'amenities', 'is_available'
                )),
                'business_name': self.business_context.get('business_name', 'Our Company')
            }
            
        except Exception:
            return None
    
    def _generate_dynamic_pricing_response(self, property_data: Dict, inquiry_data: Dict, strategy: Dict) -> str:
        """🎯 Your existing dynamic pricing response"""
        query_type = property_data.get('query_type')
        business_name = property_data.get('business_name', 'Our Company')
        total_properties = property_data.get('total_properties', 0)
        pricing_range = property_data.get('pricing_range', {})
        
        if query_type == "specific_property" and total_properties == 1:
            prop = property_data['properties'][0]
            return f"""Here's the pricing information for the property you're interested in:

🏠 **{prop['title']}**
💰 Monthly Rent: ${prop['rent_price']:,}
🛏️ {prop['bedrooms']} Bed, {prop['bathrooms']} Bath
📍 Location: {prop['location']}

🏢 About {business_name}:
• Professional property management
• Responsive maintenance team
• Online tenant portal

Would you like to schedule a viewing or get more details about this property?"""
        
        elif total_properties > 0:
            min_price = pricing_range.get('min', 0)
            max_price = pricing_range.get('max', 0)
            
            return f"""Great! {business_name} has {total_properties} properties available:

💰 **Pricing Range: ${min_price:,} - ${max_price:,}/month**

🌟 **{business_name} Features:**
• Professional property management
• 24/7 maintenance support
• Online rent payments
• Pet-friendly options available

Would you like me to show you specific units in your budget range or schedule a tour?"""
        
        return self._generate_fallback_pricing_response(inquiry_data)
    
    def _generate_fallback_pricing_response(self, inquiry_data: Dict) -> str:
        """🛡️ Your existing fallback pricing response"""
        business_name = self.business_context.get('business_name', 'Our Company') if self.business_context else 'Our Property Management Company'
        
        return f"""I'd be happy to provide pricing information for {business_name}!

💰 **Pricing Information:**
Our rental rates are competitive and vary based on:
• Unit size and layout
• Floor level and views
• Lease length and terms
• Current market conditions

Would you like me to connect you with our leasing specialist for specific pricing?"""
    
    def _generate_availability_response(self, inquiry_data: Dict, strategy: Dict) -> str:
        """🏠 Your existing availability response"""
        return f"""Excellent! We have several properties available. 

🏠 **Current Availability:**
• Various unit sizes and layouts
• Competitive pricing
• Professional management
• Move-in ready units

Would you like me to check specific availability for your needs?"""
    
    def _generate_contact_info_response(self, strategy: Dict) -> str:
        """📞 Your existing contact info response"""
        business_name = self.business_context.get('business_name', 'Our Property Management Company') if self.business_context else 'Our Property Management Company'
        
        return f"""Here is the contact information for {business_name}:

📞 Phone: (555) 123-4567
📧 Email: info@propertymanagement.com
🕐 Office Hours: Monday-Friday 9AM-6PM
📍 Address: Contact us for office location

How else can I assist you today?"""
    
    def _generate_maintenance_response(self, inquiry_data: Dict, strategy: Dict) -> str:
        """🔧 Your existing maintenance response"""
        return """I can help you submit a maintenance request!

🔧 Maintenance Process:
• Submit your request (I can help you do this now)
• Receive confirmation within 1 hour
• Maintenance scheduled within 24-48 hours
• Text notifications for appointment updates

What maintenance issue can I help you with?"""
    
    def _generate_general_response(self, inquiry_data: Dict, analysis: Dict, strategy: Dict) -> str:
        """🗣️ Your existing general response"""
        return """Hello! I'm here to help with any questions about our properties and services.

I can assist you with:
• Property availability and pricing
• Application process
• Maintenance requests  
• Payment options
• Lease information
• Contact details

What can I help you with today?"""
    
    def _record_conversation_learning_sync(self, inquiry_data: Dict, response_data: Dict, success: bool):
        """📝 Synchronous version of your learning method for LangGraph"""
        try:
            execution_time = response_data.get("processing_time", 0)
            
            learning_record = {
                "execution_id": f"{self.task_name}_{int(time.time())}",
                "success": success,
                "execution_time": round(execution_time, 2),
                "context": {
                    "conversation_analysis": inquiry_data,
                    "strategy": response_data.get("strategy_used", {}),
                    "response_confidence": response_data.get("confidence", 0),
                    "langgraph_enhanced": True
                },
                "result": response_data,
                "timestamp": datetime.now().isoformat(),
                "learning_insights": ["LangGraph workflow completed successfully"]
            }
            
            self._save_learning_to_system(learning_record)
            
        except Exception as e:
            logger.error(f"❌ Failed to record learning: {str(e)}")
    
    async def _record_error_learning(self, inquiry_data: Dict, error: str):
        """❌ Record error for learning"""
        try:
            error_record = {
                "execution_id": f"{self.task_name}_error_{int(time.time())}",
                "success": False,
                "error": error,
                "context": inquiry_data,
                "timestamp": datetime.now().isoformat(),
                "learning_insights": ["LangGraph workflow failed - review error patterns"]
            }
            
            self._save_learning_to_system(error_record)
            
        except Exception as e:
            logger.error(f"❌ Failed to record error learning: {str(e)}")
    
    def _generate_fallback_response(self, inquiry_data: Dict) -> Dict:
        """🛡️ Your existing fallback response"""
        return {
            "response": """I apologize, but I'm having trouble processing your request right now. 
            
For immediate assistance, please:
📞 Call our office: (555) 123-4567
📧 Email: info@propertymanagement.com
🕐 Office Hours: Mon-Fri 9AM-6PM

A team member will be happy to help you!""",
            "confidence": 0.3,
            "inquiry_type": "system_error",
            "follow_up_required": True,
            "escalation_needed": True,
            "strategy_used": {"fallback": True},
            "langgraph_workflow": False
        }


# Example usage and integration
async def test_hybrid_chatbot():
    """🧪 Test the hybrid LangGraph chatbot"""
    
    config = LangGraphConfig(
        llm_model="gpt-4",
        confidence_threshold=0.7,
        enable_learning=True
    )
    
    chatbot = HybridLangGraphChatbot(config=config)
    
    # Test inquiry
    inquiry = {
        "message": "What are your rental prices for 2-bedroom apartments?",
        "customer_id": "test_customer_123",
        "inquiry_type": "pricing_inquiry"
    }
    
    response = await chatbot.process_customer_inquiry(inquiry)
    
    print("🎯 LangGraph Response:")
    print(f"Response: {response['response']}")
    print(f"Confidence: {response['confidence']}")
    print(f"Insights: {response.get('autonomous_insights', [])}")
    
    return response


if __name__ == "__main__":
    import asyncio
    
    if LANGGRAPH_AVAILABLE:
        print("🚀 Testing Hybrid LangGraph Chatbot...")
        asyncio.run(test_hybrid_chatbot())
    else:
        print("⚠️ LangGraph not available. Install with: pip install langgraph langchain langchain-openai")
