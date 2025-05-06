def query_arrests_by_time_period(connection, period):
    try:
        connection.send("query_arrests_by_time_period", {"time_period": period})
        response = connection.query_json_receive()
        print(f"[DEBUG] Query response: {response}")
        if "error" in response:
            return {"error": response["error"]}
        return {"data": response["data"]}
    except Exception as e:
        return {"error": str(e)}

def query_arrests_by_area(connection, area_id):
    try:
        connection.send("query_arrests_by_area", {"area_id": area_id})
        response = connection.query_json_receive()
        print(f"[DEBUG] Query response: {response}")
        if response is None:
            return {"error": "No response from server"}
        print(f"[DEBUG] Query response: {response}")
        return response
    except Exception as e:
        print(f"[ERROR] Query failed: {e}")
        return {"error": str(e)}

def query_age_distribution(connection):
    try:
        connection.send("query_age_distribution", {})
        response = connection.query_json_receive()
        print(f"[DEBUG] Query response: {response}")
        if "error" in response:
            return {"error": response["error"]}
        return {"bins": response["bins"], "counts": response["counts"]}
    except Exception as e:
        return {"error": str(e)}

def query_most_common_crime(connection, filter_value):
    try:
        connection.send("query_most_common_crime", {"filter": filter_value})
        response = connection.query_json_receive()
        if "error" in response:
            return {"error": response["error"]}
        return {"crime": response["crime"], "count": response["count"]}
    except Exception as e:
        return {"error": str(e)}