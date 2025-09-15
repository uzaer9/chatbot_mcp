
# import asyncio
# import json
# from typing import List, Dict, Any, Optional
# from mcp import ClientSession, StdioServerParameters
# from mcp.client.stdio import stdio_client
# import google.generativeai as genai
# from app.config import config
# from utils.logger import get_logger

# logger = get_logger("mcp_client")

# # Global variables to maintain connection
# _read_stream = None
# _write_stream = None
# _session = None
# _context_manager = None

# class SoccerMCPClient:
#     """MCP Client for soccer analytics with visualization support"""
    
#     def __init__(self):
#         self.session: Optional[ClientSession] = None
#         self.tools: List[Dict] = []
#         self.messages: List[Dict] = []
#         self.last_tool_result = None  # Store last tool result for visualization
#         # *** UPDATED *** - Added to accumulate multiple tool results for comparisons
#         self.accumulated_tool_results = []  # Store multiple tool results
        
#         # Configure Gemini
#         genai.configure(api_key=config.GEMINI_API_KEY)
#         self.model = genai.GenerativeModel('gemini-2.0-flash')
        
#         logger.info("SoccerMCPClient initialized with visualization support")
    
#     async def connect_to_server(self) -> bool:
#         """Connect to the MCP soccer server"""
#         global _read_stream, _write_stream, _session, _context_manager
        
#         try:
#             logger.info(f"Connecting to MCP server: {config.MCP_SERVER_PATH}")
            
#             server_params = StdioServerParameters(
#                 command="python",
#                 args=["-u", config.MCP_SERVER_PATH],
#             )
            
#             # Create the context manager but don't exit it
#             _context_manager = stdio_client(server_params)
#             _read_stream, _write_stream = await _context_manager.__aenter__()
            
#             # Create session
#             _session = ClientSession(_read_stream, _write_stream)
#             await _session.__aenter__()
#             self.session = _session
            
#             # Initialize
#             await self.session.initialize()
            
#             # Get tools
#             tools_result = await self.session.list_tools()
#             self.tools = [
#                 {
#                     "name": tool.name,
#                     "description": getattr(tool, 'description', ''),
#                     "parameters": getattr(tool, 'inputSchema', {})
#                 }
#                 for tool in tools_result.tools
#             ]
            
#             logger.info(f"Connected! Tools: {len(self.tools)}")
#             return True
                    
#         except Exception as e:
#             logger.error(f"Connection failed: {e}")
#             return False
    
#     def format_tools_for_gemini(self) -> str:
#         """Format MCP tools for Gemini context"""
#         tools_context = "Available Soccer Data Tools:\n"
#         for tool in self.tools:
#             tools_context += f"- {tool['name']}: {tool['description']}\n"
        
#         tools_context += "\nTo use a tool, respond with JSON in this format:\n"
#         tools_context += '{"tool_call": {"name": "tool_name", "parameters": {...}}}\n'
#         tools_context += "\nIf no tool is needed, respond normally.\n"
        
#         return tools_context
    
#     def enhance_response_with_data(self, original_response: str, tool_result: Dict) -> str:
#         """Enhance response to include properly formatted JSON for visualization"""
        
#         # Add the raw JSON data at the end of the response for visualization parsing
#         enhanced_response = original_response + "\n\n"
#         enhanced_response += f"```json\n{json.dumps(tool_result, indent=2)}\n```"
        
#         return enhanced_response
    
#     # *** UPDATED *** - Enhanced to suggest multiple tool calls for comparisons
#     async def call_gemini(self, query: str) -> str:
#         """Call Gemini API with tool context"""
#         try:
#             # Build system prompt focused on data retrieval
#             tool_instructions = """
# AVAILABLE SOCCER LEAGUES:
# - "Big 5 European Leagues Combined"
# - "ENG-Premier League" 
# - "ESP-La Liga"
# - "FRA-Ligue 1"
# - "GER-Bundesliga"
# - "INT-European Championship"
# - "INT-Women's World Cup"
# - "INT-World Cup"
# - "ITA-Serie A"

# TOOL PARAMETER SPECIFICATIONS:

# For get_player_season_stats_filtered:
# - league_id: League from above list (e.g., "ESP-La Liga", "ENG-Premier League")
# - season: Format "XXYY" where XX is start year last 2 digits, YY is end year (e.g., "0506" for 2005-06, "2223" for 2022-23)
# - stat_type: Choose from "standard", "shooting", "passing", "defense", "possession", "misc" (default: "standard")
# - player: Player name 
# - team: Team name (optional)

# For read_team_season_stats:
# - leagues: League ID from above list
# - seasons: Format "XXYY" (e.g., "2223" for 2022-23)
# - stat_type: Choose from "standard", "shooting", "passing", "passing_types", "goal_shot_creation", "defense", "possession", "misc"
# - opponent_stats: true or false (default: false)
# - team_name: Team to filter
# - filters: Dictionary of additional filters

# CRITICAL RULES:
# - Season format is ALWAYS "XXYY" (2223 = 2022-23, 0910 = 2009-10, 1213 = 2012-13)
# - League IDs must be EXACTLY as listed above
# - Boolean values must be lowercase: true or false
# - For comparison queries asking about multiple players, call the tool once for EACH player separately
# - Focus on retrieving accurate data
# """

#             system_prompt = f"""You are a soccer analytics expert focused on data retrieval and analysis.

# {self.format_tools_for_gemini()}

# {tool_instructions}

# User Query: {query}

# RESPONSE PROTOCOL:
# 1. If user asks about data, use appropriate tool with exact parameters
# 2. For comparison queries mentioning multiple players, you need to call the tool separately for each player
# 3. Provide comprehensive data analysis in your response
# 4. Include clear statistics and insights
# 5. For conversational queries, respond normally

# Focus on accurate data retrieval and clear analysis."""

#             response = self.model.generate_content(system_prompt)
#             return response.text
            
#         except Exception as e:
#             logger.error(f"Gemini API call failed: {e}")
#             return f"Error calling Gemini API: {e}"
    
#     async def execute_tool(self, tool_name: str, parameters: Dict) -> Dict:
#         """Execute an MCP tool"""
#         try:
#             if not self.session:
#                 return {"error": "MCP session not connected"}
            
#             logger.info(f"Executing tool: {tool_name} with params: {parameters}")
            
#             result = await self.session.call_tool(tool_name, parameters)
            
#             if hasattr(result, 'isError') and result.isError:
#                 return {"error": f"Tool execution failed: {result.content}"}
            
#             # Parse the result
#             if hasattr(result, 'content') and result.content:
#                 if isinstance(result.content, list) and result.content:
#                     content = result.content[0]
#                     if hasattr(content, 'text'):
#                         tool_result = content.text
#                     else:
#                         tool_result = str(content)
#                 else:
#                     tool_result = str(result.content)
#             else:
#                 tool_result = "{}"
            
#             try:
#                 parsed_result = json.loads(tool_result)
                
#                 # Log data structure for potential visualization
#                 if isinstance(parsed_result, dict) and "players" in parsed_result:
#                     players_count = len(parsed_result.get("players", []))
#                     logger.info(f"Retrieved {players_count} player records")
#                 elif isinstance(parsed_result, list):
#                     logger.info(f"Retrieved {len(parsed_result)} records")
                
#                 return parsed_result
#             except json.JSONDecodeError:
#                 return {"data": tool_result}
                
#         except Exception as e:
#             logger.error(f"Tool execution error: {e}")
#             return {"error": str(e)}
    
#     def parse_gemini_response(self, response: str) -> tuple[bool, Optional[Dict], str]:
#         """Parse Gemini response for tool calls"""
#         try:
#             if "tool_call" in response and "{" in response:
#                 start = response.find("{")
#                 if start >= 0:
#                     brace_count = 0
#                     end = start
#                     for i, char in enumerate(response[start:], start):
#                         if char == '{':
#                             brace_count += 1
#                         elif char == '}':
#                             brace_count -= 1
#                         if brace_count == 0:
#                             end = i + 1
#                             break
                
#                 if end > start:
#                     json_str = response[start:end]
#                     tool_data = json.loads(json_str)
                    
#                     if "tool_call" in tool_data:
#                         return True, tool_data["tool_call"], ""
            
#             return False, None, response
            
#         except Exception as e:
#             logger.warning(f"Failed to parse tool call: {e}")
#             return False, None, response
    
#     def format_sse_event(self, event_type: str, data: dict) -> str:
#         """Format data as SSE event"""
#         return f"data: {json.dumps({'type': event_type, **data})}\n\n"
    
#     async def process_query_stream(self, query: str):
#         """Process query with streaming updates and visualization support"""
#         try:
#             logger.info(f"Processing streaming query: {query}")
            
#             # *** UPDATED *** - Reset accumulated results for new query
#             self.accumulated_tool_results = []
            
#             # Connection check
#             if not self.session:
#                 yield self.format_sse_event("status", {
#                     "status": "initializing",
#                     "message": "🚀 Starting soccer data server..."
#                 })
                
#                 connected = await self.connect_to_server()
#                 if not connected:
#                     yield self.format_sse_event("error", {
#                         "message": "❌ Failed to connect to soccer data server"
#                     })
#                     return
                
#                 yield self.format_sse_event("status", {
#                     "status": "connected", 
#                     "message": "✅ Soccer server connected"
#                 })
            
#             # AI Analysis
#             yield self.format_sse_event("status", {
#                 "status": "thinking",
#                 "message": "🤖 AI analyzing query..."
#             })
            
#             self.messages.append({"role": "user", "content": query})
            
#             max_iterations = 5
#             iteration = 0
            
#             while iteration < max_iterations:
#                 iteration += 1
                
#                 gemini_response = await self.call_gemini(query)
#                 logger.info(f"Gemini response (iteration {iteration}): {gemini_response[:1000]}...")
                
#                 is_tool_call, tool_data, text_response = self.parse_gemini_response(gemini_response)
                
#                 if is_tool_call and tool_data:
#                     tool_name = tool_data.get("name", "unknown").replace("soccerdata-mcp:", "")
#                     yield self.format_sse_event("status", {
#                         "status": "tool_detected",
#                         "message": f"🎯 AI determined need for {tool_name.replace('_', ' ')}"
#                     })
                    
#                     yield self.format_sse_event("status", {
#                         "status": "fetching",
#                         "message": "⚽ Fetching soccer data..."
#                     })
                    
#                     tool_result = await self.execute_tool(
#                         tool_data.get("name", ""),
#                         tool_data.get("parameters", {})
#                     )
                    
#                     yield self.format_sse_event("status", {
#                         "status": "processing",
#                         "message": "📊 Processing soccer statistics..."
#                     })
                    
#                     # Enhanced context for next iteration
#                     tool_context = f"""Tool {tool_data['name']} returned: {json.dumps(tool_result, indent=2)}

# Please provide a comprehensive answer based on this data."""
                    
#                     query = f"{query}\n\nTool Result: {tool_context}"
                    
#                     # *** UPDATED *** - Accumulate tool results for comparison visualization
#                     if tool_result and 'players' in tool_result:
#                         self.accumulated_tool_results.extend(tool_result['players'])
#                         # Create combined result for visualization
#                         combined_result = {'players': self.accumulated_tool_results}
#                     else:
#                         combined_result = tool_result

#                     self.last_tool_result = combined_result
                    
#                     logger.info(f"Tool executed successfully: {tool_data['name']}")
                    
#                 else:
#                     # Stream response
#                     yield self.format_sse_event("status", {
#                         "status": "generating",
#                         "message": "✏️ Generating response..."
#                     })
                    
#                     # *** UPDATED *** - Enhanced response with accumulated data
#                     # Enhance response with JSON data for visualization if tool was used
#                     if hasattr(self, 'last_tool_result') and self.last_tool_result:
#                         enhanced_response = self.enhance_response_with_data(text_response, self.last_tool_result)
#                         # Clear the stored results
#                         self.last_tool_result = None
#                         self.accumulated_tool_results = []
#                     else:
#                         enhanced_response = text_response
                    
#                     # Stream response in chunks
#                     words = enhanced_response.split()
#                     chunk_size = 3
                    
#                     for i in range(0, len(words), chunk_size):
#                         chunk_words = words[i:i+chunk_size]
#                         chunk = " ".join(chunk_words)
#                         if i > 0:
#                             chunk = " " + chunk
                        
#                         yield self.format_sse_event("content", {"chunk": chunk})
                    
#                     self.messages.append({"role": "assistant", "content": enhanced_response})
#                     return
            
#             yield self.format_sse_event("error", {
#                 "message": "Maximum iterations reached. Please try a simpler query."
#             })
            
#         except Exception as e:
#             logger.error(f"Streaming query processing error: {e}")
#             yield self.format_sse_event("error", {
#                 "message": f"Error processing query: {e}"
#             })
    
#     async def process_query(self, query: str) -> str:
#         """Process a user query with tool calling support"""
#         try:
#             logger.info(f"Processing query: {query}")
            
#             # *** UPDATED *** - Reset for new query
#             self.accumulated_tool_results = []
            
#             if not self.session:
#                 connected = await self.connect_to_server()
#                 if not connected:
#                     return "Failed to connect to soccer data server. Please try again."
            
#             self.messages.append({"role": "user", "content": query})
            
#             max_iterations = 3
#             iteration = 0
            
#             while iteration < max_iterations:
#                 iteration += 1
                
#                 gemini_response = await self.call_gemini(query)
#                 logger.info(f"Gemini response (iteration {iteration}): {gemini_response[:200]}...")
                
#                 is_tool_call, tool_data, text_response = self.parse_gemini_response(gemini_response)
                
#                 if is_tool_call and tool_data:
#                     tool_result = await self.execute_tool(
#                         tool_data.get("name", ""),
#                         tool_data.get("parameters", {})
#                     )
                    
#                     tool_context = f"""Tool {tool_data['name']} returned: {json.dumps(tool_result, indent=2)}
                    
# Please provide a comprehensive answer based on this data."""
                    
#                     query = f"{query}\n\nTool Result: {tool_context}"
                    
#                     # *** UPDATED *** - Accumulate results
#                     if tool_result and 'players' in tool_result:
#                         self.accumulated_tool_results.extend(tool_result['players'])
#                         combined_result = {'players': self.accumulated_tool_results}
#                     else:
#                         combined_result = tool_result
                    
#                     self.last_tool_result = combined_result
                    
#                     logger.info(f"Tool executed successfully: {tool_data['name']}")
                    
#                 else:
#                     # Enhance response with data if available
#                     if hasattr(self, 'last_tool_result') and self.last_tool_result:
#                         enhanced_response = self.enhance_response_with_data(text_response, self.last_tool_result)
#                         self.last_tool_result = None
#                         self.accumulated_tool_results = []
#                     else:
#                         enhanced_response = text_response
                    
#                     self.messages.append({"role": "assistant", "content": enhanced_response})
#                     return enhanced_response
            
#             return "Maximum iterations reached. Please try a simpler query."
            
#         except Exception as e:
#             logger.error(f"Query processing error: {e}")
#             return f"Error processing query: {e}"
    
#     async def get_available_leagues(self) -> List[str]:
#         """Get available leagues for frontend"""
#         try:
#             result = await self.execute_tool("available_leagues", {})
#             if "leagues" in result:
#                 return result["leagues"]
#             return []
#         except:
#             return []
    
#     async def cleanup(self):
#         """Cleanup resources"""
#         global _read_stream, _write_stream, _session, _context_manager
        
#         if _session:
#             try:
#                 await _session.__aexit__(None, None, None)
#             except:
#                 pass
        
#         if _context_manager:
#             try:
#                 await _context_manager.__aexit__(None, None, None)
#             except:
#                 pass
        
#         _session = None
#         _read_stream = None
#         _write_stream = None
#         _context_manager = None
#         self.session = None
#         logger.info("MCP session closed")

import asyncio
import json
import re
from typing import List, Dict, Any, Optional
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import google.generativeai as genai
from app.config import config
from utils.logger import get_logger

logger = get_logger("mcp_client")

# Global variables to maintain connection
_read_stream = None
_write_stream = None
_session = None
_context_manager = None

class SoccerMCPClient:
    """Multi-tool MCP Client with intelligent visualization data filtering"""
    
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.tools: List[Dict] = []
        self.messages: List[Dict] = []
        self.last_tool_result = None
        self.accumulated_tool_results = {
            'players': [],
            'teams': [],
            'shots': [],
            'matches': []
        }
        
        # Configure Gemini
        genai.configure(api_key=config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        
        logger.info("Multi-tool SoccerMCPClient initialized with visualization filtering")
    
    async def connect_to_server(self) -> bool:
        """Connect to the MCP soccer server"""
        global _read_stream, _write_stream, _session, _context_manager
        
        try:
            logger.info(f"Connecting to MCP server: {config.MCP_SERVER_PATH}")
            
            server_params = StdioServerParameters(
                command="python",
                args=["-u", config.MCP_SERVER_PATH],
            )
            
            _context_manager = stdio_client(server_params)
            _read_stream, _write_stream = await _context_manager.__aenter__()
            
            _session = ClientSession(_read_stream, _write_stream)
            await _session.__aenter__()
            self.session = _session
            
            await self.session.initialize()
            
            tools_result = await self.session.list_tools()
            self.tools = [
                {
                    "name": tool.name,
                    "description": getattr(tool, 'description', ''),
                    "parameters": getattr(tool, 'inputSchema', {})
                }
                for tool in tools_result.tools
            ]
            
            logger.info(f"Connected! Tools: {len(self.tools)}")
            return True
                    
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return False
    
    def format_tools_for_gemini(self) -> str:
        """Format MCP tools for Gemini context"""
        tools_context = "Available Soccer Data Tools:\n"
        for tool in self.tools:
            tools_context += f"- {tool['name']}: {tool['description']}\n"
        
        tools_context += "\nTo use a tool, respond with JSON in this format:\n"
        tools_context += '{"tool_call": {"name": "tool_name", "parameters": {...}}}\n'
        tools_context += "\nIf no tool is needed, respond normally.\n"
        
        return tools_context
    
    def enhance_response_with_data(self, original_response: str, tool_result: Dict) -> str:
        """Enhance response to include properly formatted JSON for visualization"""
        enhanced_response = original_response + "\n\n"
        enhanced_response += f"```json\n{json.dumps(tool_result, indent=2)}\n```"
        return enhanced_response
    
    def detect_data_type(self, tool_result: Dict) -> str:
        """Detect the type of data returned by tools"""
        if 'players' in tool_result:
            return 'player_stats'
        elif any(key in tool_result for key in ['team', 'teams']) or any(key in str(tool_result) for key in ['Pts', 'GF', 'GA']):
            return 'team_stats'  
        elif 'shots' in tool_result or 'total_shots' in tool_result:
            return 'shot_data'
        elif any(key in tool_result for key in ['schedule', 'matches']) or 'Home' in str(tool_result):
            return 'match_data'
        else:
            return 'unknown'
    
    
    async def extract_visualization_data(self, raw_data: Dict, original_query: str, data_type: str) -> Dict:
        """Enhanced visualization data extraction for multiple tool types"""
        
        logger.info(f"=== MULTI-TOOL VISUALIZATION EXTRACTION START ===")
        logger.info(f"Original query: {original_query}")
        logger.info(f"Detected data type: {data_type}")
        logger.info(f"Raw data being sent for filtering: {json.dumps(raw_data, indent=2)}")
        
        visualization_prompt = f"""You are a data analyst extracting visualization data from soccer statistics across multiple data types.

ORIGINAL USER QUERY: {original_query}

RAW DATA RETRIEVED: {json.dumps(raw_data, indent=2)}

DETECTED DATA TYPE: {data_type}

TASK: Extract ONLY the data fields needed for visualization based on the user's query and data type.

VISUALIZATION PARAMETERS BY DATA TYPE:

PLAYER STATS - Include these fields only:
- player, (player name)
- Performance,Gls (goals)
- Performance,Ast (assists) 
- Playing Time,MP (matches played)
- Performance,CrdY (yellow cards)
- Per 90 Minutes,Gls (goals per 90)
- Per 90 Minutes,Ast (assists per 90)
EXCLUDE: Playing Time,Min (minutes) - clutters bar charts

TEAM STATS - Include these fields only:
- team (team name)
- Pts (points)
- W (wins)
- D (draws) 
- L (losses)
- GF (goals for)
- GA (goals against)
- GD (goal difference)

SHOT DATA - Include these fields only:
- player (if player analysis)
- team (if team analysis)  
- outcome_counts
- shot_totals

MATCH DATA - Include these fields only:
- date
- home_team
- away_team
- result
- score

CHART TYPE RECOMMENDATIONS:
- Single entity: Bar chart + Pie chart for breakdowns
- Multiple entities: Bar chart comparison + Data table
- Distribution data: Pie chart for percentages
- Goals/Assists: Pie chart showing contribution split

RULES:
1. Remove cluttering fields (like minutes for players)
2. Focus on key performance metrics
3. Enable both bar charts and pie charts
4. Keep data clean and minimal

Extract visualization data (respond with JSON only):"""

        try:
            logger.info("Sending multi-tool data to Gemini for visualization filtering...")
            response = self.model.generate_content(visualization_prompt)
            
            logger.info(f"Gemini's multi-tool extraction response: {response.text}")
            
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                extracted_data = json.loads(json_match.group())
                
                logger.info(f"Extracted visualization data: {json.dumps(extracted_data, indent=2)}")
                logger.info(f"=== MULTI-TOOL VISUALIZATION EXTRACTION SUCCESS ===")
                
                return extracted_data
            
            logger.warning("No JSON found in multi-tool extraction response, using raw data")
            return raw_data
            
        except Exception as e:
            logger.error(f"Multi-tool visualization extraction failed: {e}")
            return raw_data
    
    def should_extract_viz_data(self, query: str) -> bool:
        """Check if query needs visualization data extraction"""
        viz_keywords = ['visualize', 'chart', 'graph', 'compare', 'show', 'plot', 'pie']
        has_viz_keyword = any(keyword in query.lower() for keyword in viz_keywords)
        logger.info(f"Checking if query needs viz extraction. Keywords found: {has_viz_keyword}")
        return has_viz_keyword
    
    async def call_gemini(self, query: str) -> str:
        """Call Gemini API with enhanced multi-tool context"""
        try:
            tool_instructions = """
AVAILABLE SOCCER LEAGUES:
- "Big 5 European Leagues Combined"
- "ENG-Premier League" 
- "ESP-La Liga"
- "FRA-Ligue 1"
- "GER-Bundesliga"
- "INT-European Championship"
- "INT-Women's World Cup"
- "INT-World Cup"
- "ITA-Serie A"

MULTI-TOOL CAPABILITIES:

1. PLAYER ANALYSIS - get_player_season_stats_filtered:
- league_id: League from above list
- season: Format "XXYY" (e.g., "2223" for 2022-23)
- stat_type: "standard", "shooting", "passing", "defense", "possession", "misc"
- player: Player name
- team: Team name (optional)

2. TEAM ANALYSIS - read_team_season_stats:
- leagues: League ID from above list
- seasons: Format "XXYY"
- stat_type: "standard", "shooting", "passing_types", etc.
- team_name: Team to filter
- filters: Additional filters

3. SHOT ANALYSIS - read_shot_events_filtered:
- leagues: League ID
- seasons: Format "XXYY"
- team: Team name (optional)
- player: Player name (optional)
- outcome: Shot outcome filter (optional)

4. MATCH ANALYSIS - read_schedule:
- leagues: League ID
- seasons: Format "XXYY"

CRITICAL RULES:
- Season format is ALWAYS "XXYY" (2223 = 2022-23, 0910 = 2009-10)
- For multi-entity queries, call appropriate tools for each entity
- Choose the right tool based on what user is asking for
- Player stats → get_player_season_stats_filtered
- Team performance → read_team_season_stats
- Shot analysis → read_shot_events_filtered
- Match data → read_schedule
"""

            system_prompt = f"""You are a multi-tool soccer analytics expert focused on data retrieval across different data types.

{self.format_tools_for_gemini()}

{tool_instructions}

User Query: {query}

RESPONSE PROTOCOL:
1. Analyze what type of data the user needs (player, team, shots, matches)
2. Choose the appropriate tool for each data type
3. For comparisons, call tools separately for each entity
4. Provide comprehensive analysis based on retrieved data

Focus on accurate tool selection and data retrieval."""

            response = self.model.generate_content(system_prompt)
            return response.text
            
        except Exception as e:
            logger.error(f"Gemini API call failed: {e}")
            return f"Error calling Gemini API: {e}"
    
    async def execute_tool(self, tool_name: str, parameters: Dict) -> Dict:
        """Execute an MCP tool with multi-tool logging"""
        try:
            if not self.session:
                return {"error": "MCP session not connected"}
            
            logger.info(f"Executing multi-tool: {tool_name} with params: {parameters}")
            
            result = await self.session.call_tool(tool_name, parameters)
            
            if hasattr(result, 'isError') and result.isError:
                return {"error": f"Tool execution failed: {result.content}"}
            
            if hasattr(result, 'content') and result.content:
                if isinstance(result.content, list) and result.content:
                    content = result.content[0]
                    if hasattr(content, 'text'):
                        tool_result = content.text
                    else:
                        tool_result = str(content)
                else:
                    tool_result = str(result.content)
            else:
                tool_result = "{}"
            
            try:
                parsed_result = json.loads(tool_result)
                
                # Log multi-tool data structure
                data_type = self.detect_data_type(parsed_result)
                logger.info(f"Tool {tool_name} returned {data_type} data")
                
                if isinstance(parsed_result, dict) and "players" in parsed_result:
                    players_count = len(parsed_result.get("players", []))
                    logger.info(f"Retrieved {players_count} player records")
                elif isinstance(parsed_result, list):
                    logger.info(f"Retrieved {len(parsed_result)} records")
                
                return parsed_result
            except json.JSONDecodeError:
                return {"data": tool_result}
                
        except Exception as e:
            logger.error(f"Multi-tool execution error: {e}")
            return {"error": str(e)}
    
    def parse_gemini_response(self, response: str) -> tuple[bool, Optional[Dict], str]:
        """Parse Gemini response for tool calls"""
        try:
            if "tool_call" in response and "{" in response:
                start = response.find("{")
                if start >= 0:
                    brace_count = 0
                    end = start
                    for i, char in enumerate(response[start:], start):
                        if char == '{':
                            brace_count += 1
                        elif char == '}':
                            brace_count -= 1
                        if brace_count == 0:
                            end = i + 1
                            break
                
                if end > start:
                    json_str = response[start:end]
                    tool_data = json.loads(json_str)
                    
                    if "tool_call" in tool_data:
                        return True, tool_data["tool_call"], ""
            
            return False, None, response
            
        except Exception as e:
            logger.warning(f"Failed to parse tool call: {e}")
            return False, None, response
    
    def format_sse_event(self, event_type: str, data: dict) -> str:
        """Format data as SSE event"""
        return f"data: {json.dumps({'type': event_type, **data})}\n\n"
    
    async def process_query_stream(self, query: str):
        """Process query with multi-tool support and intelligent visualization filtering"""
        try:
            logger.info(f"Processing multi-tool streaming query: {query}")
            
            # Reset accumulated results for new query
            for key in self.accumulated_tool_results:
                self.accumulated_tool_results[key] = []
            
            # Connection check
            if not self.session:
                yield self.format_sse_event("status", {
                    "status": "initializing",
                    "message": "🚀 Starting multi-tool soccer data server..."
                })
                
                connected = await self.connect_to_server()
                if not connected:
                    yield self.format_sse_event("error", {
                        "message": "❌ Failed to connect to soccer data server"
                    })
                    return
                
                yield self.format_sse_event("status", {
                    "status": "connected", 
                    "message": "✅ Multi-tool soccer server connected"
                })
            
            yield self.format_sse_event("status", {
                "status": "thinking",
                "message": "🤖 AI analyzing multi-tool query..."
            })
            
            self.messages.append({"role": "user", "content": query})
            
            max_iterations = 10
            iteration = 0
            
            while iteration < max_iterations:
                iteration += 1
                
                gemini_response = await self.call_gemini(query)
                logger.info(f"Multi-tool Gemini response (iteration {iteration}): {gemini_response[:1000]}...")
                
                is_tool_call, tool_data, text_response = self.parse_gemini_response(gemini_response)
                
                if is_tool_call and tool_data:
                    tool_name = tool_data.get("name", "unknown").replace("soccerdata-mcp:", "")
                    yield self.format_sse_event("status", {
                        "status": "tool_detected",
                        "message": f"🎯 AI selected {tool_name.replace('_', ' ')} tool"
                    })
                    
                    yield self.format_sse_event("status", {
                        "status": "fetching",
                        "message": "⚽ Fetching multi-tool soccer data..."
                    })
                    
                    tool_result = await self.execute_tool(
                        tool_data.get("name", ""),
                        tool_data.get("parameters", {})
                    )
                    
                    yield self.format_sse_event("status", {
                        "status": "processing",
                        "message": "📊 Processing multi-tool statistics..."
                    })
                    
                    tool_context = f"""Tool {tool_data['name']} returned: {json.dumps(tool_result, indent=2)}

Please provide a comprehensive answer based on this data."""
                    
                    query = f"{query}\n\nTool Result: {tool_context}"
                    
                    # Accumulate results by data type
                    data_type = self.detect_data_type(tool_result)
                    
                    if data_type == 'player_stats' and 'players' in tool_result:
                        self.accumulated_tool_results['players'].extend(tool_result['players'])
                    elif data_type == 'team_stats':
                        if isinstance(tool_result, list):
                            self.accumulated_tool_results['teams'].extend(tool_result)
                        elif 'teams' in tool_result:
                            self.accumulated_tool_results['teams'].extend(tool_result['teams'])
                    
                    # Create combined result for visualization
                    combined_result = {}
                    for key, values in self.accumulated_tool_results.items():
                        if values:
                            combined_result[key] = values
                    
                    logger.info(f"Combined result contains: {list(combined_result.keys())}")
                    
                    # Extract visualization data if needed
                    if self.should_extract_viz_data(query) and combined_result:
                        yield self.format_sse_event("status", {
                            "status": "filtering",
                            "message": "🧠 AI extracting visualization data..."
                        })
                        
                        viz_ready_data = await self.extract_visualization_data(combined_result, query, data_type)
                        self.last_tool_result = viz_ready_data
                    else:
                        self.last_tool_result = combined_result
                    
                    logger.info(f"Multi-tool executed successfully: {tool_data['name']}")
                    
                else:
                    # Stream response
                    yield self.format_sse_event("status", {
                        "status": "generating",
                        "message": "✏️ Generating multi-tool response..."
                    })
                    
                    # Enhance response with visualization data
                    if hasattr(self, 'last_tool_result') and self.last_tool_result:
                        enhanced_response = self.enhance_response_with_data(text_response, self.last_tool_result)
                        self.last_tool_result = None
                        for key in self.accumulated_tool_results:
                            self.accumulated_tool_results[key] = []
                    else:
                        enhanced_response = text_response
                    
                    # Stream response in chunks
                    words = enhanced_response.split()
                    chunk_size = 3
                    
                    for i in range(0, len(words), chunk_size):
                        chunk_words = words[i:i+chunk_size]
                        chunk = " ".join(chunk_words)
                        if i > 0:
                            chunk = " " + chunk
                        
                        yield self.format_sse_event("content", {"chunk": chunk})
                    
                    self.messages.append({"role": "assistant", "content": enhanced_response})
                    return
            
            yield self.format_sse_event("error", {
                "message": "Maximum iterations reached. Please try a simpler query."
            })
            
        except Exception as e:
            logger.error(f"Multi-tool streaming error: {e}")
            yield self.format_sse_event("error", {
                "message": f"Error processing multi-tool query: {e}"
            })
    
    async def process_query(self, query: str) -> str:
        """Process a user query with multi-tool support"""
        try:
            logger.info(f"Processing multi-tool query: {query}")
            
            for key in self.accumulated_tool_results:
                self.accumulated_tool_results[key] = []
            
            if not self.session:
                connected = await self.connect_to_server()
                if not connected:
                    return "Failed to connect to soccer data server. Please try again."
            
            self.messages.append({"role": "user", "content": query})
            
            max_iterations = 3
            iteration = 0
            
            while iteration < max_iterations:
                iteration += 1
                
                gemini_response = await self.call_gemini(query)
                logger.info(f"Multi-tool Gemini response (iteration {iteration}): {gemini_response[:200]}...")
                
                is_tool_call, tool_data, text_response = self.parse_gemini_response(gemini_response)
                
                if is_tool_call and tool_data:
                    tool_result = await self.execute_tool(
                        tool_data.get("name", ""),
                        tool_data.get("parameters", {})
                    )
                    
                    tool_context = f"""Tool {tool_data['name']} returned: {json.dumps(tool_result, indent=2)}
                    
Please provide a comprehensive answer based on this data."""
                    
                    query = f"{query}\n\nTool Result: {tool_context}"
                    
                    # Accumulate multi-tool results
                    data_type = self.detect_data_type(tool_result)
                    
                    if data_type == 'player_stats' and 'players' in tool_result:
                        self.accumulated_tool_results['players'].extend(tool_result['players'])
                    elif data_type == 'team_stats':
                        if isinstance(tool_result, list):
                            self.accumulated_tool_results['teams'].extend(tool_result)
                    
                    combined_result = {}
                    for key, values in self.accumulated_tool_results.items():
                        if values:
                            combined_result[key] = values
                    
                    if self.should_extract_viz_data(query) and combined_result:
                        viz_ready_data = await self.extract_visualization_data(combined_result, query, data_type)
                        self.last_tool_result = viz_ready_data
                    else:
                        self.last_tool_result = combined_result
                    
                    logger.info(f"Multi-tool executed successfully: {tool_data['name']}")
                    
                else:
                    if hasattr(self, 'last_tool_result') and self.last_tool_result:
                        enhanced_response = self.enhance_response_with_data(text_response, self.last_tool_result)
                        self.last_tool_result = None
                        for key in self.accumulated_tool_results:
                            self.accumulated_tool_results[key] = []
                    else:
                        enhanced_response = text_response
                    
                    self.messages.append({"role": "assistant", "content": enhanced_response})
                    return enhanced_response
            
            return "Maximum iterations reached. Please try a simpler query."
            
        except Exception as e:
            logger.error(f"Multi-tool query processing error: {e}")
            return f"Error processing multi-tool query: {e}"
    
    async def get_available_leagues(self) -> List[str]:
        """Get available leagues for frontend"""
        try:
            result = await self.execute_tool("available_leagues", {})
            if "leagues" in result:
                return result["leagues"]
            return []
        except:
            return []
    
    async def cleanup(self):
        """Cleanup resources"""
        global _read_stream, _write_stream, _session, _context_manager
        
        if _session:
            try:
                await _session.__aexit__(None, None, None)
            except:
                pass
        
        if _context_manager:
            try:
                await _context_manager.__aexit__(None, None, None)
            except:
                pass
        
        _session = None
        _read_stream = None
        _write_stream = None
        _context_manager = None
        self.session = None
        logger.info("Multi-tool MCP session closed")