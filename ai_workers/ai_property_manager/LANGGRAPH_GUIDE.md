# 🚀 HYBRID LANGGRAPH CHATBOT: Installation & Usage Guide

## 📦 Installation

### Core Dependencies (Required)
Your existing Django setup already has these covered.

### LangGraph Dependencies (Optional - for enhanced features)
```bash
# Install in your virtual environment
pip install langgraph langchain langchain-openai

# Or add to your requirements.txt:
# langgraph>=0.1.0
# langchain>=0.1.0
# langchain-openai>=0.1.0
```

### Environment Variables (For LLM features)
```bash
# Add to your .env file
OPENAI_API_KEY=your_openai_api_key_here
```

## 🎯 Usage

### 1. Check Chatbot Status
```bash
GET /api/ai-property-manager/chatbot/status/
```

Response:
```json
{
    "chatbots": {
        "original": {
            "available": true,
            "features": ["Autonomous learning", "Business context integration", "Real-time property data"]
        },
        "langgraph": {
            "available": true,
            "features": ["Advanced conversation flow", "State management", "LLM enhancement"]
        }
    },
    "recommendation": {
        "simple_inquiries": "original",
        "complex_conversations": "langgraph"
    }
}
```

### 2. Use Hybrid Chatbot (Main Endpoint)
```bash
POST /api/ai-property-manager/chatbot/inquiry/
Content-Type: application/json
```

Request:
```json
{
    "message": "What are your rental prices for 2-bedroom apartments?",
    "customer_id": "customer_123",
    "chatbot_type": "auto",  // "original", "langgraph", or "auto"
    "inquiry_type": "pricing_inquiry",
    "property_context": {
        "property_id": "optional"
    },
    "conversation_history": []
}
```

Response:
```json
{
    "response": "Great! We have several 2-bedroom apartments available...",
    "confidence": 0.95,
    "inquiry_type": "pricing_inquiry",
    "follow_up_required": false,
    "escalation_needed": false,
    "chatbot_used": "langgraph (auto-selected)",
    "selection_reason": "Complex conversation detected",
    "langgraph_enhanced": true,
    "autonomous_insights": ["High confidence response - strategy validated"],
    "processing_time": 2.3
}
```

### 3. Compare Both Chatbots (A/B Testing)
```bash
POST /api/ai-property-manager/chatbot/compare/
Content-Type: application/json
```

Response:
```json
{
    "original": {
        "response": {...},
        "processing_time": 1.2,
        "available": true
    },
    "langgraph": {
        "response": {...},
        "processing_time": 2.1,
        "available": true
    },
    "comparison": {
        "confidence_difference": 0.15,
        "time_difference": 0.9,
        "recommendation": "langgraph"
    }
}
```

### 4. Use Original Chatbot (Backward Compatibility)
```bash
POST /api/ai-property-manager/chatbot/original/inquiry/
```

## 🔄 Migration Strategy

### Phase 1: Install and Test (Current)
1. Keep using your original chatbot
2. Install LangGraph dependencies when ready
3. Test new features with `/compare/` endpoint

### Phase 2: Gradual Adoption
1. Use `chatbot_type: "auto"` for intelligent routing
2. Monitor performance with analytics
3. Adjust based on results

### Phase 3: Full Enhancement (Future)
1. Switch to LangGraph for complex scenarios
2. Keep original for high-volume simple queries
3. Optimize based on learning data

## 🎛️ Configuration Options

### LangGraph Config
```python
{
    "llm_model": "gpt-4",  // or "gpt-3.5-turbo"
    "confidence_threshold": 0.7,
    "max_conversation_turns": 50,
    "enable_learning": true
}
```

### Auto-Selection Logic
- **Use LangGraph for:**
  - Long conversations (>3 turns)
  - Complex messages (>20 words)
  - Keywords: "complex", "detailed", "explain"

- **Use Original for:**
  - Simple, direct questions
  - High-volume scenarios
  - When LangGraph unavailable

## 📊 Benefits Comparison

| Feature | Original Chatbot | LangGraph Enhanced |
|---------|------------------|-------------------|
| Response Speed | ⚡ Very Fast | 🔄 Moderate |
| Conversation Flow | ✅ Good | 🚀 Excellent |
| State Management | ✅ Basic | 🧠 Advanced |
| Learning System | ✅ Full | ✅ Full + Enhanced |
| Business Integration | ✅ Complete | ✅ Complete |
| Multi-turn Conversations | ✅ Good | 🚀 Excellent |
| Error Recovery | ✅ Good | 🛡️ Advanced |
| Visual Debugging | ❌ No | 🔍 Yes |
| LLM Enhancement | ❌ No | ✨ Yes |

## 🚨 Troubleshooting

### LangGraph Not Available
```json
{
    "error": "Dependencies not installed: pip install langgraph langchain langchain-openai"
}
```

**Solution:** Install dependencies or use `chatbot_type: "original"`

### OpenAI API Key Missing
```json
{
    "error": "OpenAI API key not configured"
}
```

**Solution:** Set `OPENAI_API_KEY` environment variable

### Slow Response Times
- Use `chatbot_type: "original"` for faster responses
- Configure lower `confidence_threshold`
- Monitor with `/status/` endpoint

## 🧪 Testing Commands

### Test Original Chatbot
```bash
curl -X POST http://localhost:8000/api/ai-property-manager/chatbot/original/inquiry/ \
-H "Content-Type: application/json" \
-d '{"message": "What are your office hours?", "customer_id": "test_123"}'
```

### Test LangGraph Chatbot
```bash
curl -X POST http://localhost:8000/api/ai-property-manager/chatbot/inquiry/ \
-H "Content-Type: application/json" \
-d '{"message": "What are your office hours?", "customer_id": "test_123", "chatbot_type": "langgraph"}'
```

### Check Status
```bash
curl -X GET http://localhost:8000/api/ai-property-manager/chatbot/status/
```

## 📈 Performance Monitoring

Both chatbots include comprehensive learning and analytics:

- ✅ Autonomous learning preserved
- ✅ Business context integration maintained  
- ✅ Real-time property data access
- ✅ Performance tracking enhanced
- ✅ Conversation flow optimization (LangGraph)
- ✅ Advanced error handling (LangGraph)
