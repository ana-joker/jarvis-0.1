import socket
import json
import threading
import time
from agent.task_queue import get_queue, TaskPriority

BRIDGE_HOST = '127.0.0.1'
BRIDGE_PORT = 8990

def start_c2_listener(speak_func=None):
    def listener_loop():
        while True:
            try:
                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client.connect((BRIDGE_HOST, BRIDGE_PORT))
                print("[C2 Listener] ✅ Connected to Albedo Bridge")
                
                while True:
                    data = client.recv(4096)
                    if not data:
                        break
                    
                    try:
                        payload = json.loads(data.decode())
                        if payload.get("type") == "task":
                            goal = payload.get("goal")
                            print(f"[C2 Listener] 📥 Received Sovereign Command: {goal}")
                            
                            queue = get_queue()
                            queue.submit(
                                goal=goal,
                                priority=TaskPriority.HIGH,
                                speak=speak_func
                            )
                            client.send(f"Task Started: {goal[:30]}".encode())
                    except Exception as e:
                        print(f"[C2 Listener] ⚠️ Protocol Error: {e}")
            
            except Exception as e:
                print(f"[C2 Listener] 🔄 Reconnecting to Albedo Bridge in 5s... ({e})")
                time.sleep(5)

    threading.Thread(target=listener_loop, daemon=True, name="AlbedoC2Listener").start()
