#!/usr/bin/env python
"""
Simplified pathfinding comparison test.
Compares Dijkstra algorithm against Hill Climbing algorithm using actual map data.
"""
import os
import sys
import django
import csv
import matplotlib.pyplot as plt
import numpy as np
import signal
from typing import List, Dict, Tuple

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agv_server.settings')
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
django.setup()

from agv_data.pathfinding.factory import PathfindingFactory


def load_map_from_csv(csv_file_path: str) -> Tuple[List[int], List[Dict]]:
    """Load map data from CSV file and convert to nodes and connections format."""
    nodes = []
    connections = []
    
    with open(csv_file_path, 'r') as file:
        reader = csv.reader(file)
        matrix = list(reader)
    
    # Convert to integer matrix
    int_matrix = []
    for row in matrix:
        int_row = [int(val) for val in row]
        int_matrix.append(int_row)
    
    # Generate nodes (1-indexed)
    num_nodes = len(int_matrix)
    nodes = list(range(1, num_nodes + 1))
    
    # Generate connections from matrix
    for i in range(num_nodes):
        for j in range(num_nodes):
            if i != j and int_matrix[i][j] != 10000:  # 10000 means no connection
                connections.append({
                    'node1': i + 1,  # Convert to 1-indexed
                    'node2': j + 1,
                    'distance': int_matrix[i][j]
                })
    
    return nodes, connections


def calculate_path_cost(path: List[int], connections: List[Dict]) -> float:
    """Calculate the total cost of a path."""
    if len(path) < 2:
        return 0
    
    # Build distance lookup
    distance_lookup = {}
    for conn in connections:
        key1 = (conn['node1'], conn['node2'])
        key2 = (conn['node2'], conn['node1'])
        distance_lookup[key1] = conn['distance']
        distance_lookup[key2] = conn['distance']
    
    total_cost = 0
    for i in range(len(path) - 1):
        key = (path[i], path[i + 1])
        if key in distance_lookup:
            total_cost += distance_lookup[key]
        else:
            return float('inf')  # Invalid path
    
    return total_cost


def generate_test_cases(nodes: List[int], num_tests: int = 20) -> List[Tuple[int, int]]:
    """Generate random test cases for pathfinding."""
    import random
    test_cases = []
    
    # Ensure we have enough nodes
    if len(nodes) < 2:
        return test_cases
    
    for _ in range(num_tests):
        start = random.choice(nodes)
        end = random.choice([n for n in nodes if n != start])
        test_cases.append((start, end))
    
    return test_cases


def signal_handler(signum, frame):
    """Handle Ctrl+C signal."""
    print("\nReceived interrupt signal. Cleaning up...")
    plt.close('all')
    sys.exit(0)


def run_comparison_test():
    """Run the pathfinding comparison test."""
    print("Starting Dijkstra vs Hill Climbing Algorithm Comparison")
    print("=" * 60)
    # Load map data
    csv_file_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'sample-data', 'map-connection-and-distance.csv'
    )
    
    if not os.path.exists(csv_file_path):
        print(f"Error: Map file not found at {csv_file_path}")
        return
    
    print(f"Loading map data from: {csv_file_path}")
    nodes, connections = load_map_from_csv(csv_file_path)
    
    print(f"Map loaded: {len(nodes)} nodes, {len(connections)} connections")
      # Initialize algorithms
    dijkstra = PathfindingFactory.get_algorithm("dijkstra", nodes, connections)
    hill_climbing = PathfindingFactory.get_algorithm("hill_climbing", nodes, connections)
    
    # Generate test cases
    test_cases = generate_test_cases(nodes, 30)
    print(f"Generated {len(test_cases)} test cases")    # Results storage
    results = {
        'dijkstra': {'success': 0, 'total_cost': 0, 'paths': []},
        'hill_climbing': {'success': 0, 'total_cost': 0, 'paths': []}
    }
    
    # Track path optimality comparison
    optimality_comparison = {
        'dijkstra_wins': 0,
        'hill_climbing_wins': 0,
        'ties': 0,
        'both_found_path': 0
    }
    
    # Run tests
    print("\nRunning pathfinding tests...")
    
    valid_tests = 0
    
    for i, (start, end) in enumerate(test_cases):
        print(f"Test {i+1}: Finding path from node {start} to node {end}")
        
        # Test Dijkstra
        dijkstra_path = dijkstra.find_shortest_path(start, end)
        dijkstra_cost = calculate_path_cost(dijkstra_path, connections) if dijkstra_path else float('inf')
          # Test Hill Climbing
        hill_climbing_path = hill_climbing.find_shortest_path(start, end)
        hill_climbing_cost = calculate_path_cost(hill_climbing_path, connections) if hill_climbing_path else float('inf')
          # Only count tests where at least one algorithm found a path
        if dijkstra_path or hill_climbing_path:
            valid_tests += 1
            
            if dijkstra_path and dijkstra_cost != float('inf'):
                results['dijkstra']['success'] += 1
                results['dijkstra']['total_cost'] += dijkstra_cost
                results['dijkstra']['paths'].append(dijkstra_path)
                print(f"  Dijkstra: Found path with cost {dijkstra_cost}")
            else:
                print(f"  Dijkstra: No path found")
            
            if hill_climbing_path and hill_climbing_cost != float('inf'):
                results['hill_climbing']['success'] += 1
                results['hill_climbing']['total_cost'] += hill_climbing_cost
                results['hill_climbing']['paths'].append(hill_climbing_path)
                print(f"  Hill Climbing: Found path with cost {hill_climbing_cost}")
            else:
                print(f"  Hill Climbing: No path found")            # Compare results
            if dijkstra_path and hill_climbing_path:
                optimality_comparison['both_found_path'] += 1
                if dijkstra_cost < hill_climbing_cost:
                    optimality_comparison['dijkstra_wins'] += 1
                    print(f"  → Dijkstra wins (cost: {dijkstra_cost} vs {hill_climbing_cost})")
                elif hill_climbing_cost < dijkstra_cost:
                    optimality_comparison['hill_climbing_wins'] += 1
                    print(f"  → Hill Climbing wins (cost: {hill_climbing_cost} vs {dijkstra_cost})")
                else:
                    optimality_comparison['ties'] += 1
                    print(f"  → Tie (both found cost: {dijkstra_cost})")
        
        print()
    
    # Calculate statistics
    print("=" * 60)
    print("FINAL RESULTS")
    print("=" * 60)
    
    dijkstra_success_rate = (results['dijkstra']['success'] / valid_tests) * 100 if valid_tests > 0 else 0
    hill_climbing_success_rate = (results['hill_climbing']['success'] / valid_tests) * 100 if valid_tests > 0 else 0
    
    # Calculate path optimality rates
    dijkstra_optimality_rate = (optimality_comparison['dijkstra_wins'] / optimality_comparison['both_found_path']) * 100 if optimality_comparison['both_found_path'] > 0 else 0
    hill_climbing_optimality_rate = (optimality_comparison['hill_climbing_wins'] / optimality_comparison['both_found_path']) * 100 if optimality_comparison['both_found_path'] > 0 else 0
    tie_rate = (optimality_comparison['ties'] / optimality_comparison['both_found_path']) * 100 if optimality_comparison['both_found_path'] > 0 else 0
    
    print(f"Total valid tests: {valid_tests}")
    print(f"Tests where both algorithms found paths: {optimality_comparison['both_found_path']}")
    print(f"\nDijkstra Algorithm:")
    print(f"  Success rate: {dijkstra_success_rate:.1f}% ({results['dijkstra']['success']}/{valid_tests})")
    print(f"  Path optimality rate: {dijkstra_optimality_rate:.1f}% ({optimality_comparison['dijkstra_wins']}/{optimality_comparison['both_found_path']})")
    
    print(f"\nHill Climbing Algorithm:")
    print(f"  Success rate: {hill_climbing_success_rate:.1f}% ({results['hill_climbing']['success']}/{valid_tests})")
    print(f"  Path optimality rate: {hill_climbing_optimality_rate:.1f}% ({optimality_comparison['hill_climbing_wins']}/{optimality_comparison['both_found_path']})")
    
    print(f"\nTied results: {tie_rate:.1f}% ({optimality_comparison['ties']}/{optimality_comparison['both_found_path']})")
    
    # Create visualization
    create_comparison_chart(dijkstra_success_rate, hill_climbing_success_rate, 
                          dijkstra_optimality_rate, hill_climbing_optimality_rate)


def create_comparison_chart(dijkstra_success, hill_climbing_success, 
                          dijkstra_optimality, hill_climbing_optimality):
    """Create a bar chart comparing the algorithms."""
    
    # Create figure with subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
    
    # Success Rate Chart
    algorithms = ['Dijkstra', 'Hill Climbing']
    success_rates = [dijkstra_success, hill_climbing_success]
    
    bars1 = ax1.bar(algorithms, success_rates, color=['#2E8B57', '#CD5C5C'])
    ax1.set_ylabel('Success Rate (%)')
    ax1.set_title('Path Finding Success Rate')
    ax1.set_ylim(0, 100)
    
    # Add value labels on bars
    for bar, value in zip(bars1, success_rates):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{value:.1f}%', ha='center', va='bottom')
    
    # Path Optimality Chart
    optimality_rates = [dijkstra_optimality, hill_climbing_optimality]
    bars2 = ax2.bar(algorithms, optimality_rates, color=['#2E8B57', '#CD5C5C'])
    ax2.set_ylabel('Path Optimality Rate (%)')
    ax2.set_title('Path Optimality (Higher is Better)')
    ax2.set_ylim(0, 100)
    
    # Add value labels on bars
    for bar, value in zip(bars2, optimality_rates):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{value:.1f}%', ha='center', va='bottom')
    
    plt.tight_layout()
      # Save the chart
    output_path = 'pathfinding_comparison.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\nComparison chart saved as: {output_path}")
    
    # Show the chart with timeout or keyboard interrupt handling
    print("Chart is displayed. Press Ctrl+C to exit or close the chart window.")
    try:
        plt.show(block=False)  # Non-blocking show
        plt.pause(0.1)  # Small pause to ensure chart is displayed
        
        # Keep the script alive until user interrupts or closes chart
        while plt.get_fignums():  # Check if any figures are still open
            plt.pause(1)  # Wait 1 second between checks
            
    except KeyboardInterrupt:
        print("\nExiting... Chart window will be closed.")
        plt.close('all')
    except Exception as e:
        print(f"\nChart display error: {e}")
        plt.close('all')


if __name__ == "__main__":
    # Set up signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        run_comparison_test()
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
        plt.close('all')
        sys.exit(0)
    except Exception as e:
        print(f"\nError during test execution: {e}")
        plt.close('all')
        sys.exit(1)
