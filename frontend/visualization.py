# import pandas as pd
# import streamlit as st
# from typing import Dict, List, Optional, Tuple
# import re
# import json


# class SoccerVisualizationEngine:
#     """Dynamic visualization engine for soccer data using Streamlit charts"""
    
#     def __init__(self):
#         self.visualization_keywords = [
#             'visualize', 'chart', 'graph', 'plot', 'show chart', 'create chart',
#             'bar chart', 'line chart', 'compare', 'comparison', 'visual'
#         ]
        
#         # Define metric mappings from query keywords to data columns
#         self.metric_mappings = {
#             'goals': ['Performance,Gls', 'Gls'],
#             'assists': ['Performance,Ast', 'Ast'], 
#             'minutes': ['Playing Time,Min', 'Min'],
#             'matches': ['Playing Time,MP', 'MP'],
#             'starts': ['Playing Time,Starts', 'Starts'],
#             'yellow cards': ['Performance,CrdY', 'CrdY'],
#             'red cards': ['Performance,CrdR', 'CrdR'],
#             'goals per 90': ['Per 90 Minutes,Gls'],
#             'assists per 90': ['Per 90 Minutes,Ast'],
#             'penalties': ['Performance,PK', 'PK'],
#             'points': ['Pts'],
#             'wins': ['W'],
#             'draws': ['D'],
#             'losses': ['L'],
#             'goals for': ['GF'],
#             'goals against': ['GA']
#         }
    
#     def should_create_visualization(self, query: str, response: str) -> bool:
#         """Determine if visualization should be created based on keywords"""
#         query_lower = query.lower()
#         return any(keyword in query_lower for keyword in self.visualization_keywords)
    
#     def extract_requested_metrics(self, query: str) -> List[str]:
#         """Extract specific metrics mentioned in the query"""
#         query_lower = query.lower()
#         requested_metrics = []
        
#         for metric_name, column_names in self.metric_mappings.items():
#             if metric_name in query_lower:
#                 requested_metrics.extend(column_names)
        
#         # Default metrics if none specified
#         if not requested_metrics:
#             requested_metrics = ['Performance,Gls', 'Performance,Ast', 'Playing Time,MP']
        
#         return requested_metrics
    
#     # *** UPDATED *** - Enhanced to handle multiple JSON blocks for comparisons
#     def parse_data_from_response(self, response: str) -> Optional[Dict]:
#         """Extract structured data from chatbot response - handles multiple players"""
#         try:
#             all_players = []
            
#             # Look for multiple JSON code blocks first
#             json_blocks = re.findall(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            
#             for json_str in json_blocks:
#                 data = json.loads(json_str)
#                 if 'players' in data:
#                     all_players.extend(data['players'])
            
#             # If we found players from JSON blocks, return combined data
#             if all_players:
#                 return {'players': all_players}
            
#             # Fallback: Look for inline JSON data
#             json_match = re.search(r'\{[^{}]*"players"[^{}]*\[[^\]]*\][^{}]*\}', response, re.DOTALL)
#             if json_match:
#                 json_str = json_match.group()
#                 data = json.loads(json_str)
#                 if 'players' in data:
#                     all_players.extend(data['players'])
#                     return {'players': all_players}
                
#         except Exception as e:
#             st.warning(f"Could not parse JSON data: {e}")
#         return None
    
#     # *** UPDATED *** - Enhanced comparison detection
#     def determine_chart_type(self, data: Dict, query: str) -> str:
#         """Determine chart type based on data structure and query"""
#         if not data or 'players' not in data:
#             return 'none'
        
#         players_data = data['players']
#         if not players_data:
#             return 'none'
        
#         num_records = len(players_data)
#         unique_players = len(set(p.get('player,', '') for p in players_data))
        
#         # Check if query explicitly asks for comparison
#         comparison_keywords = ['compare', 'vs', 'versus', 'comparison']
#         has_comparison_keyword = any(keyword in query.lower() for keyword in comparison_keywords)
        
#         # Analysis logic from documentation
#         if has_comparison_keyword or unique_players > 1:
#             return 'comparison'   # Comparison analysis
#         elif num_records == 1:
#             return 'single_bar'  # Single item analysis
#         else:
#             return 'comparison'  # Default to comparison for multiple records
    
#     def find_best_metrics(self, data: Dict, query: str) -> List[str]:
#         """Find the best metrics to display based on query and available data"""
#         players_data = data.get('players', [])
#         if not players_data:
#             return []
        
#         # Get available columns
#         available_columns = list(players_data[0].keys())
        
#         # Get requested metrics from query
#         requested_metrics = self.extract_requested_metrics(query)
        
#         # Find intersection of requested and available
#         valid_metrics = []
#         for metric in requested_metrics:
#             if metric in available_columns:
#                 valid_metrics.append(metric)
        
#         # Fallback to common metrics if none found
#         if not valid_metrics:
#             fallback_metrics = ['Performance,Gls', 'Performance,Ast', 'Playing Time,MP']
#             for metric in fallback_metrics:
#                 if metric in available_columns:
#                     valid_metrics.append(metric)
        
#         return valid_metrics[:4]  # Limit to 4 metrics for readability
    
#     def create_data_table(self, data: Dict, metrics: List[str]) -> str:
#         """Create markdown table for comparison data"""
#         players_data = data.get('players', [])
#         if not players_data:
#             return ""
        
#         # Create DataFrame
#         df = pd.DataFrame(players_data)
        
#         # Select relevant columns
#         display_columns = ['player,'] + metrics
#         available_columns = [col for col in display_columns if col in df.columns]
        
#         if len(available_columns) < 2:
#             return ""
        
#         # Create clean table
#         display_df = df[available_columns].copy()
        
#         # Clean column names for display
#         column_mapping = {
#             'player,': 'Player',
#             'Performance,Gls': 'Goals',
#             'Performance,Ast': 'Assists',
#             'Playing Time,MP': 'Matches',
#             'Playing Time,Min': 'Minutes',
#             'Performance,CrdY': 'Yellow Cards',
#             'Performance,CrdR': 'Red Cards'
#         }
        
#         display_df = display_df.rename(columns=column_mapping)
        
#         return display_df.to_markdown(index=False)
    
#     def create_single_bar_chart(self, data: Dict, metrics: List[str]) -> pd.DataFrame:
#         """Create DataFrame for single item analysis bar chart"""
#         players_data = data.get('players', [])
#         if not players_data:
#             return pd.DataFrame()
        
#         player_data = players_data[0]
        
#         # Extract metric values
#         chart_data = []
        
#         for metric in metrics:
#             if metric in player_data:
#                 # Clean metric name for display
#                 clean_name = metric.replace('Performance,', '').replace('Playing Time,', '').replace('Per 90 Minutes,', '')
#                 chart_data.append({
#                     'Metric': clean_name,
#                     'Value': player_data[metric]
#                 })
        
#         df = pd.DataFrame(chart_data)
#         return df.set_index('Metric') if not df.empty else pd.DataFrame()
    
#     #  UPDATED - Fixed to handle multiple players properly
#     def create_comparison_chart(self, data: Dict, metrics: List[str]) -> pd.DataFrame:
#         """Create DataFrame for comparison analysis - handles multiple players"""
#         players_data = data.get('players', [])
#         if not players_data:
#             return pd.DataFrame()
        
#         # Create DataFrame for Streamlit bar chart
#         chart_data = []
        
#         # Get clean metric names
#         clean_metrics = [metric.replace('Performance,', '').replace('Playing Time,', '').replace('Per 90 Minutes,', '') for metric in metrics]
        
#         for player_data in players_data:
#             player_name = player_data.get('player,', 'Unknown')
#             player_row = {'Player': player_name}
            
#             for i, metric in enumerate(metrics):
#                 if metric in player_data:
#                     clean_name = clean_metrics[i]
#                     player_row[clean_name] = player_data[metric]
            
#             chart_data.append(player_row)
        
#         # Convert to DataFrame with players as index and metrics as columns
#         df = pd.DataFrame(chart_data)
#         if not df.empty:
#             df = df.set_index('Player')
        
#         return df
    
#     def render_visualization(self, query: str, response: str):
#         """Main method to render visualization in Streamlit"""
        
#         # Check if visualization is requested
#         if not self.should_create_visualization(query, response):
#             return
        
#         # Extract data from response
#         data = self.parse_data_from_response(response)
#         if not data:
#             st.warning("No data found for visualization. Make sure your query includes proper data.")
#             return
        
#         # Determine chart type
#         chart_type = self.determine_chart_type(data, query)
#         if chart_type == 'none':
#             return
        
#         # Find best metrics to display
#         metrics = self.find_best_metrics(data, query)
#         if not metrics:
#             st.warning("No valid metrics found for visualization.")
#             return
        
#         st.markdown("---")
#         st.subheader("📊 Dynamic Visualization")
        
#         # *** UPDATED *** - Enhanced rendering logic
#         # Create appropriate visualization
#         if chart_type == 'single_bar':
#             chart_df = self.create_single_bar_chart(data, metrics)
#             if not chart_df.empty:
#                 st.markdown("### 📈 Performance Breakdown")
#                 st.bar_chart(chart_df)
#                 st.info("💡 **Single Item Analysis**: This bar chart breaks down the key performance metrics for detailed analysis.")
                
#         elif chart_type == 'comparison':
#             # Create data table
#             table = self.create_data_table(data, metrics)
#             if table:
#                 st.markdown("### 📋 Data Comparison Table")
#                 st.markdown(table)
#                 st.markdown("")  # Add spacing
            
#             # Create comparison chart
#             chart_df = self.create_comparison_chart(data, metrics)
#             if not chart_df.empty:
#                 st.markdown("### 📈 Visual Comparison")
#                 st.bar_chart(chart_df)
                
#                 # Alternative views for specific cases
#                 if len(chart_df.columns) == 2:
#                     st.markdown("#### Alternative View: Scatter Plot")
#                     # Create scatter data
#                     scatter_data = chart_df.reset_index()
#                     col1, col2 = chart_df.columns[0], chart_df.columns[1]
#                     scatter_data = scatter_data.rename(columns={'index': 'Player'})
#                     st.scatter_chart(scatter_data, x=col1, y=col2)
                
#                 st.info("💡 **Comparison Analysis**: The table shows exact values while the chart provides visual comparison between entities.")


# # Helper function for Streamlit integration
# def process_visualization_request(query: str, response: str):
#     """Process and render visualization directly in Streamlit"""
#     engine = SoccerVisualizationEngine()
#     engine.render_visualization(query, response)

#visualization.py

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Optional, Tuple
import re
import json
import numpy as np


class SoccerVisualizationEngine:
    """Dynamic visualization engine supporting all soccer tools with intelligent chart selection"""
    
    def __init__(self):
        self.visualization_keywords = [
            'visualize', 'chart', 'graph', 'plot', 'show chart', 'create chart',
            'bar chart', 'line chart', 'compare', 'comparison', 'visual', 'pie chart', 'pie',
            'spider', 'radar', 'performance profile', 'strengths', 'weaknesses', 'spider chart',
            'analyze', 'analysis', 'breakdown', 'distribution', 'table', 'stats', 'show'
        ]
        
        # Supported tool data mappings
        self.tool_data_configs = {
            'get_player_season_stats_filtered': {
                'data_key': 'players',
                'entity_field': ['player,', 'player'],
                'key_metrics': ['Performance,Gls', 'Performance,Ast', 'Playing Time,MP', 'Performance,CrdY'],
                'chart_types': ['spider', 'bar', 'pie', 'table']
            },
            'read_team_season_stats': {
                'data_key': 'teams', 
                'entity_field': ['team'],
                'key_metrics': ['Pts', 'W', 'D', 'L', 'GF', 'GA'],
                'chart_types': ['spider', 'bar', 'pie', 'table']
            },
            'read_shot_events_filtered': {
                'data_key': 'shots',
                'entity_field': ['player', 'team'],
                'key_metrics': ['outcome', 'total_shots'],
                'chart_types': ['bar', 'pie', 'table']
            },
            'read_schedule': {
                'data_key': 'matches',
                'entity_field': ['Home', 'Away'],
                'key_metrics': ['date', 'Home', 'Away', 'Score'],
                'chart_types': ['table', 'bar']
            },
            'read_team_match_stats': {
                'data_key': 'matches',
                'entity_field': ['team'],
                'key_metrics': ['date', 'Opponent', 'Result'],
                'chart_types': ['table', 'bar']
            },
            'available_leagues': {
                'data_key': 'leagues',
                'entity_field': ['league'],
                'key_metrics': ['league', 'country'],
                'chart_types': ['table']
            },
            'read_leagues': {
                'data_key': 'leagues',
                'entity_field': ['league'],
                'key_metrics': ['league', 'country'],
                'chart_types': ['table']
            },
            'read_seasons': {
                'data_key': 'seasons',
                'entity_field': ['season'],
                'key_metrics': ['season', 'league'],
                'chart_types': ['table']
            }
        }
    
    def should_create_visualization(self, query: str, response: str) -> bool:
        """Enhanced check for visualization needs - supports all data types"""
        # Check for visualization keywords
        has_viz_keyword = any(keyword in query.lower() for keyword in self.visualization_keywords)
        
        # Check if response contains structured data
        has_structured_data = '```json' in response
        
        # Always visualize if we have data and user is asking for analysis
        return has_viz_keyword or has_structured_data
    
    def parse_data_from_response(self, response: str) -> Optional[Dict]:
        """Enhanced data parsing supporting all tool outputs"""
        try:
            json_blocks = re.findall(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            
            combined_data = {}
            
            for json_str in json_blocks:
                data = json.loads(json_str)
                
                # Handle all possible data structures
                for tool_config in self.tool_data_configs.values():
                    data_key = tool_config['data_key']
                    
                    if data_key in data:
                        if data_key not in combined_data:
                            combined_data[data_key] = []
                        
                        if isinstance(data[data_key], list):
                            combined_data[data_key].extend(data[data_key])
                        else:
                            combined_data[data_key].append(data[data_key])
                
                # Handle single entity data (like filtered extraction)
                if not any(key in data for key in ['players', 'teams', 'shots', 'matches', 'leagues', 'seasons']):
                    # This is likely a single player/team object
                    if any(field in data for field in ['player', 'player,', 'Performance,Gls']):
                        combined_data['players'] = [data]
                    elif any(field in data for field in ['team', 'Pts', 'W', 'D', 'L']):
                        combined_data['teams'] = [data]
            
            if combined_data:
                data_summary = [f"{len(v)} {k}" for k, v in combined_data.items() if v]
                st.info(f"Loaded data: {', '.join(data_summary)}")
                return combined_data
            
            return None
                
        except Exception as e:
            st.warning(f"Could not parse visualization data: {e}")
            return None
    
    def detect_data_types(self, data: Dict) -> List[str]:
        """Detect all data types present in the data"""
        detected_types = []
        
        for data_key in data:
            if data[data_key]:  # Check if data exists and is not empty
                detected_types.append(data_key)
        
        return detected_types
    
    def count_entities_by_type(self, data: Dict) -> Dict[str, int]:
        """Count entities for each data type"""
        entity_counts = {}
        
        for data_type, records in data.items():
            if isinstance(records, list):
                entity_counts[data_type] = len(records)
            else:
                entity_counts[data_type] = 1
                
        return entity_counts
    
    def determine_chart_strategy(self, data: Dict, query: str) -> Dict:
        """Determine optimal visualization strategy for any data type"""
        
        data_types = self.detect_data_types(data)
        entity_counts = self.count_entities_by_type(data)
        query_lower = query.lower()
        
        # Explicit chart requests
        if any(word in query_lower for word in ['spider', 'radar', 'profile']):
            primary_chart = 'spider'
        elif any(word in query_lower for word in ['pie', 'distribution', 'breakdown']):
            primary_chart = 'pie'
        elif any(word in query_lower for word in ['table', 'detailed', 'all data']):
            primary_chart = 'table'
        elif any(word in query_lower for word in ['compare', 'vs', 'versus']):
            primary_chart = 'bar'
        else:
            # Dynamic selection based on data characteristics
            total_entities = sum(entity_counts.values())
            
            if 'players' in data_types and total_entities == 1:
                primary_chart = 'spider'  # Single player profile
            elif total_entities > 1:
                primary_chart = 'bar'     # Multiple entities comparison
            elif 'leagues' in data_types or 'seasons' in data_types:
                primary_chart = 'table'   # Reference data
            else:
                primary_chart = 'bar'     # Default
        
        return {
            'primary_chart': primary_chart,
            'secondary_chart': 'table',
            'data_types': data_types,
            'entity_counts': entity_counts,
            'reasoning': f'Selected {primary_chart} for {len(data_types)} data types with {sum(entity_counts.values())} total entities'
        }
    
    def render_visualization(self, query: str, response: str):
        """Main dynamic visualization renderer supporting all tools"""
        
        try:
            if not self.should_create_visualization(query, response):
                return
            
            # Parse data from response
            data = self.parse_data_from_response(response)
            if not data:
                st.warning("No visualization data found in response.")
                return
            
            # Determine visualization strategy
            strategy = self.determine_chart_strategy(data, query)
            
            # Create visualization section
            st.markdown("---")
            st.subheader("Dynamic Multi-Tool Visualization")
            
            # Show strategy info
            st.info(f"**Strategy**: {strategy['reasoning']}")
            
            # Show data summary
            if strategy['data_types']:
                summary_items = [f"{count} {dtype}" for dtype, count in strategy['entity_counts'].items()]
                st.success(f"**Data Available**: {', '.join(summary_items)}")
            
            # Debug view
            with st.expander("View Raw Data"):
                st.json(data)
            
            # Render visualizations
            self.render_dynamic_visualizations(data, strategy, query)
            
        except Exception as e:
            st.error(f"Visualization error: {e}")
            if 'data' in locals() and data:
                st.info("Showing raw data as fallback:")
                st.json(data)
    
    def render_dynamic_visualizations(self, data: Dict, strategy: Dict, query: str):
        """Render visualizations based on strategy and data types"""
        
        primary_chart = strategy['primary_chart']
        secondary_chart = strategy['secondary_chart']
        data_types = strategy['data_types']
        
        try:
            # Primary visualization
            if primary_chart == 'spider':
                self.create_universal_spider_chart(data, data_types)
            elif primary_chart == 'pie':
                self.create_universal_pie_charts(data, data_types)
            elif primary_chart == 'bar':
                self.create_universal_bar_charts(data, data_types)
            elif primary_chart == 'table':
                self.create_universal_tables(data, data_types)
            
            # Secondary visualization
            if secondary_chart != primary_chart and secondary_chart != 'none':
                st.markdown("### Secondary Analysis")
                
                if secondary_chart == 'table':
                    self.create_universal_tables(data, data_types)
                elif secondary_chart == 'bar':
                    self.create_universal_bar_charts(data, data_types)
                elif secondary_chart == 'pie':
                    self.create_universal_pie_charts(data, data_types)
            
        except Exception as e:
            st.error(f"Chart rendering failed: {e}")
            st.warning("Falling back to table view")
            self.create_universal_tables(data, data_types)
    
    def create_universal_spider_chart(self, data: Dict, data_types: List[str]):
        """Universal spider chart supporting players and teams"""
        
        st.markdown("### Spider Chart Analysis")
        
        if 'players' in data_types:
            self.create_player_spider_chart(data['players'])
        elif 'teams' in data_types:
            self.create_team_spider_chart(data['teams'])
        else:
            st.warning("Spider charts work best with player or team data")
            self.create_universal_bar_charts(data, data_types)
    
    def create_player_spider_chart(self, players_data: List[Dict]):
        """Enhanced player spider chart"""
        
        if not players_data:
            st.warning("No player data available for spider chart")
            return
        
        spider_metrics = {
            'Goals': ['Performance,Gls', 'Goals'],
            'Assists': ['Performance,Ast', 'Assists'],
            'Matches': ['Playing Time,MP', 'Matches'],
            'Goals/90': ['Per 90 Minutes,Gls', 'Goals/90'],
            'Assists/90': ['Per 90 Minutes,Ast', 'Assists/90'],
            'Discipline': ['Performance,CrdY', 'Yellow Cards']
        }
        
        fig = go.Figure()
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#FF8C42', '#6C5CE7']
        
        for idx, player in enumerate(players_data[:8]):
            player_name = self._get_entity_name(player, ['player,', 'player', 'Player'])
            
            values = []
            labels = []
            
            for label, possible_keys in spider_metrics.items():
                value = self._get_flexible_value(player, possible_keys, 0)
                
                if label == 'Discipline':
                    max_cards = 15
                    value = max(0, max_cards - float(value)) * (100 / max_cards)
                    labels.append(f"{label}<br>(Fewer cards = better)")
                else:
                    labels.append(label)
                
                values.append(float(value) if value else 0)
            
            # Normalize values
            normalized_values = []
            max_vals = {'Goals': 50, 'Assists': 25, 'Matches': 40, 'Goals/90': 2.0, 'Assists/90': 1.5}
            
            for i, (label, value) in enumerate(zip(spider_metrics.keys(), values)):
                if label == 'Discipline':
                    normalized_values.append(value)
                else:
                    max_val = max_vals.get(label, 100)
                    normalized_values.append(min(100, (value / max_val) * 100))
            
            fig.add_trace(go.Scatterpolar(
                r=normalized_values + [normalized_values[0]],
                theta=labels + [labels[0]],
                fill='toself',
                name=player_name,
                line_color=colors[idx % len(colors)],
                fillcolor=colors[idx % len(colors)],
                opacity=0.6
            ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100],
                    showticklabels=True,
                    tickvals=[20, 40, 60, 80, 100],
                    ticktext=['20%', '40%', '60%', '80%', '100%']
                )
            ),
            showlegend=True,
            title="Player Performance Spider Chart",
            height=600
        )
        
        st.plotly_chart(fig, use_container_width=True)
        st.info("Spider chart shows normalized performance metrics (0-100%). Larger areas indicate better overall performance.")
    
    def create_team_spider_chart(self, teams_data: List[Dict]):
        """Team spider chart visualization"""
        
        if not teams_data:
            st.warning("No team data available for spider chart")
            return
        
        team_metrics = {
            'Attack': ['GF', 'Goals For'],
            'Defense': ['GA', 'Goals Against'],
            'Points': ['Pts', 'Points'],
            'Wins': ['W', 'Wins'],
            'Draws': ['D', 'Draws'],
            'Goal Diff': ['GD', 'Goal Difference']
        }
        
        fig = go.Figure()
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD']
        
        for idx, team in enumerate(teams_data[:6]):
            team_name = self._get_entity_name(team, ['team', 'Team'])
            
            values = []
            labels = []
            
            for label, possible_keys in team_metrics.items():
                value = self._get_flexible_value(team, possible_keys, 0)
                
                if label == 'Defense':
                    max_ga = 80
                    value = max(0, max_ga - float(value)) * (100 / max_ga)
                    labels.append(f"{label}<br>(Fewer goals = better)")
                else:
                    labels.append(label)
                
                values.append(float(value) if value else 0)
            
            # Normalize values
            normalized_values = []
            max_vals = {'Attack': 120, 'Points': 100, 'Wins': 35, 'Draws': 15, 'Goal Diff': 80}
            
            for i, (label, value) in enumerate(zip(team_metrics.keys(), values)):
                if label == 'Defense':
                    normalized_values.append(value)
                else:
                    max_val = max_vals.get(label, 100)
                    normalized_values.append(min(100, (value / max_val) * 100))
            
            fig.add_trace(go.Scatterpolar(
                r=normalized_values + [normalized_values[0]],
                theta=labels + [labels[0]],
                fill='toself',
                name=team_name,
                line_color=colors[idx % len(colors)],
                fillcolor=colors[idx % len(colors)],
                opacity=0.6
            ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100],
                    showticklabels=True,
                    tickvals=[20, 40, 60, 80, 100],
                    ticktext=['20%', '40%', '60%', '80%', '100%']
                )
            ),
            showlegend=True,
            title="Team Performance Spider Chart",
            height=600
        )
        
        st.plotly_chart(fig, use_container_width=True)
        st.info("Team spider chart shows normalized performance across key metrics.")
    
    def create_universal_pie_charts(self, data: Dict, data_types: List[str]):
        """Universal pie charts for all data types"""
        
        st.markdown("### Distribution Analysis")
        
        charts_created = 0
        
        for data_type in data_types:
            if data_type in data and data[data_type]:
                pie_data = self._create_pie_data_for_type(data[data_type], data_type)
                if pie_data is not None:
                    title = f"{data_type.replace('_', ' ').title()} Distribution"
                    self._render_enhanced_pie_chart(pie_data, title)
                    charts_created += 1
        
        if charts_created == 0:
            st.warning("No suitable data found for pie chart visualization")
    
    def _create_pie_data_for_type(self, records: List[Dict], data_type: str) -> Optional[pd.DataFrame]:
        """Create pie chart data for any data type"""
        
        if not records:
            return None
        
        try:
            if data_type == 'players':
                if len(records) == 1:
                    player = records[0]
                    goals = self._get_flexible_value(player, ['Performance,Gls', 'Goals'], 0)
                    assists = self._get_flexible_value(player, ['Performance,Ast', 'Assists'], 0)
                    
                    if goals + assists > 0:
                        return pd.DataFrame({
                            'Category': ['Goals', 'Assists'],
                            'Value': [goals, assists],
                            'Percentage': [
                                round(goals/(goals+assists)*100, 1),
                                round(assists/(goals+assists)*100, 1)
                            ]
                        })
                else:
                    # Multiple players - goals distribution
                    pie_data = []
                    total_goals = sum(self._get_flexible_value(p, ['Performance,Gls', 'Goals'], 0) for p in records)
                    
                    if total_goals > 0:
                        for player in records:
                            goals = self._get_flexible_value(player, ['Performance,Gls', 'Goals'], 0)
                            name = self._get_entity_name(player, ['player,', 'player', 'Player'])
                            percentage = round((goals/total_goals)*100, 1)
                            pie_data.append({
                                'Category': name,
                                'Value': goals,
                                'Percentage': percentage
                            })
                        return pd.DataFrame(pie_data)
            
            elif data_type == 'teams':
                if len(records) == 1:
                    team = records[0]
                    wins = self._get_flexible_value(team, ['W', 'Wins'], 0)
                    draws = self._get_flexible_value(team, ['D', 'Draws'], 0)
                    losses = self._get_flexible_value(team, ['L', 'Losses'], 0)
                    total = wins + draws + losses
                    
                    if total > 0:
                        return pd.DataFrame({
                            'Category': ['Wins', 'Draws', 'Losses'],
                            'Value': [wins, draws, losses],
                            'Percentage': [
                                round(wins/total*100, 1),
                                round(draws/total*100, 1),
                                round(losses/total*100, 1)
                            ]
                        })
                else:
                    # Multiple teams - points distribution
                    pie_data = []
                    total_points = sum(self._get_flexible_value(t, ['Pts', 'Points'], 0) for t in records)
                    
                    if total_points > 0:
                        for team in records:
                            points = self._get_flexible_value(team, ['Pts', 'Points'], 0)
                            name = self._get_entity_name(team, ['team', 'Team'])
                            percentage = round((points/total_points)*100, 1)
                            pie_data.append({
                                'Category': name,
                                'Value': points,
                                'Percentage': percentage
                            })
                        return pd.DataFrame(pie_data)
            
            elif data_type == 'shots':
                # Shot outcomes distribution
                outcome_counts = {}
                for shot in records:
                    outcome = self._get_flexible_value(shot, ['outcome', 'Outcome'], 'Unknown')
                    outcome_counts[outcome] = outcome_counts.get(outcome, 0) + 1
                
                if outcome_counts:
                    total_shots = sum(outcome_counts.values())
                    pie_data = []
                    for outcome, count in outcome_counts.items():
                        percentage = round((count/total_shots)*100, 1)
                        pie_data.append({
                            'Category': outcome,
                            'Value': count,
                            'Percentage': percentage
                        })
                    return pd.DataFrame(pie_data)
            
        except Exception as e:
            st.warning(f"Could not create pie data for {data_type}: {e}")
            
        return None
    
    def _render_enhanced_pie_chart(self, pie_data: pd.DataFrame, title: str):
        """Render enhanced pie chart"""
        
        try:
            pie_data_filtered = pie_data[pie_data['Value'] > 0]
            
            if pie_data_filtered.empty:
                return
            
            labels = [f"{row['Category']}<br>{row['Value']} ({row['Percentage']}%)" 
                     for _, row in pie_data_filtered.iterrows()]
            
            fig = go.Figure(data=[go.Pie(
                labels=labels,
                values=pie_data_filtered['Value'],
                hole=0.3,
                textinfo='label',
                textposition='outside',
                showlegend=True,
                marker=dict(
                    colors=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#FF8C42', '#6C5CE7'],
                    line=dict(color='#FFFFFF', width=3)
                )
            )])
            
            fig.update_layout(
                title=title,
                height=500,
                font=dict(size=12)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error creating pie chart: {e}")
    
    def create_universal_bar_charts(self, data: Dict, data_types: List[str]):
        """Universal bar charts for all data types"""
        
        st.markdown("### Comparative Analysis")
        
        for data_type in data_types:
            if data_type in data and data[data_type]:
                try:
                    records = data[data_type]
                    df = pd.DataFrame(records)
                    
                    if not df.empty:
                        self._render_bar_chart_for_type(df, data_type)
                        
                except Exception as e:
                    st.warning(f"Could not create bar chart for {data_type}: {e}")
    
    def _render_bar_chart_for_type(self, df: pd.DataFrame, data_type: str):
        """Render bar chart for specific data type"""
        
        try:
            df_clean = self._clean_column_names(df)
            
            # Get entity column
            entity_cols = ['Player', 'Team', 'League', 'Home', 'Away']
            entity_col = None
            
            for col in entity_cols:
                if col in df_clean.columns:
                    entity_col = col
                    break
            
            if entity_col and len(df_clean) > 1:
                df_chart = df_clean.set_index(entity_col)
            else:
                df_chart = df_clean
            
            # Select numeric columns
            numeric_cols = df_chart.select_dtypes(include=[int, float]).columns.tolist()
            
            # Prioritize key metrics
            if data_type == 'players':
                priority_metrics = ['Goals', 'Assists', 'Matches', 'Goals/90', 'Assists/90']
            elif data_type == 'teams':
                priority_metrics = ['Points', 'Wins', 'Goals For', 'Goals Against']
            else:
                priority_metrics = numeric_cols[:6]
            
            final_cols = []
            for metric in priority_metrics:
                if metric in numeric_cols:
                    final_cols.append(metric)
                    numeric_cols.remove(metric)
            
            final_cols.extend(numeric_cols[:6-len(final_cols)])
            
            if final_cols:
                chart_data = df_chart[final_cols]
                
                st.markdown(f"#### {data_type.replace('_', ' ').title()} Comparison")
                st.bar_chart(chart_data, height=400)
                
                if len(final_cols) > 0:
                    st.info(f"Showing metrics: {', '.join(final_cols)}")
            
        except Exception as e:
            st.error(f"Error creating bar chart for {data_type}: {e}")
    
    def create_universal_tables(self, data: Dict, data_types: List[str]):
        """Universal table view for all data types"""
        
        st.markdown("### Detailed Data Tables")
        
        for data_type in data_types:
            if data_type in data and data[data_type]:
                try:
                    records = data[data_type]
                    df = pd.DataFrame(records)
                    df_clean = self._clean_column_names(df)
                    
                    st.markdown(f"#### {data_type.replace('_', ' ').title()}")
                    st.dataframe(df_clean, use_container_width=True)
                    st.write(f"Records: {len(df_clean)}")
                    
                except Exception as e:
                    st.warning(f"Could not create table for {data_type}: {e}")
    
    def _clean_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """Enhanced column name cleaning for all data types"""
        
        column_mapping = {
            'player,': 'Player',
        'player': 'Player',
        'Performance,Gls': 'Goals',
        'Performance,Ast': 'Assists',
        'Playing Time,MP': 'Matches',
        'Playing Time,Min': 'Minutes',
        'Playing Time,Starts': 'Starts',
        'Playing Time,90s': '90s',
        'Performance,CrdY': 'Yellow Cards',
        'Performance,CrdR': 'Red Cards',
        'Performance,G+A': 'G+A',
        'Performance,G-PK': 'G-PK',
        'Performance,PK': 'PK',
        'Performance,PKatt': 'PKatt',
        'Per 90 Minutes,Gls': 'Goals/90',
        'Per 90 Minutes,Ast': 'Assists/90',
        'Per 90 Minutes,G+A': 'G+A/90',  # Changed to avoid duplicate
        'Per 90 Minutes,G-PK': 'G-PK/90',  # Changed to avoid duplicate
        'Per 90 Minutes,G+A-PK': 'G+A-PK/90',  # Changed to avoid duplicate
        'team': 'Team',
        'team,': 'Team',
        'Pts': 'Points',
        'W': 'Wins',
        'D': 'Draws',
        'L': 'Losses',
        'GF': 'Goals For',
        'GA': 'Goals Against',
        'GD': 'Goal Difference',
        'league,': 'League',
        'season,': 'Season',
        'nation,': 'Nation',
        'pos,': 'Position',
        'age,': 'Age',
        'born,': 'Born'
        }
        
        df_renamed = df.rename(columns=column_mapping)
        
        # Clean comma-based column names
        new_columns = {}
        for col in df_renamed.columns:
            if ',' in str(col):
                clean_name = str(col).split(',')[-1].strip()
                new_columns[col] = clean_name
        
        if new_columns:
            df_renamed = df_renamed.rename(columns=new_columns)
        
        return df_renamed
    
    def _get_flexible_value(self, data_dict: Dict, possible_keys: List[str], default=None):
        """Get value with flexible key matching"""
        for key in possible_keys:
            if key in data_dict:
                return data_dict[key]
        return default
    
    def _get_entity_name(self, data_dict: Dict, possible_keys: List[str]) -> str:
        """Get entity name with fallbacks"""
        name = self._get_flexible_value(data_dict, possible_keys, 'Unknown')
        return str(name)


# Helper function for Streamlit integration
def process_visualization_request(query: str, response: str):
    """Process and render dynamic visualization supporting all soccer tools"""
    engine = SoccerVisualizationEngine()
    engine.render_visualization(query, response)