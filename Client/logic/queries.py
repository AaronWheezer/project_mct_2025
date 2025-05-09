def query_arrests_by_descent(connection, descent_code, user_id):
    """Request the number of arrests for a specific descent."""
    try:
        connection.send("query_arrests_by_descent", {"user_id": user_id, "descent_code": descent_code})
        response = connection.query_json_receive()
        if "error" in response:
            return {"error": response["error"]}
        return response
    except Exception as e:
        return {"error": str(e)}
def query_arrests_by_area(connection, area_id, user_id):
    try:
        connection.send("query_arrests_by_area", {"user_id": user_id,"area_id": area_id})
        response = connection.query_json_receive()
        print(f"[DEBUG] Query response: {response}")
        if response is None:
            return {"error": "No response from server"}
        print(f"[DEBUG] Query response: {response}")
        return response
    except Exception as e:
        print(f"[ERROR] Query failed: {e}")
        return {"error": str(e)}

def query_age_distribution(connection, user_id):
    try:
        connection.send("query_age_distribution", {"user_id": user_id})
        response = connection.query_json_receive()
        print(f"[DEBUG] Query response: {response}")
        if "error" in response:
            return {"error": response["error"]}
        return {"bins": response["bins"], "counts": response["counts"]}
    except Exception as e:
        return {"error": str(e)}

def query_most_common_crime(connection, filter_value , user_id):
    try:
        connection.send("query_most_common_crime", {"user_id": user_id,"filter": filter_value})
        response = connection.query_json_receive()
        if "error" in response:
            return {"error": response["error"]}
        return {"crime": response["crime"], "count": response["count"]}
    except Exception as e:
        return {"error": str(e)}