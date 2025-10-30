"""
tools/llm_wrapper.py
Unified LLM interface using Groq for fast inference
"""


from groq import Groq
import json
import os
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv
import time
import re


class LLMWrapper:
    """
     Unified interface for LLM operations using Groq
     Supports multiple models with automatic fallback
    """
    # Available Groq models (in order of preference)
    MODELS = {
        'best': 'llama-3.1-70b-versatile',     # Highest quality
        'fast': 'llama-3.1-8b-instant',        # Fastest
        'reasoning': 'mixtral-8x7b-32768',     # Good for analysis
        'efficient': 'gemma-7b-it'             # Most efficient
    }

    def __init__(self, api_key: Optional[str] = None, model: str = 'best'):

         """
        Initialize Groq client
        
        Args:
            api_key: Groq API key (or loads from .env)
            model: Model preference ('best', 'fast', 'reasoning', 'efficient')
        """
         
         # Load environment variables
         load_dotenv()

          # Get API key
         self.api_key = api_key or os.getenv("GROQ_API_KEY")

         if not self.api_key:
            raise ValueError(
                "GROQ_API_KEY not found! "
                "Set it in .env file or pass as parameter. "
                "Get free key: https://console.groq.com/keys"
            )
         
          # Initialize client
         self.client = Groq(api_key=self.api_key)

          # Set model
         self.model = self.MODELS.get(model, self.MODELS['best'])
        
         # Stats tracking
         self.total_tokens = 0
         self.total_calls = 0
         self.total_errors = 0
        
         print(f"✅ Groq LLM initialized with model: {self.model}")

    
    def generate(
        self, 
        prompt: str, 
        max_tokens: int = 1000,
        temperature: float = 0.7, # This parameter is used to make the output midly creative
        system_prompt: Optional[str] = None
    ) -> str:
          """
        Generate text response
        
        Args:
            prompt: User prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0-1.0)
            system_prompt: Optional system instruction
        
        Returns:
            Generated text
        """
          
          try:
            # Build messages
            messages = []
            
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            
            messages.append({
                "role": "user",
                "content": prompt
            })

             # Call Groq API
            start_time = time.time()
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=0.95
            )
            
            elapsed = time.time() - start_time
            
            # Extract response
            result = response.choices[0].message.content
            
            # Update stats
            self.total_tokens += response.usage.total_tokens
            self.total_calls += 1
            
            print(f"✅ LLM call completed in {elapsed:.2f}s ({response.usage.total_tokens} tokens)")
            
            return result

          except Exception as e:
            self.total_errors += 1
            print(f"❌ LLM error: {e}")
            raise  
        
    def generate_structured(
        self,
        prompt: str,
        schema: Dict[str, Any],
        max_tokens: int = 2000,
        temperature: float = 0.3
    ) -> Dict[str, Any]:    
        """
        Generate JSON response matching a schema
        
        Args:
            prompt: User prompt
            schema: Expected JSON schema
            max_tokens: Maximum tokens
            temperature: Lower for more deterministic JSON
        
        Returns:
            Parsed JSON object
        """
        # Add JSON instruction to prompt
        schema_str = json.dumps(schema, indent=2)
        
        full_prompt = f"""{prompt}

IMPORTANT: Respond with ONLY valid JSON matching this schema:
{schema_str}

Do not include any explanation or markdown formatting.

Return pure JSON that can be parsed directly."""
        
        system_prompt = "You are a precise JSON generator. Always return valid JSON with no additional text."
        
        # Generate response
        response_text = self.generate(
            prompt=full_prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            system_prompt=system_prompt
        )
        
        # Parse JSON
        try:
            # Try direct parse
            return json.loads(response_text)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code blocks
            json_match = re.search(r'```json\s*\n(.*?)\n```', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            
            # Try to find JSON object in text
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            
            # If all fails, raise error
            raise ValueError(f"Could not parse JSON from response: {response_text[:200]}")
        
    
    def generate_with_retry(
        self,
        prompt: str,
        max_retries: int = 3,
        **kwargs
    ) -> str:
        """
        Generate with automatic retry on failure
        
        Args:
            prompt: User prompt
            max_retries: Maximum retry attempts
            **kwargs: Additional arguments for generate()
        
        Returns:
            Generated text
        """
        last_error = None
        
        for attempt in range(max_retries):
            try:
                return self.generate(prompt, **kwargs)
            except Exception as e:
                last_error = e
                print(f"⚠️ Attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
        
        raise last_error
    
    def batch_generate(
        self,
        prompts: List[str],
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> List[str]:
        """
        Generate responses for multiple prompts
        
        Args:
            prompts: List of prompts
            max_tokens: Max tokens per response
            temperature: Sampling temperature
        
        Returns:
            List of responses
        """
        results = []
        
        for i, prompt in enumerate(prompts):
            print(f"Processing prompt {i + 1}/{len(prompts)}...")
            
            try:
                response = self.generate(
                    prompt=prompt,
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                results.append(response)
            except Exception as e:
                print(f"❌ Prompt {i + 1} failed: {e}")
                results.append(None)
            
            # Rate limiting (30 req/min = 2 sec between calls)
            if i < len(prompts) - 1:
                time.sleep(2)
        
        return results
    
    def count_tokens(self, text: str) -> int:
        """
        Estimate token count (rough approximation)
        
        Args:
            text: Input text
        
        Returns:
            Estimated token count
        """
        # Rough estimate: 1 token ≈ 4 characters
        return len(text) // 4
    
    def get_stats(self) -> Dict[str, Any]:
        """Get usage statistics"""
        return {
            'total_calls': self.total_calls,
            'total_tokens': self.total_tokens,
            'total_errors': self.total_errors,
            'model': self.model,
            'avg_tokens_per_call': self.total_tokens / max(self.total_calls, 1)
        }
    
    def reset_stats(self):
        """Reset usage statistics"""
        self.total_tokens = 0
        self.total_calls = 0
        self.total_errors = 0

# ==================== HELPER FUNCTIONS ====================

def create_llm(model: str = 'best', api_key: Optional[str] = None) -> LLMWrapper:
    """
    Convenience function to create LLM wrapper
    
    Args:
        model: Model preference
        api_key: Optional API key
    
    Returns:
        LLMWrapper instance
    """
    return LLMWrapper(api_key=api_key, model=model)


# ==================== DEMO & TESTING ====================

def demo_llm():
    """Demonstrate LLM wrapper functionality"""
    
    print("="*60)
    print("🤖 GROQ LLM WRAPPER DEMO")
    print("="*60)
    print()
    
    # Initialize LLM
    llm = LLMWrapper(model='fast')  # Use fast model for demo

     # Test 1: Simple generation
    print("\n📝 Test 1: Simple Text Generation")
    print("-" * 60)
    response = llm.generate(
        prompt="Explain what a research paper abstract is in one sentence.",
        max_tokens=100,
        temperature=0.7
    )
    print(f"Response: {response}")
    
    # Test 2: Structured JSON generation
    print("\n📊 Test 2: Structured JSON Output")
    print("-" * 60)

    schema = {
        "title": "string",
        "summary": "string",
        "key_points": ["string", "string", "string"]
    }
    
    json_response = llm.generate_structured(
        prompt="Summarize what makes a good research paper in 3 key points.",
        schema=schema,
        temperature=0.3
    )
    print(json.dumps(json_response, indent=2))
    
    # Test 3: Batch generation
    print("\n🔄 Test 3: Batch Processing")
    print("-" * 60)


    prompts = [
        "Name one benefit of peer review.",
        "Name one challenge in academic publishing.",
        "Name one trend in AI research."
    ]
    
    batch_results = llm.batch_generate(prompts, max_tokens=50)
    for i, result in enumerate(batch_results, 1):
        print(f"{i}. {result}")
    
    # Show stats
    print("\n📈 Usage Statistics")
    print("-" * 60)
    stats = llm.get_stats()
    print(json.dumps(stats, indent=2))
    
    print("\n✅ Demo complete!")


if __name__ == "__main__":
    demo_llm()