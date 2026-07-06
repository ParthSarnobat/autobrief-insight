import json
import os
from dotenv import load_dotenv
from mcp.mcp_server import fetch_ai_news
from utils.security import sanitize_payload

# Load environment variables globally so all agents inherit the API key immediately
load_dotenv()

class ADKAgent:
    """Base class representing the core of the ADK 2.0 Framework."""
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role

    def run(self, *args, **kwargs):
        raise NotImplementedError("Each ADK 2.0 agent must implement the run method.")

class ScoutAgent(ADKAgent):
    """
    Autonomously uses the MCP web scraper tool to gather the latest AI news.
    """
    def __init__(self):
        super().__init__(name="Scout", role="Web Scraper & Information Gatherer")
        
    def run(self) -> str:
        print(f"[{self.name}] Autonomously fetching today's AI news...")
        
        # Utilize the MCP RSS fetcher tool (no URL required)
        result_json = fetch_ai_news()
        data = json.loads(result_json)
        
        if data.get("status") == "success":
            return json.dumps(data.get("content"))
        else:
            return f"Error gathering data: {data.get('content')}"

class AnalystAgent(ADKAgent):
    """
    Takes the top 5 items and formats them into a clean, bulleted Markdown report summarizing the major events.
    """
    def __init__(self):
        super().__init__(name="Analyst", role="Data Structuring & Analysis")
        
    def run(self, scraped_json: str) -> tuple[str, str]:
        print(f"[{self.name}] Analyzing and formatting data into HTML cards...")
        
        # SYSTEM PROMPT INSTRUCTION FOR FUTURE LLM INTEGRATION:
        # DO NOT repeat the title or name of the article in your summary.
        # Jump straight into the core, high-signal technical insights.
        # Each bullet must contain unique, analytical details about what was launched or discovered.
        
        try:
            articles = json.loads(scraped_json)
            if not isinstance(articles, list):
                raise ValueError("Payload is not a valid list of articles.")
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            error_html = f"<div style='color:red; font-family: monospace;'><h3>Analysis Failed</h3><p>Error: {e}</p><pre>{tb}</pre><p>Payload:</p><pre>{scraped_json}</pre></div>"
            return error_html, f"Analysis failed: {e}"
            
        from google import genai
        from pydantic import BaseModel, Field
        import os
        from dotenv import load_dotenv
        
        # Load environment variables from .env file
        load_dotenv()
        
        class ArticleSummary(BaseModel):
            bullets: list[str] = Field(description="List of exactly 3 distinct, highly technical summary sentences.")

        class BatchSummary(BaseModel):
            summaries: list[ArticleSummary] = Field(description="List of summaries, one for each article provided, in the exact same order.")

        try:
            client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        except Exception as e:
            client = None
            print(f"Warning: Failed to initialize genai client. Ensure GEMINI_API_KEY is set. Error: {e}")

        system_instruction = (
            "You are an expert technical analyst. Read the provided article texts. "
            "Return a JSON object containing a 'summaries' array, where each item contains exactly 3 distinct, "
            "highly technical summary sentences for the corresponding article in the input order. "
            "DO NOT repeat the article title anywhere in these bullets. DO NOT use placeholder text."
        )

        if client:
            prompt = "Please analyze the following AI news articles and provide a technical summary for each:\n\n"
            for idx, article in enumerate(articles):
                prompt += f"--- Article {idx + 1} ---\n"
                prompt += f"Title: {article.get('title', '')}\n"
                prompt += f"Snippet: {article.get('snippet', '')}\n\n"
                
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    import time
                    time.sleep(2) # Small buffer
                    response = client.models.generate_content(
                        model='gemini-3.5-flash',
                        contents=prompt,
                        config={
                            'response_mime_type': 'application/json',
                            'response_schema': BatchSummary,
                            'system_instruction': system_instruction
                        }
                    )
                    text = response.text.strip()
                    if text.startswith("```json"):
                        text = text[7:]
                    if text.startswith("```"):
                        text = text[3:]
                    if text.endswith("```"):
                        text = text[:-3]
                    
                    result = json.loads(text.strip())
                    summaries = result.get('summaries', [])
                    
                    for idx, article in enumerate(articles):
                        if idx < len(summaries):
                            article['bullets'] = summaries[idx].get('bullets', [])
                        else:
                            article['bullets'] = ["Error: LLM did not return a summary for this article.", "Check API limits.", ""]
                    break # Success
                except Exception as e:
                    error_msg = str(e)
                    if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                        if attempt < max_retries - 1:
                            import re
                            wait_time = 30 # Default wait
                            match = re.search(r'retry in (\d+(?:\.\d+)?)s', error_msg)
                            if match:
                                wait_time = float(match.group(1)) + 2
                            print(f"Rate limited (429). Retrying in {wait_time:.1f}s... (Attempt {attempt + 1}/{max_retries})")
                            time.sleep(wait_time)
                            continue
                    
                    print(f"LLM Error during batch processing: {e}")
                    for article in articles:
                        article['bullets'] = ["Error parsing LLM response.", "Verify API limits.", str(e)]
                    break
        else:
            for article in articles:
                article['bullets'] = ["API Key Missing.", "Please set GEMINI_API_KEY.", "Unable to generate summaries."]

        html_content = "<div class='card-grid'>\n"
        context_analysis = "Today's AI News Report:\n\n"
        
        for idx, item in enumerate(articles, 1):
            title = item.get('title', 'AI Update')
            snippet = item.get('snippet', '')
            bullets = item.get('bullets', ['Key technical development detail one.', 'Strategic industry impact breakdown.', 'Deployment timeline and use-case analysis.'])
            url = item.get('url', '#')
            
            # Context for Interrogator: Include the raw snippet for deep insights!
            context_analysis += f"{idx}. {title}\nURL: {url}\nRaw Article Content: {snippet}\nSummarized Bullets:\n"
            
            # Build bullet list items carefully ensuring NO title repetition
            bullet_html = ""
            for bullet in bullets:
                if title.lower() in bullet.lower() and len(bullet) < len(title) + 10:
                    continue # Skip redundant title repeats
                bullet_html += f"<li class='news-bullet'>{bullet}</li>\n"
                context_analysis += f"- {bullet}\n"
            context_analysis += "\n"
            
            card = f"""
            <div class="news-card">
                <div>
                    <h3 class="news-title">{title}</h3>
                    <ul style="margin: 0 0 20px 0; padding-left: 20px; list-style-type: disc; overflow: visible !important;">
                        {bullet_html}
                    </ul>
                </div>
                <a href="{url}" target="_blank" class="news-link">Read Full Article 🔗</a>
            </div>
            """
            html_content += card
            
        html_content += "</div>"
        return html_content, context_analysis

class InterrogatorAgent(ADKAgent):
    """
    Handles follow-up chat conversations based on the compiled news context.
    Passes all incoming messages through the security utility first.
    """
    def __init__(self):
        super().__init__(name="Interrogator", role="Interactive QA & Follow-up")
        
    def run(self, user_message: str, context: str) -> str:
        print(f"[{self.name}] Securing and processing chat query...")
        
        # Security Utility Integration
        sanitized_message = sanitize_payload(user_message)
        
        if "[REDACTED" in sanitized_message:
            return f"[{self.name}] Security Alert: Your message contained restricted patterns and was redacted. Processed query: '{sanitized_message}'"
            
        from google import genai
        try:
            client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        except Exception as e:
            client = None
            print(f"Warning: Failed to initialize genai client for Chatbot. Error: {e}")
            
        if client:
            prompt = f"Context (Today's AI News):\n{context}\n\nUser query: {sanitized_message}"
            try:
                response = client.models.generate_content(
                    model='gemini-3.5-flash',
                    contents=prompt,
                    config={
                        'system_instruction': "You are the Interrogator Agent, an expert AI analyst. Use the provided context to answer the user's query accurately. When the user asks for more details about a specific article, you MUST provide a comprehensive, deep-dive analysis of at least 500 words, leveraging all available raw article text provided in the context. Do not hallucinate outside the context."
                    }
                )
                return response.text
            except Exception as e:
                return f"Error communicating with LLM: {e}"
        else:
            return "API Key Missing. Please set GEMINI_API_KEY in your .env file to use the chatbot."

def run_multi_agent_workflow(user_question: str = ""):
    print("=== Starting Autonomous ADK 2.0 Multi-Agent Workflow ===")
    
    # 1. Scout Agent retrieves data autonomously
    scout = ScoutAgent()
    scraped_data = scout.run()
    
    # 2. Analyst Agent formats it
    analyst = AnalystAgent()
    analysis_html, analysis_context = analyst.run(scraped_data)
    
    print("\n--- Analyst Output ---")
    print(analysis_context)
    
    if user_question:
        # 3. Interrogator Agent handles follow up safely
        interrogator = InterrogatorAgent()
        print(f"\n--- Follow-up Interaction ---")
        print(f"User: {user_question}")
        chat_response = interrogator.run(user_question, context=analysis_context)
        print(f"Interrogator: {chat_response}")
        return analysis_html, chat_response
        
    return analysis_html

if __name__ == "__main__":
    test_question = "Tell me more about the new models released today."
    run_multi_agent_workflow(test_question)
