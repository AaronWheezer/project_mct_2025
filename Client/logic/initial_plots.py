import json

def fetch_initial_plots(connection):
    try:
        #send so server knows what we want
        # Send request to server for initial plots
        connection.send("get_initial_plots", {})

        buffer = b""  
        while True:
            chunk = connection.receive()  
            if not chunk:
                break  # No more data or disconnected

            buffer += chunk  
            if len(buffer) >= 4:
                num_plots = int.from_bytes(buffer[:4], 'big') 
                buffer = buffer[4:] 

                plot_paths = []
                while len(plot_paths) < num_plots:
                    if len(buffer) >= 4:
                        path_len = int.from_bytes(buffer[:4], 'big')
                        buffer = buffer[4:]  

                        if len(buffer) >= path_len:
                            plot_path = buffer[:path_len].decode('utf-8') 
                            plot_paths.append(plot_path)
                            buffer = buffer[path_len:]  
                return plot_paths

    except Exception as e:
        print(f"[ERROR] Failed to fetch plot paths: {e}")
        return []
