import networkx as nx
from typing import Dict, Any

def create_session_graph(session_data: Dict[str, Any]) -> nx.DiGraph:
    """
    Create a directed graph from session data.
    
    Parameters:
    -dict:
      - "queries": a list of query nodes. Each node should be a dict with at least:
          - "queryId": a unique identifier for the query.
          - "text": the query text.
          - "timestamp": the time when the query was submitted.
      - "transitions": a list of transitions between queries. Each transition should be a dict with:
          - "from": source queryId.
          - "to": destination queryId.
          - "count": frequency of this transition.
          - "timeDifference": time difference (in minutes) between queries.
          - "weight": computed weight (possibly with decay).
    
    Returns:
    - nx.DiGraph:
        - Nodes represent queries with their attributes.
        - Edges represent transitions with attributes "count", "timeDifference", and "weight".
    """
    graph = nx.DiGraph()

    # Add query nodes to the graph
    for query in session_data.get("queries", []):
        query_id = query.get("queryId")
        # Add node with attributes (text and timestamp)
        graph.add_node(query_id, text=query.get("text"), timestamp=query.get("timestamp"))
    
    # Add transitions as edges between query nodes
    for transition in session_data.get("transitions", []):
        source = transition.get("from")
        target = transition.get("to")
        # Add edge with transition attributes (count, timeDifference, weight)
        graph.add_edge(source, target, 
                         count=transition.get("count", 1),
                         timeDifference=transition.get("timeDifference"),
                         weight=transition.get("weight"))
    
    return graph

# Example usage:
if __name__ == "__main__":
    # Sample session data (from your provided example)
    sample_session = {
        "sessionId": "session_20250407_user001_1",
        "userId": "user001",
        "startTime": "2025-04-07T09:30:00Z",
        "endTime": "2025-04-07T10:15:00Z",
        "queries": [
            {"queryId": "q1", "text": "organic baby clothes", "timestamp": "2025-04-07T09:30:00Z"},
            {"queryId": "q2", "text": "aden + anais swaddles", "timestamp": "2025-04-07T09:42:00Z"},
            {"queryId": "q3", "text": "handmade nursery decor", "timestamp": "2025-04-07T10:05:00Z"}
        ],
        "transitions": [
            {"from": "q1", "to": "q2", "count": 1, "timeDifference": 12, "weight": 0.61},
            {"from": "q2", "to": "q3", "count": 1, "timeDifference": 23, "weight": 0.42}
        ]
    }
    
    sg = create_session_graph(sample_session)
    print("Nodes in the session graph:", sg.nodes(data=True))
    print("Edges in the session graph:", list(sg.edges(data=True)))
