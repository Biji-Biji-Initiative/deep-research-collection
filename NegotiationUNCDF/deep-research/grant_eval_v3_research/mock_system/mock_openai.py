#!/usr/bin/env python3
"""
Mock OpenAI Client for Testing Deep Research System
Simulates OpenAI API responses without requiring actual API keys
"""

import json
import time
import random
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
from dataclasses import dataclass, field
import logging


@dataclass
class MockFile:
    """Mock OpenAI file object"""
    id: str
    object: str = "file"
    bytes: int = 0
    created_at: int = field(default_factory=lambda: int(time.time()))
    filename: str = ""
    purpose: str = "assistants"
    status: str = "processed"
    
    def model_dump(self):
        return {
            "id": self.id,
            "object": self.object,
            "bytes": self.bytes,
            "created_at": self.created_at,
            "filename": self.filename,
            "purpose": self.purpose,
            "status": self.status
        }


@dataclass
class MockVectorStore:
    """Mock OpenAI vector store object"""
    id: str
    object: str = "vector_store"
    created_at: int = field(default_factory=lambda: int(time.time()))
    name: str = ""
    usage_bytes: int = 0
    file_counts: Dict[str, int] = field(default_factory=lambda: {
        "in_progress": 0,
        "completed": 0,
        "failed": 0,
        "cancelled": 0,
        "total": 0
    })
    status: str = "completed"
    expires_after: Optional[Dict[str, Any]] = None
    expires_at: Optional[int] = None
    last_active_at: int = field(default_factory=lambda: int(time.time()))
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def model_dump(self):
        return {
            "id": self.id,
            "object": self.object,
            "created_at": self.created_at,
            "name": self.name,
            "usage_bytes": self.usage_bytes,
            "file_counts": self.file_counts,
            "status": self.status,
            "expires_after": self.expires_after,
            "expires_at": self.expires_at,
            "last_active_at": self.last_active_at,
            "metadata": self.metadata
        }


@dataclass
class MockAssistant:
    """Mock OpenAI assistant object"""
    id: str
    object: str = "assistant"
    created_at: int = field(default_factory=lambda: int(time.time()))
    name: str = ""
    description: str = ""
    model: str = "gpt-4-1106-preview"
    instructions: str = ""
    tools: List[Dict[str, Any]] = field(default_factory=list)
    tool_resources: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    top_p: float = 1.0
    temperature: float = 1.0
    response_format: str = "auto"
    
    def model_dump(self):
        return {
            "id": self.id,
            "object": self.object,
            "created_at": self.created_at,
            "name": self.name,
            "description": self.description,
            "model": self.model,
            "instructions": self.instructions,
            "tools": self.tools,
            "tool_resources": self.tool_resources,
            "metadata": self.metadata,
            "top_p": self.top_p,
            "temperature": self.temperature,
            "response_format": self.response_format
        }


@dataclass
class MockThread:
    """Mock OpenAI thread object"""
    id: str
    object: str = "thread"
    created_at: int = field(default_factory=lambda: int(time.time()))
    tool_resources: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def model_dump(self):
        return {
            "id": self.id,
            "object": self.object,
            "created_at": self.created_at,
            "tool_resources": self.tool_resources,
            "metadata": self.metadata
        }


@dataclass
class MockMessage:
    """Mock OpenAI message object"""
    id: str
    object: str = "thread.message"
    created_at: int = field(default_factory=lambda: int(time.time()))
    thread_id: str = ""
    role: str = "user"
    content: List[Dict[str, Any]] = field(default_factory=list)
    attachments: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def model_dump(self):
        return {
            "id": self.id,
            "object": self.object,
            "created_at": self.created_at,
            "thread_id": self.thread_id,
            "role": self.role,
            "content": self.content,
            "attachments": self.attachments,
            "metadata": self.metadata
        }


@dataclass
class MockRun:
    """Mock OpenAI run object"""
    id: str
    object: str = "thread.run"
    created_at: int = field(default_factory=lambda: int(time.time()))
    thread_id: str = ""
    assistant_id: str = ""
    status: str = "completed"
    required_action: Optional[Dict[str, Any]] = None
    last_error: Optional[Dict[str, Any]] = None
    expires_at: int = field(default_factory=lambda: int(time.time()) + 600)
    started_at: int = field(default_factory=lambda: int(time.time()))
    cancelled_at: Optional[int] = None
    failed_at: Optional[int] = None
    completed_at: Optional[int] = field(default_factory=lambda: int(time.time()))
    model: str = "gpt-4-1106-preview"
    instructions: str = ""
    tools: List[Dict[str, Any]] = field(default_factory=list)
    tool_resources: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    usage: Dict[str, int] = field(default_factory=lambda: {
        "prompt_tokens": random.randint(500, 2000),
        "completion_tokens": random.randint(1000, 5000),
        "total_tokens": 0
    })
    
    def __post_init__(self):
        if self.usage["total_tokens"] == 0:
            self.usage["total_tokens"] = self.usage["prompt_tokens"] + self.usage["completion_tokens"]
    
    def model_dump(self):
        return {
            "id": self.id,
            "object": self.object,
            "created_at": self.created_at,
            "thread_id": self.thread_id,
            "assistant_id": self.assistant_id,
            "status": self.status,
            "required_action": self.required_action,
            "last_error": self.last_error,
            "expires_at": self.expires_at,
            "started_at": self.started_at,
            "cancelled_at": self.cancelled_at,
            "failed_at": self.failed_at,
            "completed_at": self.completed_at,
            "model": self.model,
            "instructions": self.instructions,
            "tools": self.tools,
            "tool_resources": self.tool_resources,
            "metadata": self.metadata,
            "usage": self.usage
        }


class MockFiles:
    """Mock OpenAI Files API"""
    
    def __init__(self):
        self.uploaded_files = {}
        self.delay_multiplier = 1.0
        self.logger = logging.getLogger(f"{__name__}.MockFiles")
    
    def create(self, file: Any, purpose: str = "assistants") -> MockFile:
        """Mock file upload"""
        # Simulate upload delay
        time.sleep(random.uniform(0.5, 2.0) * self.delay_multiplier)
        
        file_id = f"file-{uuid.uuid4().hex[:24]}"
        
        # Get file info
        filename = getattr(file, 'name', 'uploaded_file.txt')
        if hasattr(file, 'read'):
            content = file.read()
            if isinstance(content, bytes):
                file_bytes = len(content)
            else:
                file_bytes = len(content.encode('utf-8'))
            # Reset file pointer if possible
            if hasattr(file, 'seek'):
                file.seek(0)
        else:
            file_bytes = random.randint(1000, 100000)
        
        mock_file = MockFile(
            id=file_id,
            filename=filename,
            purpose=purpose,
            bytes=file_bytes
        )
        
        self.uploaded_files[file_id] = mock_file
        
        self.logger.info(f"Mock uploaded file: {filename} ({file_bytes} bytes) -> {file_id}")
        
        return mock_file
    
    def retrieve(self, file_id: str) -> MockFile:
        """Retrieve file info"""
        if file_id in self.uploaded_files:
            return self.uploaded_files[file_id]
        else:
            raise Exception(f"File {file_id} not found")


class MockVectorStores:
    """Mock OpenAI Vector Stores API"""
    
    def __init__(self):
        self.vector_stores = {}
        self._file_batches = {}
        self.delay_multiplier = 1.0
        self.logger = logging.getLogger(f"{__name__}.MockVectorStores")
    
    def create(self, name: str = "", metadata: Dict[str, Any] = None, **kwargs) -> MockVectorStore:
        """Create mock vector store"""
        # Simulate creation delay
        time.sleep(random.uniform(1.0, 3.0) * self.delay_multiplier)
        
        vs_id = f"vs_{uuid.uuid4().hex[:24]}"
        
        vector_store = MockVectorStore(
            id=vs_id,
            name=name,
            metadata=metadata or {},
            usage_bytes=random.randint(1000000, 10000000)
        )
        
        self.vector_stores[vs_id] = vector_store
        
        self.logger.info(f"Mock created vector store: {name} -> {vs_id}")
        
        return vector_store
    
    def retrieve(self, vector_store_id: str) -> MockVectorStore:
        """Retrieve vector store"""
        if vector_store_id in self.vector_stores:
            return self.vector_stores[vector_store_id]
        else:
            raise Exception(f"Vector store {vector_store_id} not found")
    
    @property
    def file_batches(self):
        """Mock file batches interface"""
        return MockVectorStoreFileBatches(self)


class MockVectorStoreFileBatches:
    """Mock Vector Store File Batches API"""
    
    def __init__(self, parent):
        self.parent = parent
        self.batches = {}
        self.logger = logging.getLogger(f"{__name__}.MockVectorStoreFileBatches")
    
    def create(self, vector_store_id: str, file_ids: List[str]) -> Dict[str, Any]:
        """Create file batch"""
        # Simulate batch processing delay
        time.sleep(random.uniform(2.0, 5.0) * self.parent.delay_multiplier)
        
        batch_id = f"vsfb_{uuid.uuid4().hex[:24]}"
        
        batch = {
            "id": batch_id,
            "object": "vector_store.file_batch",
            "created_at": int(time.time()),
            "vector_store_id": vector_store_id,
            "status": "completed",
            "file_counts": {
                "in_progress": 0,
                "completed": len(file_ids),
                "failed": 0,
                "cancelled": 0,
                "total": len(file_ids)
            }
        }
        
        self.batches[batch_id] = batch
        
        # Update vector store file counts
        if vector_store_id in self.parent.vector_stores:
            vs = self.parent.vector_stores[vector_store_id]
            vs.file_counts["completed"] += len(file_ids)
            vs.file_counts["total"] += len(file_ids)
        
        self.logger.info(f"Mock created file batch: {len(file_ids)} files -> {batch_id}")
        
        return batch
    
    def retrieve(self, vector_store_id: str, batch_id: str) -> Dict[str, Any]:
        """Retrieve file batch"""
        if batch_id in self.batches:
            return self.batches[batch_id]
        else:
            raise Exception(f"File batch {batch_id} not found")


class MockAssistants:
    """Mock OpenAI Assistants API"""
    
    def __init__(self):
        self.assistants = {}
        self.delay_multiplier = 1.0
        self.logger = logging.getLogger(f"{__name__}.MockAssistants")
    
    def create(self, 
              name: str,
              instructions: str,
              model: str = "gpt-4-1106-preview",
              tools: List[Dict[str, Any]] = None,
              tool_resources: Dict[str, Any] = None,
              metadata: Dict[str, Any] = None,
              **kwargs) -> MockAssistant:
        """Create mock assistant"""
        # Simulate creation delay
        time.sleep(random.uniform(0.5, 1.5) * self.delay_multiplier)
        
        assistant_id = f"asst_{uuid.uuid4().hex[:24]}"
        
        assistant = MockAssistant(
            id=assistant_id,
            name=name,
            instructions=instructions,
            model=model,
            tools=tools or [],
            tool_resources=tool_resources or {},
            metadata=metadata or {}
        )
        
        self.assistants[assistant_id] = assistant
        
        self.logger.info(f"Mock created assistant: {name} -> {assistant_id}")
        
        return assistant
    
    def retrieve(self, assistant_id: str) -> MockAssistant:
        """Retrieve assistant"""
        if assistant_id in self.assistants:
            return self.assistants[assistant_id]
        else:
            raise Exception(f"Assistant {assistant_id} not found")


class MockThreads:
    """Mock OpenAI Threads API"""
    
    def __init__(self):
        self.threads = {}
        self._messages = {}
        self._runs = {}
        self.delay_multiplier = 1.0
        self.logger = logging.getLogger(f"{__name__}.MockThreads")
    
    def create(self, tool_resources: Dict[str, Any] = None, metadata: Dict[str, Any] = None) -> MockThread:
        """Create mock thread"""
        thread_id = f"thread_{uuid.uuid4().hex[:24]}"
        
        thread = MockThread(
            id=thread_id,
            tool_resources=tool_resources or {},
            metadata=metadata or {}
        )
        
        self.threads[thread_id] = thread
        self._messages[thread_id] = []
        
        self.logger.info(f"Mock created thread: {thread_id}")
        
        return thread
    
    def retrieve(self, thread_id: str) -> MockThread:
        """Retrieve thread"""
        if thread_id in self.threads:
            return self.threads[thread_id]
        else:
            raise Exception(f"Thread {thread_id} not found")
    
    @property
    def messages(self):
        """Mock messages interface"""
        return MockThreadMessages(self)
    
    @property
    def runs(self):
        """Mock runs interface"""
        return MockThreadRuns(self)


class MockThreadMessages:
    """Mock Thread Messages API"""
    
    def __init__(self, parent):
        self.parent = parent
        self.logger = logging.getLogger(f"{__name__}.MockThreadMessages")
    
    def create(self, thread_id: str, role: str, content: Union[str, List[Dict[str, Any]]], 
               attachments: List[Dict[str, Any]] = None, metadata: Dict[str, Any] = None) -> MockMessage:
        """Create mock message"""
        message_id = f"msg_{uuid.uuid4().hex[:24]}"
        
        # Handle content format
        if isinstance(content, str):
            content_list = [{"type": "text", "text": {"value": content, "annotations": []}}]
        else:
            content_list = content
        
        message = MockMessage(
            id=message_id,
            thread_id=thread_id,
            role=role,
            content=content_list,
            attachments=attachments or [],
            metadata=metadata or {}
        )
        
        if thread_id not in self.parent._messages:
            self.parent._messages[thread_id] = []
        
        self.parent._messages[thread_id].append(message)
        
        self.logger.info(f"Mock created message in thread {thread_id}: {role}")
        
        return message
    
    def list(self, thread_id: str, limit: int = 20, order: str = "desc") -> Dict[str, Any]:
        """List messages in thread"""
        messages = self.parent._messages.get(thread_id, [])
        
        if order == "desc":
            messages = sorted(messages, key=lambda m: m.created_at, reverse=True)
        else:
            messages = sorted(messages, key=lambda m: m.created_at)
        
        return {
            "object": "list",
            "data": messages[:limit],
            "first_id": messages[0].id if messages else None,
            "last_id": messages[min(len(messages)-1, limit-1)].id if messages else None,
            "has_more": len(messages) > limit
        }


class MockThreadRuns:
    """Mock Thread Runs API"""
    
    def __init__(self, parent):
        self.parent = parent
        self.logger = logging.getLogger(f"{__name__}.MockThreadRuns")
    
    def create(self, thread_id: str, assistant_id: str, 
               instructions: str = None, model: str = None,
               tools: List[Dict[str, Any]] = None, 
               tool_resources: Dict[str, Any] = None,
               metadata: Dict[str, Any] = None) -> MockRun:
        """Create mock run"""
        run_id = f"run_{uuid.uuid4().hex[:24]}"
        
        run = MockRun(
            id=run_id,
            thread_id=thread_id,
            assistant_id=assistant_id,
            instructions=instructions or "",
            model=model or "gpt-4-1106-preview",
            tools=tools or [],
            tool_resources=tool_resources or {},
            metadata=metadata or {}
        )
        
        if thread_id not in self.parent._runs:
            self.parent._runs[thread_id] = []
        
        self.parent._runs[thread_id].append(run)
        
        self.logger.info(f"Mock created run in thread {thread_id}: {run_id}")
        
        # Simulate assistant response
        self._simulate_assistant_response(thread_id, run_id)
        
        return run
    
    def retrieve(self, thread_id: str, run_id: str) -> MockRun:
        """Retrieve run"""
        runs = self.parent._runs.get(thread_id, [])
        for run in runs:
            if run.id == run_id:
                return run
        raise Exception(f"Run {run_id} not found in thread {thread_id}")
    
    def _simulate_assistant_response(self, thread_id: str, run_id: str):
        """Simulate assistant generating a response"""
        # Generate realistic research response
        response_content = self._generate_research_response(thread_id, run_id)
        
        # Create assistant message
        messages_api = MockThreadMessages(self.parent)
        messages_api.create(
            thread_id=thread_id,
            role="assistant",
            content=response_content
        )
        
        self.logger.info(f"Mock assistant response generated for run {run_id}")
    
    def _generate_research_response(self, thread_id: str, run_id: str) -> str:
        """Generate realistic research response based on context"""
        
        # Get the thread messages to understand context
        messages = self.parent._messages.get(thread_id, [])
        user_messages = [msg for msg in messages if msg.role == "user"]
        
        if not user_messages:
            return "I'm ready to help with your research. Please provide specific instructions."
        
        latest_message = user_messages[-1]
        user_content = ""
        if latest_message.content:
            for content_item in latest_message.content:
                if content_item.get("type") == "text":
                    user_content += content_item.get("text", {}).get("value", "")
        
        # Generate contextual response
        responses = [
            f"""Based on my analysis of the provided materials, I've identified several key insights:

## Executive Summary
The grant evaluation system demonstrates strong potential for impact in the targeted domain. Key strengths include comprehensive methodology, clear objectives, and measurable outcomes.

## Detailed Analysis

### 1. Technical Approach
- **Innovation Level**: High - introduces novel methodologies
- **Feasibility**: Well-structured implementation plan
- **Risk Assessment**: Moderate risks with clear mitigation strategies

### 2. Impact Assessment
- **Direct Benefits**: Significant improvement in evaluation accuracy
- **Stakeholder Value**: High value proposition for target users
- **Scalability**: Strong potential for broader application

### 3. Resource Allocation
- **Budget Justification**: Reasonable allocation across categories
- **Timeline**: Realistic milestones and deliverables
- **Personnel**: Appropriate expertise and capacity

## Recommendations
1. Consider expanding pilot testing scope
2. Develop comprehensive user training program
3. Establish clear success metrics and monitoring systems
4. Plan for long-term sustainability and maintenance

## Risk Mitigation
- Technical risks: Prototype validation and iterative development
- Resource risks: Contingency planning and flexible resource allocation
- Timeline risks: Agile methodology with regular checkpoints

## Conclusion
This grant proposal demonstrates strong merit and alignment with funding priorities. Recommend for approval with suggested enhancements.

*Analysis completed with comprehensive file search and detailed evaluation framework.*
""",
            f"""Research Analysis Complete - Key Findings:

## Document Analysis Summary
Processed {random.randint(15, 45)} documents totaling {random.randint(150, 500)} pages of content.

### Critical Success Factors Identified:
1. **Stakeholder Engagement**: Strong community involvement and buy-in
2. **Technical Infrastructure**: Robust system architecture with scalability
3. **Evaluation Framework**: Comprehensive metrics and assessment protocols
4. **Risk Management**: Proactive identification and mitigation strategies

### Quantitative Assessment:
- **Alignment Score**: {random.randint(85, 95)}/100
- **Feasibility Rating**: {random.randint(80, 92)}/100  
- **Impact Potential**: {random.randint(88, 96)}/100
- **Innovation Index**: {random.randint(82, 94)}/100

### Financial Analysis:
- Total Request: ${random.randint(250000, 850000):,}
- Cost per Outcome: ${random.randint(15000, 45000):,}
- ROI Projection: {random.randint(250, 450)}% over 3 years

### Implementation Timeline:
- Phase 1: Months 1-6 - Foundation and setup
- Phase 2: Months 7-18 - Core implementation  
- Phase 3: Months 19-24 - Testing and refinement
- Phase 4: Months 25-36 - Deployment and evaluation

### Key Risks and Mitigation:
1. **Technical Complexity** - Phased implementation approach
2. **Stakeholder Adoption** - Comprehensive change management
3. **Resource Constraints** - Flexible resource allocation model
4. **Timeline Pressures** - Agile development methodology

This proposal demonstrates exceptional merit with strong execution potential.
""",
            f"""Comprehensive Evaluation Report Generated

## Executive Assessment
**Overall Rating**: {random.choice(['Highly Recommended', 'Recommended', 'Conditionally Recommended'])}
**Confidence Level**: {random.randint(85, 95)}%

## Methodology Applied
- Multi-criteria decision analysis (MCDA)
- Stakeholder impact assessment  
- Financial cost-benefit analysis
- Risk probability modeling
- Comparative benchmarking

## Key Performance Indicators
| Metric | Score | Benchmark |
|--------|-------|-----------|
| Innovation | {random.randint(85, 95)} | 80+ |
| Feasibility | {random.randint(80, 92)} | 75+ |
| Impact | {random.randint(88, 96)} | 85+ |
| Sustainability | {random.randint(82, 90)} | 80+ |

## Detailed Findings

### Strengths:
- Clear articulation of problem and solution
- Strong theoretical foundation and methodology
- Experienced team with relevant expertise
- Realistic timeline and resource requirements
- Comprehensive evaluation and monitoring plan

### Areas for Enhancement:
- Expand diversity and inclusion considerations
- Strengthen long-term sustainability planning
- Enhance stakeholder engagement strategy
- Consider broader scalability opportunities

### Strategic Recommendations:
1. Pilot program validation before full implementation
2. Establish advisory board with domain experts
3. Develop comprehensive training and support materials
4. Create knowledge transfer and dissemination plan

## Conclusion
This proposal represents a high-quality submission with strong potential for meaningful impact. The research methodology is sound, the team is qualified, and the expected outcomes align well with funding priorities.

**Decision Recommendation**: APPROVE with minor revisions as noted above.
"""
        ]
        
        return random.choice(responses)


class MockOpenAI:
    """Mock OpenAI client that simulates all API functionality"""
    
    def __init__(self, api_key: str = "mock-api-key", timeout: int = 3600, delay_multiplier: float = 1.0):
        """Initialize mock client"""
        self.api_key = api_key
        self.timeout = timeout
        self.delay_multiplier = delay_multiplier
        
        # Initialize mock APIs
        self.files = MockFiles()
        self.beta = type('beta', (), {
            'vector_stores': MockVectorStores(),
            'assistants': MockAssistants(),
            'threads': MockThreads()
        })()
        
        # Set delay multiplier on all components
        self.files.delay_multiplier = delay_multiplier
        self.beta.vector_stores.delay_multiplier = delay_multiplier
        self.beta.assistants.delay_multiplier = delay_multiplier
        self.beta.threads.delay_multiplier = delay_multiplier
        
        self.logger = logging.getLogger(f"{__name__}.MockOpenAI")
        self.logger.info(f"Mock OpenAI client initialized with timeout: {timeout}s")
        
        # Track usage for realistic metrics
        self.usage_stats = {
            "total_tokens": 0,
            "total_requests": 0,
            "total_cost": 0.0,
            "start_time": time.time()
        }
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics"""
        current_time = time.time()
        duration = current_time - self.usage_stats["start_time"]
        
        return {
            **self.usage_stats,
            "session_duration": duration,
            "requests_per_minute": self.usage_stats["total_requests"] / (duration / 60) if duration > 0 else 0,
            "tokens_per_request": self.usage_stats["total_tokens"] / self.usage_stats["total_requests"] if self.usage_stats["total_requests"] > 0 else 0
        }
    
    def _update_usage_stats(self, tokens: int = 0, cost: float = 0.0):
        """Update usage statistics"""
        self.usage_stats["total_tokens"] += tokens
        self.usage_stats["total_requests"] += 1
        self.usage_stats["total_cost"] += cost


# Utility functions for testing
def simulate_api_error(error_rate: float = 0.05) -> bool:
    """Randomly simulate API errors for testing error handling"""
    return random.random() < error_rate


def simulate_network_delay(min_delay: float = 0.1, max_delay: float = 2.0):
    """Simulate network latency"""
    delay = random.uniform(min_delay, max_delay)
    time.sleep(delay)


if __name__ == "__main__":
    # Test the mock client
    logging.basicConfig(level=logging.INFO)
    
    client = MockOpenAI()
    
    # Test file upload
    from io import StringIO
    test_file = StringIO("This is a test file for mock upload")
    test_file.name = "test_document.txt"
    
    uploaded_file = client.files.create(test_file, purpose="assistants")
    print(f"Uploaded file: {uploaded_file.id}")
    
    # Test vector store creation
    vector_store = client.beta.vector_stores.create(
        name="test_store",
        metadata={"purpose": "testing"}
    )
    print(f"Created vector store: {vector_store.id}")
    
    # Test assistant creation
    assistant = client.beta.assistants.create(
        name="Test Assistant",
        instructions="You are a helpful research assistant.",
        tools=[{"type": "file_search"}]
    )
    print(f"Created assistant: {assistant.id}")
    
    # Test thread and message creation
    thread = client.beta.threads.create()
    print(f"Created thread: {thread.id}")
    
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content="Please analyze the uploaded documents."
    )
    print(f"Created message: {message.id}")
    
    # Test run creation (which generates response)
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id
    )
    print(f"Created run: {run.id}")
    
    # Check messages after run
    messages = client.beta.threads.messages.list(thread.id)
    print(f"Thread now has {len(messages['data'])} messages")
    
    # Show usage stats
    stats = client.get_usage_stats()
    print(f"Usage stats: {stats}")