import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional
import json
from anthropic import AsyncAnthropic
from ..tools.technical_analysis import TechnicalAnalysisTool
from ..tools.analysis_formatter import AnalysisFormatterTool
from ..tools.analysis_validator import AnalysisValidatorTool
from ..tools.mock_analyzer import MockAnalyzerTool
from ..tools.prompt_builder import PromptBuilderTool
from ..config import get_config_value

class ClaudeMarketAnalyzer:
    """
    Enhanced market analyzer using Claude AI with comprehensive technical analysis
    """
    
    def __init__(self, config: Optional[Dict] = None):
        if config is None:
            config = get_config_value('ai', {})
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.api_key = get_config_value('ai.claude_api_key')
        self.model = get_config_value('ai.model', 'claude-3-5-sonnet-20241022')
        self.max_tokens = get_config_value('ai.max_tokens', 3000)
        self.debug_mode = get_config_value('ai.debug_mode', False)
        
        # Initialize tools
        self.technical_analyzer = TechnicalAnalysisTool()
        self.formatter = AnalysisFormatterTool()
        self.validator = AnalysisValidatorTool()
        self.mock_analyzer = MockAnalyzerTool()
        self.prompt_builder = PromptBuilderTool()
        
        if self.debug_mode:
            self.logger.info("DEBUG MODE: Используются только fallback функции, ИИ отключен")
            self.client = None
        elif not self.api_key:
            self.logger.warning("Claude API key not found. Using mock mode.")
            self.client = None
        else:
            self.client = AsyncAnthropic(api_key=self.api_key)
    
    
    async def analyze_market(self, market_data: Dict, technical_analysis: Dict = None) -> Dict:
        """Main market analysis function with comprehensive technical analysis"""
        
        try:
            # Check for data errors
            if 'error' in market_data:
                self.logger.warning(f"Received incomplete data: {market_data.get('error')}")
                return self.mock_analyzer.create_fallback_analysis(market_data)
            
            # Use fallback analysis in debug mode or if no Claude API
            if self.debug_mode:
                self.logger.info("DEBUG MODE: Using enhanced mock analysis instead of Claude API")
                return self.mock_analyzer.create_enhanced_mock_analysis(market_data, technical_analysis)
            elif not self.client:
                self.logger.info("Using mock analysis (no Claude API key)")
                return self.mock_analyzer.create_enhanced_mock_analysis(market_data, technical_analysis)
            
            # Format comprehensive data for AI
            formatted_data = self.formatter.format_comprehensive_market_data(market_data, technical_analysis)
            prompt = self.prompt_builder.create_enhanced_analysis_prompt(formatted_data)
            
            self.logger.info(f"Sending request to Claude for analysis of {market_data.get('symbol', 'UNKNOWN')}")
            
            # Send request to Claude
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=[
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ]
            )
            
            # Extract response text
            response_text = response.content[0].text
            
            # Parse JSON response
            try:
                # Extract JSON block from response
                response_text = response_text.strip()
                
                # Look for JSON block in response
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                
                if json_start != -1 and json_end > json_start:
                    json_text = response_text[json_start:json_end]
                    analysis = json.loads(json_text)
                else:
                    # If JSON not found, try to parse entire response
                    analysis = json.loads(response_text)
                
                self.logger.info(f"Claude analysis received: {analysis.get('market_sentiment', 'unknown')} sentiment, "
                               f"confidence {analysis.get('confidence_score', 0):.2f}")
                
                # Validate and enhance analysis
                analysis = self.validator.validate_enhanced_analysis(analysis, market_data)
                return analysis
                
            except json.JSONDecodeError as e:
                self.logger.error(f"Error parsing Claude JSON response: {e}")
                self.logger.debug(f"Claude response (first 1000 chars): {response_text[:1000]}")
                return self.mock_analyzer.create_fallback_analysis(market_data)
                
        except Exception as e:
            self.logger.error(f"Error in Claude market analysis: {e}")
            return self.mock_analyzer.create_fallback_analysis(market_data)
    
    def generate_prompt_preview(self, market_data: Dict, technical_analysis: Dict = None) -> str:
        """Generate and return the full prompt that would be sent to Claude for inspection"""
        
        try:
            formatted_data = self.formatter.format_comprehensive_market_data(market_data, technical_analysis)
            if formatted_data is None:
                self.logger.error("format_comprehensive_market_data returned None")
                return "Error: Failed to format market data"
            
            prompt = self.prompt_builder.create_enhanced_analysis_prompt(formatted_data)
            if prompt is None:
                self.logger.error("create_enhanced_analysis_prompt returned None")
                return "Error: Failed to create analysis prompt"
            
            return prompt
        except Exception as e:
            self.logger.error(f"Error in generate_prompt_preview: {e}")
            return f"Error generating prompt: {e}"
