"""
Monday.com GraphQL query templates
"""

QUERIES = {
    "get_board_items": """
        query GetBoardItems($board_id: [ID!]!, $limit: Int!) {
          boards(ids: $board_id) {
            id
            name
            items_page(limit: $limit) {
              cursor
              items {
                id
                name
                column_values {
                  id
                  title
                  text
                  value
                  type
                }
              }
            }
          }
        }
    """,
    
    "get_next_items": """
        query GetNextItems($cursor: String!, $limit: Int!) {
          next_items_page(cursor: $cursor, limit: $limit) {
            cursor
            items {
              id
              name
              column_values {
                id
                title
                text
                value
                type
              }
            }
          }
        }
    """,
    
    "get_board_columns": """
        query GetBoardColumns($board_id: [ID!]!) {
          boards(ids: $board_id) {
            id
            name
            columns {
              id
              title
              type
              settings_str
            }
          }
        }
    """,
    
    "health_check": """
        query HealthCheck($board_id: [ID!]!) {
          boards(ids: $board_id) {
            id
            name
          }
        }
    """
}
