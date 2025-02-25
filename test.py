import os
import logging
from typing import List, Dict
import openai
from anthropic import Anthropic
import google.generativeai as genai

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelClient:
    def __init__(self):
        self.clients = self._initialize_clients()
        
    def _initialize_clients(self):
        """Initialize API clients for different providers"""
        return {
            "openai": openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY")),
            "anthropic": Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY")),
            "google": genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        }

    def generate_response(self, model: str, prompt: str) -> str:
        """Generate response from specified model"""
        try:
            if model.startswith("gpt"):
                response = self.clients["openai"].chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.choices[0].message.content
                
            elif model.startswith("claude"):
                response = self.clients["anthropic"].messages.create(
                    model=model,
                    max_tokens=1000,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text
                
            elif model.startswith("gemini"):
                response = genai.generate_content(
                    model=model,
                    contents=prompt
                )
                return response.text
                
        except Exception as e:
            logger.error(f"Error generating response from {model}: {str(e)}")
            return None

class ConversationOrchestrator:
    def __init__(self):
        self.model_client = ModelClient()
        self.models = [
            "gpt-4",
            "claude-3-opus-20240229",
            "gemini-pro"
        ]
        self.conversation_history = []
        
    def _format_prompt(self, original_prompt: str, history: List[Dict]) -> str:
        """Format the conversation history into a prompt"""
        history_text = "\n\n".join(
            [f"{entry['model']} response:\n{entry['response']}" 
             for entry in history]
        )
        return f"""Original prompt: {original_prompt}

Previous discussion:
{history_text}

Please respond to the original prompt while considering the previous discussion.
Your response should address both the original question and any relevant points 
made in the conversation history. Provide your most comprehensive analysis:"""

    def run_conversation(self, original_prompt: str, iterations: int = 3):
        """Run the conversation loop for specified iterations"""
        self.conversation_history = []
        
        for iteration in range(iterations):
            logger.info(f"\n=== Iteration {iteration + 1} ===")
            
            current_prompt = self._format_prompt(original_prompt, self.conversation_history)
            
            iteration_responses = []
            for model in self.models:
                response = self.model_client.generate_response(model, current_prompt)
                if response:
                    logger.info(f"\n{model} response:\n{response}")
                    iteration_responses.append({
                        "model": model,
                        "iteration": iteration + 1,
                        "response": response
                    })
            
            self.conversation_history.extend(iteration_responses)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="LLM Conversation Orchestrator")
    parser.add_argument("prompt", help="The initial prompt for the conversation")
    parser.add_argument("-i", "--iterations", type=int, default=3,
                        help="Number of conversation iterations")
    
    args = parser.parse_args()
    
    orchestrator = ConversationOrchestrator()
    orchestrator.run_conversation(args.prompt, args.iterations)