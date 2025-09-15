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
import pandas as pd
import streamlit as st
from typing import Dict, List, Optional
import re
import json


class SoccerVisualizationEngine:
    """Enhanced visualization engine with pie charts and multi-tool support"""
    
    def __init__(self):
        self.visualization_keywords = [
            'visualize', 'chart', 'graph', 'plot', 'show chart', 'create chart',
            'bar chart', 'line chart', 'compare', 'comparison', 'visual', 'pie chart', 'pie'
        ]
    
    def should_create_visualization(self, query: str, response: str) -> bool:
        """Determine if visualization should be created based on keywords"""
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in self.visualization_keywords)
    
    def parse_data_from_response(self, response: str) -> Optional[Dict]:
        """Extract data from chatbot response - supports multiple data types"""
        try:
            # Look for JSON code blocks (primary method for filtered data)
            json_blocks = re.findall(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            
            combined_data = {}
            
            for json_str in json_blocks:
                data = json.loads(json_str)
                
                # Merge different data types
                for key in ['players', 'teams', 'shots', 'matches']:
                    if key in data:
                        if key not in combined_data:
                            combined_data[key] = []
                        combined_data[key].extend(data[key])
            
            if combined_data:
                st.info(f"Loaded data: {', '.join([f'{len(v)} {k}' for k, v in combined_data.items()])}")
                return combined_data
            
            # Fallback: Look for inline JSON data
            json_match = re.search(r'\{[^{}]*"(players|teams|shots|matches)"[^{}]*\[[^\]]*\][^{}]*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                return json.loads(json_str)
                
        except Exception as e:
            st.warning(f"Could not parse visualization data: {e}")
        return None
    
    def detect_data_type(self, data: Dict) -> str:
        """Detect primary data type for visualization logic"""
        if 'players' in data and data['players']:
            return 'player_stats'
        elif 'teams' in data and data['teams']:
            return 'team_stats'
        elif 'shots' in data and data['shots']:
            return 'shot_data'
        elif 'matches' in data and data['matches']:
            return 'match_data'
        return 'unknown'
    
    def determine_chart_type(self, data: Dict, query: str) -> str:
        """Determine chart type based on data structure and query intent"""
        data_type = self.detect_data_type(data)
        
        if data_type == 'unknown':
            return 'none'
        
        # Check for comparison keywords
        comparison_keywords = ['compare', 'vs', 'versus', 'comparison', 'between']
        has_comparison_keyword = any(keyword in query.lower() for keyword in comparison_keywords)
        
        # Check for pie chart keywords
        pie_keywords = ['pie', 'distribution', 'breakdown', 'percentage', 'proportion']
        wants_pie_chart = any(keyword in query.lower() for keyword in pie_keywords)
        
        # Determine entity count
        entity_count = 0
        if data_type == 'player_stats':
            entity_count = len(set(p.get('player,', '') for p in data.get('players', [])))
        elif data_type == 'team_stats':
            entity_count = len(data.get('teams', []))
        
        if wants_pie_chart:
            return 'pie_focus'
        elif has_comparison_keyword or entity_count > 1:
            return 'comparison'
        else:
            return 'single_analysis'
    
    def clean_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean column names for better display"""
        column_mapping = {
            'player,': 'Player',
            'Performance,Gls': 'Goals',
            'Performance,Ast': 'Assists',
            'Playing Time,MP': 'Matches',
            'Performance,CrdY': 'Yellow Cards',
            'Performance,CrdR': 'Red Cards',
            'Per 90 Minutes,Gls': 'Goals/90',
            'Per 90 Minutes,Ast': 'Assists/90',
            'team': 'Team',
            'Pts': 'Points',
            'W': 'Wins',
            'D': 'Draws', 
            'L': 'Losses',
            'GF': 'Goals For',
            'GA': 'Goals Against',
            'GD': 'Goal Difference'
        }
        
        return df.rename(columns=column_mapping)
    
    def create_pie_chart_data(self, data: Dict, data_type: str) -> Optional[pd.DataFrame]:
        """Create pie chart data based on data type"""
        
        if data_type == 'player_stats':
            players_data = data.get('players', [])
            if not players_data:
                return None
            
            # For single player: Goals vs Assists breakdown
            if len(players_data) == 1:
                player = players_data[0]
                goals = player.get('Performance,Gls', 0)
                assists = player.get('Performance,Ast', 0)
                
                if goals + assists > 0:
                    return pd.DataFrame({
                        'Contribution': ['Goals', 'Assists'],
                        'Count': [goals, assists]
                    })
            
            # For multiple players: Goals distribution
            else:
                pie_data = []
                for player in players_data:
                    pie_data.append({
                        'Player': player.get('player,', 'Unknown'),
                        'Goals': player.get('Performance,Gls', 0)
                    })
                return pd.DataFrame(pie_data)
        
        elif data_type == 'team_stats':
            teams_data = data.get('teams', [])
            if not teams_data:
                return None
            
            # For single team: W/D/L breakdown
            if len(teams_data) == 1:
                team = teams_data[0]
                wins = team.get('W', 0)
                draws = team.get('D', 0)
                losses = team.get('L', 0)
                
                return pd.DataFrame({
                    'Result': ['Wins', 'Draws', 'Losses'],
                    'Count': [wins, draws, losses]
                })
            
            # For multiple teams: Points distribution
            else:
                pie_data = []
                for team in teams_data:
                    pie_data.append({
                        'Team': team.get('team', 'Unknown'),
                        'Points': team.get('Pts', 0)
                    })
                return pd.DataFrame(pie_data)
        
        return None
    
    def create_comparison_visualization(self, data: Dict):
        """Create comparison table and charts for multiple entities"""
        data_type = self.detect_data_type(data)
        
        if data_type == 'player_stats':
            players_data = data.get('players', [])
            df = pd.DataFrame(players_data)
        elif data_type == 'team_stats':
            teams_data = data.get('teams', [])
            df = pd.DataFrame(teams_data)
        else:
            st.warning("Unsupported data type for comparison")
            return
        
        if df.empty:
            return
        
        # Clean column names
        df_clean = self.clean_column_names(df)
        
        # Display comparison table
        st.markdown("### 📋 Data Comparison Table")
        st.dataframe(df_clean, use_container_width=True)
        st.markdown("")
        
        # Create bar chart
        chart_df = df_clean.copy()
        
        # Set entity names as index for charting
        index_col = 'Player' if data_type == 'player_stats' else 'Team'
        if index_col in chart_df.columns:
            chart_df = chart_df.set_index(index_col)
        
        # Select only numeric columns
        numeric_columns = chart_df.select_dtypes(include=[int, float]).columns
        chart_data = chart_df[numeric_columns]
        
        if not chart_data.empty:
            st.markdown("### 📊 Bar Chart Comparison")
            st.bar_chart(chart_data)
            
            # Add pie chart for goals distribution (if goals data exists)
            pie_data = self.create_pie_chart_data(data, data_type)
            if pie_data is not None and len(pie_data) > 1:
                st.markdown("### 🥧 Distribution Pie Chart")
                
                if data_type == 'player_stats':
                    # Goals distribution among players
                    fig_data = pie_data.set_index('Player')['Goals']
                    st.plotly_chart({
                        "data": [{
                            "type": "pie",
                            "labels": fig_data.index.tolist(),
                            "values": fig_data.values.tolist(),
                            "hole": 0.3
                        }],
                        "layout": {"title": "Goals Distribution"}
                    }, use_container_width=True)
                
                elif data_type == 'team_stats':
                    # Points distribution among teams
                    fig_data = pie_data.set_index('Team')['Points']
                    st.plotly_chart({
                        "data": [{
                            "type": "pie", 
                            "labels": fig_data.index.tolist(),
                            "values": fig_data.values.tolist(),
                            "hole": 0.3
                        }],
                        "layout": {"title": "Points Distribution"}
                    }, use_container_width=True)
            
            st.info("💡 **Comparison Analysis**: Table shows exact values, bar chart enables metric comparison, and pie chart shows distribution.")
    
    def create_single_entity_visualization(self, data: Dict):
        """Create visualization for single entity analysis"""
        data_type = self.detect_data_type(data)
        
        if data_type == 'player_stats':
            players_data = data.get('players', [])
            if not players_data:
                return
            
            player_data = players_data[0]
            player_name = player_data.get('player,', 'Player')
            
            # Create bar chart from player metrics
            metrics_data = []
            for key, value in player_data.items():
                if key != 'player,' and isinstance(value, (int, float)) and value > 0:
                    clean_name = key.replace('Performance,', '').replace('Playing Time,', '').replace('Per 90 Minutes,', '')
                    metrics_data.append({'Metric': clean_name, 'Value': value})
            
            if metrics_data:
                df = pd.DataFrame(metrics_data).set_index('Metric')
                
                st.markdown(f"### 📊 {player_name} - Performance Breakdown")
                st.bar_chart(df)
                
                # Add goals vs assists pie chart
                pie_data = self.create_pie_chart_data(data, data_type)
                if pie_data is not None:
                    st.markdown("### 🥧 Goals vs Assists Breakdown")
                    fig_data = pie_data.set_index('Contribution')['Count']
                    st.plotly_chart({
                        "data": [{
                            "type": "pie",
                            "labels": fig_data.index.tolist(),
                            "values": fig_data.values.tolist(),
                            "hole": 0.3
                        }],
                        "layout": {"title": f"{player_name} - Goal Contributions"}
                    }, use_container_width=True)
        
        elif data_type == 'team_stats':
            teams_data = data.get('teams', [])
            if not teams_data:
                return
            
            team_data = teams_data[0]
            team_name = team_data.get('team', 'Team')
            
            # Create bar chart
            metrics_data = []
            for key, value in team_data.items():
                if key != 'team' and isinstance(value, (int, float)) and value >= 0:
                    metrics_data.append({'Metric': key, 'Value': value})
            
            if metrics_data:
                df = pd.DataFrame(metrics_data).set_index('Metric')
                
                st.markdown(f"### 📊 {team_name} - Performance Breakdown")
                st.bar_chart(df)
                
                # Add W/D/L pie chart
                pie_data = self.create_pie_chart_data(data, data_type)
                if pie_data is not None:
                    st.markdown("### 🥧 Results Distribution")
                    fig_data = pie_data.set_index('Result')['Count']
                    st.plotly_chart({
                        "data": [{
                            "type": "pie",
                            "labels": fig_data.index.tolist(),
                            "values": fig_data.values.tolist(),
                            "hole": 0.3
                        }],
                        "layout": {"title": f"{team_name} - Match Results"}
                    }, use_container_width=True)
        
        # Display detailed table
        st.markdown("### 📋 Detailed Statistics")
        if data_type == 'player_stats':
            metrics_df = pd.DataFrame([players_data[0]])
        else:
            metrics_df = pd.DataFrame([teams_data[0]])
        
        metrics_clean = self.clean_column_names(metrics_df)
        st.dataframe(metrics_clean, use_container_width=True)
        
        st.info("💡 **Single Entity Analysis**: Bar chart shows metric breakdown and pie chart displays key distributions.")
    
    def create_pie_focused_visualization(self, data: Dict):
        """Create pie-chart focused visualization"""
        data_type = self.detect_data_type(data)
        pie_data = self.create_pie_chart_data(data, data_type)
        
        if pie_data is None:
            st.warning("No suitable data found for pie chart visualization")
            return
        
        st.markdown("### 🥧 Distribution Analysis")
        
        if data_type == 'player_stats':
            if len(data.get('players', [])) == 1:
                # Goals vs Assists pie
                fig_data = pie_data.set_index('Contribution')['Count']
                st.plotly_chart({
                    "data": [{
                        "type": "pie",
                        "labels": fig_data.index.tolist(),
                        "values": fig_data.values.tolist(),
                        "hole": 0.3
                    }],
                    "layout": {"title": "Goal Contributions Distribution"}
                }, use_container_width=True)
            else:
                # Goals distribution among players
                fig_data = pie_data.set_index('Player')['Goals']
                st.plotly_chart({
                    "data": [{
                        "type": "pie",
                        "labels": fig_data.index.tolist(),
                        "values": fig_data.values.tolist(),
                        "hole": 0.3
                    }],
                    "layout": {"title": "Goals Distribution Among Players"}
                }, use_container_width=True)
        
        # Show supporting data table
        st.markdown("### 📋 Supporting Data")
        st.dataframe(pie_data, use_container_width=True)
        
        st.info("💡 **Distribution Focus**: Pie chart emphasizes proportions and relative contributions.")
    
    def render_visualization(self, query: str, response: str):
        """Main method to render enhanced visualization with pie charts"""
        
        # Check if visualization is requested
        if not self.should_create_visualization(query, response):
            return
        
        # Extract data
        data = self.parse_data_from_response(response)
        if not data:
            st.warning("No visualization data found. Ensure your query includes visualization keywords.")
            return
        
        # Determine chart type
        chart_type = self.determine_chart_type(data, query)
        if chart_type == 'none':
            return
        
        # Create visualization section
        st.markdown("---")
        st.subheader("📊 Enhanced Dynamic Visualization")
        
        # Show data summary
        data_summary = []
        for key, values in data.items():
            if values:
                data_summary.append(f"{len(values)} {key}")
        
        if data_summary:
            st.info(f"Visualizing: {', '.join(data_summary)}")
        
        # Debug option
        with st.expander("🔍 View Raw Data"):
            st.json(data)
        
        # Render appropriate visualization
        try:
            if chart_type == 'comparison':
                self.create_comparison_visualization(data)
            elif chart_type == 'single_analysis':
                self.create_single_entity_visualization(data)
            elif chart_type == 'pie_focus':
                self.create_pie_focused_visualization(data)
                
        except Exception as e:
            st.error(f"Visualization error: {e}")
            st.info("Showing raw data instead:")
            st.json(data)


# Helper function for Streamlit integration
def process_visualization_request(query: str, response: str):
    """Process and render enhanced visualization with pie charts"""
    engine = SoccerVisualizationEngine()
    engine.render_visualization(query, response)