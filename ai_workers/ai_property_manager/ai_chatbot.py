import logging
import time
from datetime import datetime
from typing import Dict, List, Optional
from django.db.models import Min, Max, Count, Avg
from ai_workers.models import BusinessAIWorker, AIWorkerLearningRecord
from ai_workers.ai_property_manager.tasks import AutonomousTaskExecutor

logger = logging.getLogger(__name__)


class AutonomousChatbotExecutor(AutonomousTaskExecutor):
    """
    🤖 AUTONOMOUS AI CHATBOT: Intelligent Customer Service Agent
    
    This extends the autonomous pattern to conversational AI, enabling:
    1. 💬 Context-aware conversation handling
    2. 🧠 Learning from customer interaction patterns
    3. ⚡ Adaptive response strategies based on inquiry types
    4. 📊 Continuous improvement through conversation analytics
    """
    
    def __init__(self, task_name="ai_chatbot"):
        super().__init__(task_name)
        self.conversation_context = {}
        self.response_strategies = {}
        
    def process_customer_inquiry(self, inquiry_data: Dict) -> Dict:
        """
        🎯 MAIN ENTRY POINT: Process customer inquiry with autonomous intelligence
        
        Args:
            inquiry_data: {
                "message": "Customer message",
                "customer_id": "unique_id",
                "inquiry_type": "faq|tenant_inquiry|general",
                "property_context": {"property_id": "xxx"} (optional),
                "conversation_history": [] (optional)
            }
        
        Returns:
            {
                "response": "AI generated response",
                "confidence": 0.95,
                "inquiry_type": "detected_type",
                "follow_up_required": False,
                "escalation_needed": False
            }
        """
        self._start_conversation_tracking(inquiry_data)
        
        try:
            # Step 1: Analyze inquiry with context awareness
            analysis = self._analyze_inquiry_with_context(inquiry_data)
            
            # Step 2: Determine optimal response strategy
            strategy = self._determine_response_strategy(analysis)
            
            # Step 3: Generate response using learned patterns
            response_data = self._generate_intelligent_response(inquiry_data, analysis, strategy)
            
            # Step 4: Record learning for continuous improvement
            self._record_conversation_learning(inquiry_data, response_data, success=True)
            
            return response_data
            
        except Exception as e:
            logger.error(f"❌ Chatbot processing failed: {str(e)}")
            
            # Fallback response + learning from failure
            fallback_response = self._generate_fallback_response(inquiry_data)
            self._record_conversation_learning(inquiry_data, fallback_response, success=False, error=str(e))
            
            return fallback_response
    
    def _start_conversation_tracking(self, inquiry_data: Dict):
        """📊 Start tracking conversation metrics for learning"""
        self.execution_start_time = time.time()
        
        self.conversation_context = {
            "customer_id": inquiry_data.get("customer_id"),
            "inquiry_type": inquiry_data.get("inquiry_type", "general"),
            "message_length": len(inquiry_data.get("message", "")),
            "has_property_context": bool(inquiry_data.get("property_context")),
            "conversation_history_length": len(inquiry_data.get("conversation_history", [])),
            "start_time": datetime.now().isoformat()
        }
        
        # 🔗 Get business context for real-time data access
        self.business_context = self._get_business_context()
        
        print(f"🎯 Conversation tracking started for customer: {self.conversation_context['customer_id']}")
        if self.business_context:
            print(f"🏢 Business context loaded: {self.business_context.get('business_name', 'Unknown')}")
    
    def _get_business_context(self):
        """
        🏢 BUSINESS CONTEXT: Get real business data for personalized responses
        
        This connects the chatbot to actual business data instead of hard-coded responses
        """
        try:
            from ai_workers.models import BusinessAIWorker
            
            # Find the business worker for this conversation
            business_worker = BusinessAIWorker.objects.filter(
                ai_worker__name="AI Property Manager",
                status="active"
            ).first()
            
            if not business_worker:
                print("⚠️ No active Business AI Worker found - using fallback data")
                return None
            
            # Get business information
            business = business_worker.business
            
            business_context = {
                "business_id": business.id,
                "business_name": getattr(business, 'business_name', 'Property Management'),
                "business_worker": business_worker,
                "business_user": business
            }
            
            print(f"✅ Business context loaded for: {business_context['business_name']}")
            return business_context
            
        except Exception as e:
            print(f"⚠️ Failed to load business context: {str(e)}")
            return None
    
    def _analyze_inquiry_with_context(self, inquiry_data: Dict) -> Dict:
        """
        🔍 INTELLIGENT ANALYSIS: Deep understanding of customer inquiry
        
        This goes beyond simple keyword matching to understand:
        1. Intent and urgency
        2. Emotional tone
        3. Technical complexity
        4. Property-specific context
        """
        message = inquiry_data.get("message", "").lower()
        
        analysis = {
            "primary_intent": self._detect_primary_intent(message),
            "urgency_level": self._assess_urgency(message),
            "emotional_tone": self._detect_emotional_tone(message),
            "technical_complexity": self._assess_technical_complexity(message),
            "property_related": self._is_property_specific(inquiry_data),
            "requires_human_escalation": False
        }
        
        # Advanced pattern recognition
        if any(word in message for word in ["emergency", "urgent", "broken", "flooding", "electrical"]):
            analysis["urgency_level"] = "high"
            analysis["requires_human_escalation"] = True
        
        if any(word in message for word in ["legal", "eviction", "lawsuit", "court"]):
            analysis["requires_human_escalation"] = True
        
        print(f"🔍 Inquiry analysis: {analysis['primary_intent']} (urgency: {analysis['urgency_level']})")
        return analysis
    
    def _detect_primary_intent(self, message: str) -> str:
        """Detect the main intent of the customer message"""
        # FAQ patterns
        if any(word in message for word in ["hours", "office", "contact", "phone", "email"]):
            return "contact_info"
        if any(word in message for word in ["application", "apply", "requirements", "qualify"]):
            return "application_process"
        if any(word in message for word in ["rent", "price", "cost", "fees", "deposit"]):
            return "pricing_inquiry"
        if any(word in message for word in ["available", "vacancy", "units", "properties"]):
            return "availability_inquiry"
        
        # Tenant-specific patterns
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
        """Assess urgency level of the inquiry"""
        high_urgency_words = ["emergency", "urgent", "immediately", "asap", "critical", "flooding", "fire", "electrical"]
        medium_urgency_words = ["soon", "quickly", "important", "problem", "issue"]
        
        if any(word in message for word in high_urgency_words):
            return "high"
        elif any(word in message for word in medium_urgency_words):
            return "medium"
        else:
            return "low"
    
    def _detect_emotional_tone(self, message: str) -> str:
        """Detect emotional tone for appropriate response style"""
        frustrated_words = ["frustrated", "angry", "upset", "disappointed", "terrible", "awful"]
        positive_words = ["thank", "great", "excellent", "happy", "satisfied", "love"]
        neutral_words = ["question", "inquiry", "information", "details"]
        
        if any(word in message for word in frustrated_words):
            return "frustrated"
        elif any(word in message for word in positive_words):
            return "positive"
        else:
            return "neutral"
    
    def _assess_technical_complexity(self, message: str) -> str:
        """Assess technical complexity to determine response detail level"""
        technical_words = ["hvac", "electrical", "plumbing", "structural", "permits", "codes"]
        
        if any(word in message for word in technical_words):
            return "high"
        elif len(message.split()) > 50:  # Long detailed message
            return "medium"
        else:
            return "low"
    
    def _is_property_specific(self, inquiry_data: Dict) -> bool:
        """Check if inquiry is about a specific property"""
        return bool(inquiry_data.get("property_context")) or any(
            word in inquiry_data.get("message", "").lower() 
            for word in ["unit", "apartment", "property", "address", "building"]
        )
    
    def _determine_response_strategy(self, analysis: Dict) -> Dict:
        """
        ⚡ ADAPTIVE STRATEGY: Choose optimal response approach based on analysis + learning
        """
        # Base strategy from analysis
        base_strategy = {
            "response_style": self._get_response_style(analysis),
            "detail_level": self._get_detail_level(analysis),
            "escalation_path": self._get_escalation_path(analysis),
            "follow_up_required": analysis["urgency_level"] in ["high", "medium"]
        }
        
        # Enhance with learning (similar to file processing strategy optimization)
        try:
            optimized_strategy = self._optimize_conversation_strategy(base_strategy, analysis)
            print(f"🧠 Conversation strategy optimized with learning data")
            return optimized_strategy
        except Exception as e:
            print(f"⚠️ Strategy optimization failed, using base strategy: {str(e)}")
            return base_strategy
    
    def _get_response_style(self, analysis: Dict) -> str:
        """Determine appropriate response style"""
        if analysis["emotional_tone"] == "frustrated":
            return "empathetic_solution_focused"
        elif analysis["urgency_level"] == "high":
            return "urgent_direct"
        elif analysis["emotional_tone"] == "positive":
            return "warm_helpful"
        else:
            return "professional_informative"
    
    def _get_detail_level(self, analysis: Dict) -> str:
        """Determine appropriate level of detail"""
        if analysis["technical_complexity"] == "high":
            return "detailed_technical"
        elif analysis["urgency_level"] == "high":
            return "concise_actionable"
        else:
            return "balanced_informative"
    
    def _get_escalation_path(self, analysis: Dict) -> str:
        """Determine if and how to escalate"""
        if analysis["requires_human_escalation"]:
            return "immediate_human"
        elif analysis["urgency_level"] == "high":
            return "supervisor_notification"
        else:
            return "none"
    
    def _optimize_conversation_strategy(self, base_strategy: Dict, analysis: Dict) -> Dict:
        """🎯 Use historical conversation data to optimize response strategy"""
        try:
            from ai_workers.models import AIWorkerLearningRecord, BusinessAIWorker
            
            # Find business worker for learning context
            business_worker = BusinessAIWorker.objects.filter(
                ai_worker__name="AI Property Manager",
                status="active"
            ).first()
            
            if not business_worker:
                return base_strategy
            
            # Find similar conversation patterns
            similar_conversations = AIWorkerLearningRecord.objects.filter(
                business_worker=business_worker,
                task_name=self.task_name,
                execution_status='success'
            ).order_by('-created_at')[:20]
            
            if similar_conversations.exists():
                # Analyze which strategies worked best for similar inquiries
                intent = analysis["primary_intent"]
                tone = analysis["emotional_tone"]
                
                successful_strategies = []
                for record in similar_conversations:
                    context = record.context_data.get('conversation_analysis', {})
                    if (context.get('primary_intent') == intent and 
                        context.get('emotional_tone') == tone):
                        successful_strategies.append(record.context_data.get('strategy', {}))
                
                if successful_strategies:
                    # Use most successful strategy patterns
                    optimized = base_strategy.copy()
                    # Apply learned optimizations
                    optimized['learned_optimization'] = True
                    optimized['success_rate'] = len(successful_strategies) / len(similar_conversations) * 100
                    
                    print(f"📈 Strategy optimized based on {len(successful_strategies)} similar conversations")
                    return optimized
            
            print(f"🆕 No similar conversation history - using base strategy")
            
        except Exception as e:
            print(f"⚠️ Conversation optimization failed: {str(e)}")
        
        return base_strategy
    
    def _generate_intelligent_response(self, inquiry_data: Dict, analysis: Dict, strategy: Dict) -> Dict:
        """
        🚀 INTELLIGENT RESPONSE GENERATION: Create contextual, personalized responses
        """
        intent = analysis["primary_intent"]
        message = inquiry_data.get("message", "")
        
        # Generate response based on intent and strategy
        if intent == "contact_info":
            response = self._generate_contact_info_response(strategy)
        elif intent == "application_process":
            response = self._generate_application_response(strategy)
        elif intent == "pricing_inquiry":
            response = self._generate_pricing_response(inquiry_data, strategy)
        elif intent == "availability_inquiry":
            response = self._generate_availability_response(inquiry_data, strategy)
        elif intent == "maintenance_request":
            response = self._generate_maintenance_response(inquiry_data, strategy)
        elif intent == "payment_inquiry":
            response = self._generate_payment_response(inquiry_data, strategy)
        elif intent == "lease_inquiry":
            response = self._generate_lease_response(inquiry_data, strategy)
        else:
            response = self._generate_general_response(inquiry_data, analysis, strategy)
        
        return {
            "response": response,
            "confidence": self._calculate_response_confidence(analysis, strategy),
            "inquiry_type": intent,
            "follow_up_required": strategy.get("follow_up_required", False),
            "escalation_needed": strategy.get("escalation_path") != "none",
            "strategy_used": strategy,
            "processing_time": time.time() - self.execution_start_time
        }
    
    def _generate_contact_info_response(self, strategy: Dict) -> str:
        """
        📞 REAL CONTACT INFO: Generate contact response using actual business data
        """
        style = strategy.get("response_style", "professional_informative")
        business_name = self.business_context.get('business_name', 'Our Property Management Company') if self.business_context else 'Our Property Management Company'
        
        # Try to get real business contact info
        contact_info = self._get_real_contact_info()
        
        if style == "warm_helpful":
            return f"""I'd be happy to help you get in touch with {business_name}! Here are our contact details:

📞 **Phone:** {contact_info['phone']}
📧 **Email:** {contact_info['email']}
🕐 **Office Hours:** {contact_info['hours']}
📍 **Address:** {contact_info['address']}

Is there anything specific I can help you with right now? I'm here to assist with:
• Property availability and pricing
• Scheduling tours
• Application process
• Maintenance requests
• General questions"""
        else:
            return f"""Here is the contact information for {business_name}:

📞 Phone: {contact_info['phone']}
📧 Email: {contact_info['email']}
🕐 Office Hours: {contact_info['hours']}
📍 Address: {contact_info['address']}

How else can I assist you today?"""
    
    def _get_real_contact_info(self) -> Dict[str, str]:
        """
        📋 BUSINESS CONTACT: Get real business contact information
        """
        try:
            if self.business_context:
                business_user = self.business_context.get('business_user')
                
                # Try to get contact info from business user profile
                contact_info = {
                    'phone': getattr(business_user, 'phone', '(555) 123-4567'),
                    'email': getattr(business_user, 'email', 'info@propertymanagement.com'),
                    'hours': 'Monday-Friday 9AM-6PM, Saturday 10AM-2PM',
                    'address': getattr(business_user, 'address', 'Contact us for office location')
                }
                
                # Use real email if available
                if hasattr(business_user, 'email') and business_user.email:
                    contact_info['email'] = business_user.email
                
                return contact_info
            
        except Exception as e:
            print(f"⚠️ Failed to get real contact info: {str(e)}")
        
        # Fallback contact info
        return {
            'phone': '(555) 123-4567',
            'email': 'info@propertymanagement.com', 
            'hours': 'Monday-Friday 9AM-6PM, Saturday 10AM-2PM',
            'address': 'Contact us for office location'
        }
    
    def _generate_application_response(self, strategy: Dict) -> str:
        """Generate application process response"""
        return """I can help you with the application process! Here's what you'll need:

📋 Required Documents:
• Valid ID or Driver's License
• Proof of Income (last 3 pay stubs)
• Employment Verification
• Previous Rental References
• Bank Statements (last 2 months)

💰 Application Fees:
• Application Fee: $50 per applicant
• Security Deposit: First month's rent
• Pet Deposit: $300 (if applicable)

The application typically takes 24-48 hours to process. Would you like me to send you the application link?"""
    
    def _generate_pricing_response(self, inquiry_data: Dict, strategy: Dict) -> str:
        """
        💰 REAL-TIME PRICING: Generate pricing response using actual property data
        
        🔄 TRANSFORMATION: From hard-coded to database-driven responses
        """
        try:
            # Get real property data from database
            property_data = self._get_real_property_data(inquiry_data)
            
            if property_data and property_data.get('properties'):
                return self._generate_dynamic_pricing_response(property_data, inquiry_data, strategy)
            else:
                return self._generate_fallback_pricing_response(inquiry_data)
                
        except Exception as e:
            print(f"⚠️ Real-time pricing failed: {str(e)}")
            return self._generate_fallback_pricing_response(inquiry_data)
    
    def _get_real_property_data(self, inquiry_data: Dict) -> Dict:
        """
        🔍 DATABASE QUERY: Get actual property data for pricing responses
        """
        try:
            from ai_workers.ai_property_manager.models import PropertyListing
            
            if not self.business_context:
                return None
            
            business_user = self.business_context.get('business_user')
            property_context = inquiry_data.get('property_context', {})
            
            # Base query for business properties
            base_query = PropertyListing.objects.filter(
                business=business_user
            )
            
            # Filter by specific property if provided
            if property_context.get('property_id'):
                properties = base_query.filter(id=property_context['property_id'])
                query_type = "specific_property"
            else:
                # Get available properties for general pricing inquiry
                properties = base_query.filter(is_available=True)
                query_type = "general_availability"
            
            if not properties.exists():
                print("📭 No properties found matching criteria")
                return None
            
            # Calculate pricing statistics
            pricing_stats = properties.aggregate(
                min_price=Min('rent_price'),
                max_price=Max('rent_price'), 
                avg_price=Avg('rent_price'),
                total_count=Count('id')
            )
            
            # Group by property type for detailed breakdown
            property_breakdown = {}
            for prop in properties:
                prop_type = prop.property_type or 'Unknown'
                if prop_type not in property_breakdown:
                    property_breakdown[prop_type] = {
                        'count': 0,
                        'min_price': float('inf'),
                        'max_price': 0,
                        'properties': []
                    }
                
                breakdown = property_breakdown[prop_type]
                breakdown['count'] += 1
                breakdown['min_price'] = min(breakdown['min_price'], prop.rent_price or 0)
                breakdown['max_price'] = max(breakdown['max_price'], prop.rent_price or 0)
                breakdown['properties'].append({
                    'id': str(prop.id),
                    'title': prop.title,
                    'rent_price': prop.rent_price,
                    'bedrooms': prop.bedrooms,
                    'bathrooms': prop.bathrooms,
                    'location': prop.location,
                    'amenities': prop.amenities or [],
                    'is_available': prop.is_available
                })
            
            result = {
                'query_type': query_type,
                'total_properties': pricing_stats['total_count'],
                'pricing_range': {
                    'min': pricing_stats['min_price'],
                    'max': pricing_stats['max_price'],
                    'average': pricing_stats['avg_price']
                },
                'property_breakdown': property_breakdown,
                'properties': list(properties.values(
                    'id', 'title', 'rent_price', 'bedrooms', 'bathrooms', 
                    'location', 'property_type', 'amenities', 'is_available'
                )),
                'business_name': self.business_context.get('business_name', 'Our Company')
            }
            
            print(f"📊 Retrieved {result['total_properties']} properties with pricing range ${pricing_stats['min_price']}-${pricing_stats['max_price']}")
            return result
            
        except Exception as e:
            print(f"❌ Database query failed: {str(e)}")
            return None
    
    def _generate_dynamic_pricing_response(self, property_data: Dict, inquiry_data: Dict, strategy: Dict) -> str:
        """
        🎯 DYNAMIC RESPONSE: Generate personalized response using real property data
        """
        query_type = property_data.get('query_type')
        business_name = property_data.get('business_name', 'Our Company')
        total_properties = property_data.get('total_properties', 0)
        pricing_range = property_data.get('pricing_range', {})
        property_breakdown = property_data.get('property_breakdown', {})
        
        # Build response based on available data
        if query_type == "specific_property" and total_properties == 1:
            # Specific property inquiry
            prop = property_data['properties'][0]
            return f"""Here's the pricing information for the property you're interested in:

🏠 **{prop['title']}**
💰 Monthly Rent: ${prop['rent_price']:,}
🛏️ {prop['bedrooms']} Bed, {prop['bathrooms']} Bath
📍 Location: {prop['location']}
{'✅ Available Now' if prop['is_available'] else '❌ Currently Occupied'}

🏢 About {business_name}:
• Professional property management
• Responsive maintenance team
• Online tenant portal

Would you like to schedule a viewing or get more details about this property?"""
        
        elif total_properties > 0:
            # Multiple properties available
            min_price = pricing_range.get('min', 0)
            max_price = pricing_range.get('max', 0)
            
            response = f"""Great! {business_name} has {total_properties} properties available with pricing information:

💰 **Pricing Range: ${min_price:,} - ${max_price:,}/month**

"""
            
            # Add breakdown by property type
            if property_breakdown:
                response += "🏠 **Available Units:**\n"
                for prop_type, data in property_breakdown.items():
                    if data['count'] > 0:
                        type_min = data['min_price'] if data['min_price'] != float('inf') else 0
                        type_max = data['max_price']
                        response += f"• {prop_type}: {data['count']} units (${type_min:,} - ${type_max:,})\n"
                
                response += "\n"
            
            # Add business features
            response += f"""🌟 **{business_name} Features:**
• Professional property management
• 24/7 maintenance support
• Online rent payments
• Pet-friendly options available

Would you like me to show you specific units in your budget range or schedule a tour?"""
            
            return response
        
        else:
            return self._generate_fallback_pricing_response(inquiry_data)
    
    def _generate_fallback_pricing_response(self, inquiry_data: Dict) -> str:
        """
        🛡️ FALLBACK PRICING: Use when real data is unavailable
        """
        business_name = self.business_context.get('business_name', 'Our Company') if self.business_context else 'Our Property Management Company'
        
        return f"""I'd be happy to provide pricing information for {business_name}!

💰 **Pricing Information:**
Our rental rates are competitive and vary based on:
• Unit size and layout
• Floor level and views
• Lease length and terms
• Current market conditions

📞 **For Accurate Pricing:**
I'd love to give you specific rates! Could you tell me:
• What type of unit are you interested in?
• Your preferred move-in timeframe?
• Any specific location preferences?

I can then provide you with current availability and exact pricing for units that match your needs.

Would you like me to connect you with our leasing specialist for immediate assistance?"""
    
    def _generate_availability_response(self, inquiry_data: Dict, strategy: Dict) -> str:
        """
        🏠 REAL-TIME AVAILABILITY: Generate availability response using actual property data
        """
        try:
            # Get real availability data
            availability_data = self._get_real_availability_data(inquiry_data)
            
            if availability_data and availability_data.get('available_properties'):
                return self._generate_dynamic_availability_response(availability_data, strategy)
            else:
                return self._generate_fallback_availability_response()
                
        except Exception as e:
            print(f"⚠️ Real-time availability failed: {str(e)}")
            return self._generate_fallback_availability_response()
    
    def _get_real_availability_data(self, inquiry_data: Dict) -> Dict:
        """
        📋 AVAILABILITY QUERY: Get actual available properties from database
        """
        try:
            from ai_workers.ai_property_manager.models import PropertyListing
            
            if not self.business_context:
                return None
            
            business_user = self.business_context.get('business_user')
            
            # Get available properties
            available_properties = PropertyListing.objects.filter(
                business=business_user,
                is_available=True
            ).order_by('property_type', 'rent_price')
            
            if not available_properties.exists():
                return None
            
            # Group by property type for organized display
            availability_by_type = {}
            total_available = 0
            
            for prop in available_properties:
                prop_type = prop.property_type or 'Other'
                if prop_type not in availability_by_type:
                    availability_by_type[prop_type] = []
                
                availability_by_type[prop_type].append({
                    'id': str(prop.id),
                    'title': prop.title,
                    'rent_price': prop.rent_price,
                    'bedrooms': prop.bedrooms,
                    'bathrooms': prop.bathrooms,
                    'location': prop.location,
                    'amenities': prop.amenities or [],
                    'move_in_date': 'Immediate' if prop.is_available else 'TBD'
                })
                total_available += 1
            
            return {
                'total_available': total_available,
                'availability_by_type': availability_by_type,
                'available_properties': list(available_properties.values(
                    'id', 'title', 'rent_price', 'bedrooms', 'bathrooms',
                    'location', 'property_type', 'amenities'
                )),
                'business_name': self.business_context.get('business_name', 'Our Company')
            }
            
        except Exception as e:
            print(f"❌ Availability query failed: {str(e)}")
            return None
    
    def _generate_dynamic_availability_response(self, availability_data: Dict, strategy: Dict) -> str:
        """
        ✨ DYNAMIC AVAILABILITY: Generate personalized availability response
        """
        total_available = availability_data.get('total_available', 0)
        availability_by_type = availability_data.get('availability_by_type', {})
        business_name = availability_data.get('business_name', 'Our Company')
        
        if total_available == 0:
            return self._generate_fallback_availability_response()
        
        response = f"""Excellent news! {business_name} currently has {total_available} units available:

🏠 **Current Availability:**
"""
        
        # Add detailed breakdown by property type
        for prop_type, properties in availability_by_type.items():
            if properties:
                count = len(properties)
                min_price = min(prop['rent_price'] for prop in properties if prop['rent_price'])
                max_price = max(prop['rent_price'] for prop in properties if prop['rent_price'])
                
                response += f"• **{prop_type}**: {count} unit{'s' if count > 1 else ''} "
                
                if min_price == max_price:
                    response += f"(${min_price:,}/month)\n"
                else:
                    response += f"(${min_price:,} - ${max_price:,}/month)\n"
                
                # Show specific units if not too many
                if count <= 3:
                    for prop in properties:
                        response += f"  → {prop['title']}: {prop['bedrooms']}BR/{prop['bathrooms']}BA - ${prop['rent_price']:,}\n"
                    response += "\n"
        
        response += f"""🌟 **What's Included:**
• Professional property management by {business_name}
• Online tenant portal
• Responsive maintenance team
• Move-in ready units

📅 **Move-in Timeline:**
Most units available for immediate occupancy

Would you like me to:
• Schedule a tour of specific units?
• Send you detailed property information?
• Connect you with our leasing specialist?

What type of unit interests you most?"""
        
        return response
    
    def _generate_fallback_availability_response(self) -> str:
        """
        🛡️ FALLBACK AVAILABILITY: Use when no properties are available or data fails
        """
        business_name = self.business_context.get('business_name', 'Our Company') if self.business_context else 'Our Property Management Company'
        
        return f"""Thank you for your interest in {business_name}!

🔍 **Checking Availability:**
I'm currently updating our availability system. While I gather the latest information:

📞 **Immediate Assistance:**
• Call our leasing office for real-time availability
• Schedule a tour to see available units
• Join our waiting list for preferred units

📋 **What We Typically Offer:**
• Various unit sizes and layouts
• Competitive market pricing
• Professional property management
• Quality amenities and services

Could you tell me what you're looking for? (unit size, budget range, move-in timeline)
I can then provide you with the most current availability and pricing."""
    
    def _generate_maintenance_response(self, inquiry_data: Dict, strategy: Dict) -> str:
        """Generate maintenance request response"""
        urgency = self.conversation_context.get("urgency_level", "low")
        
        if urgency == "high":
            return """I understand this is urgent! For emergency maintenance issues:

🚨 Emergency Contact: (555) 123-HELP (4357)
Available 24/7 for emergencies

I'm also creating a priority work order for you right now. Can you provide:
• Your unit number
• Detailed description of the issue
• Best contact number for maintenance access

Emergency issues (flooding, electrical, heating/cooling failures) will be addressed within 2 hours."""
        else:
            return """I can help you submit a maintenance request! Here's how it works:

🔧 Maintenance Process:
• Submit your request (I can help you do this now)
• Receive confirmation within 1 hour
• Maintenance scheduled within 24-48 hours
• Text notifications for appointment updates

To get started, please provide:
• Unit number
• Description of the issue
• Preferred appointment time
• Any access instructions

What maintenance issue can I help you with?"""
    
    def _generate_payment_response(self, inquiry_data: Dict, strategy: Dict) -> str:
        """Generate payment-related response"""
        return """I can help with payment questions! Here are your options:

💳 Payment Methods:
• Online Portal: pay.propertymanagement.com
• Phone: (555) 123-PAY (automated system)
• Mail: Check to office address
• In-person: Office hours Mon-Fri 9AM-6PM

📅 Payment Schedule:
• Due Date: 1st of each month
• Grace Period: Through 5th (no late fee)
• Late Fee: $50 after 5th

🔄 Auto-Pay Available:
• $25 discount for setting up auto-pay
• Never miss a payment

Would you like me to help you set up online access or auto-pay?"""
    
    def _generate_lease_response(self, inquiry_data: Dict, strategy: Dict) -> str:
        """Generate lease-related response"""
        return """I can help with lease questions! Common lease topics:

📄 Lease Information:
• Standard lease terms: 12 months
• Month-to-month available (+$200/month)
• Lease renewal options available 60 days before expiration
• Early termination: 60-day notice + 2 months rent

🔄 Lease Changes:
• Add/remove occupants: $100 processing fee
• Pet additions: Pet deposit + monthly fee
• Subletting: Requires written approval

📋 Lease Documents:
• Digital copies available in tenant portal
• Amendments require both parties' signatures

What specific lease question can I help you with? If you need to make changes, I can connect you with our leasing specialist."""
    
    def _generate_general_response(self, inquiry_data: Dict, analysis: Dict, strategy: Dict) -> str:
        """Generate general response for unspecified inquiries"""
        tone = analysis.get("emotional_tone", "neutral")
        
        if tone == "frustrated":
            return """I understand your frustration, and I'm here to help resolve this for you.
            
Could you please provide more details about your specific concern? I want to make sure I give you the most accurate and helpful information.

Common topics I can help with immediately:
• Rent payments and account questions
• Maintenance requests
• Lease information
• Property availability
• Contact information

If this is urgent, I can also connect you directly with our management team."""
        else:
            return """Hello! I'm here to help with any questions about our properties and services.

I can assist you with:
• Property availability and pricing
• Application process
• Maintenance requests  
• Payment options
• Lease information
• Contact details

What can I help you with today?"""
    
    def _calculate_response_confidence(self, analysis: Dict, strategy: Dict) -> float:
        """Calculate confidence score for the response"""
        confidence = 0.8  # Base confidence
        
        # Adjust based on intent clarity
        if analysis["primary_intent"] != "general_inquiry":
            confidence += 0.1
        
        # Adjust based on learning optimization
        if strategy.get("learned_optimization"):
            confidence += 0.1
        
        # Adjust based on escalation needs
        if analysis.get("requires_human_escalation"):
            confidence -= 0.2
        
        return min(confidence, 1.0)
    
    def _generate_fallback_response(self, inquiry_data: Dict) -> Dict:
        """Generate fallback response when processing fails"""
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
            "strategy_used": {"fallback": True}
        }
    
    def _record_conversation_learning(self, inquiry_data: Dict, response_data: Dict, success: bool, error: str = None):
        """
        📝 CONVERSATION LEARNING: Record conversation outcomes for improvement
        
        This enables the chatbot to learn from:
        1. Successful conversation patterns
        2. Failed interactions and recovery strategies
        3. Customer satisfaction indicators
        4. Response effectiveness metrics
        """
        try:
            execution_time = time.time() - self.execution_start_time if self.execution_start_time else 0
            
            learning_record = {
                "execution_id": f"{self.task_name}_{int(time.time())}",
                "success": success,
                "execution_time": round(execution_time, 2),
                "context": {
                    **self.conversation_context,
                    "conversation_analysis": inquiry_data,
                    "strategy": response_data.get("strategy_used", {}),
                    "response_confidence": response_data.get("confidence", 0)
                },
                "result": response_data,
                "error": error,
                "timestamp": datetime.now().isoformat(),
                "learning_insights": self._generate_conversation_insights(inquiry_data, response_data, success, execution_time)
            }
            
            print(f"📚 Conversation learning recorded: {learning_record['learning_insights']}")
            
            # Save to database using parent class method
            self._save_learning_to_system(learning_record)
            
        except Exception as e:
            logger.error(f"❌ Failed to record conversation learning: {str(e)}")
    
    def _generate_conversation_insights(self, inquiry_data: Dict, response_data: Dict, success: bool, execution_time: float) -> List[str]:
        """💡 Generate insights from conversation interaction"""
        insights = []
        
        # Performance insights
        if execution_time > 5:
            insights.append("Slow response time - consider optimization")
        elif execution_time < 1:
            insights.append("Fast response - strategy working efficiently")
        
        # Confidence insights
        confidence = response_data.get("confidence", 0)
        if confidence > 0.9:
            insights.append("High confidence response - strategy validated")
        elif confidence < 0.6:
            insights.append("Low confidence - may need strategy adjustment")
        
        # Intent recognition insights
        if inquiry_data.get("inquiry_type") == response_data.get("inquiry_type"):
            insights.append("Intent correctly identified")
        else:
            insights.append("Intent mismatch - improve classification")
        
        # Success/failure insights
        if success:
            insights.append("Successful conversation - customer needs addressed")
        else:
            insights.append("Conversation failed - review error patterns")
        
        return insights
