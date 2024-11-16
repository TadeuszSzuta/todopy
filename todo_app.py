import requests
import time
from signalr import Connection


HUB_URL = "http://localhost:7203/todoHub"
API_URL = "http://localhost:7203/todoitems"

def on_todos_updated():
    print("Todos updated!")
    print_todos()

# Tworzenie połączenia SignalR
def start_signalr_connection():
    connection = Connection(HUB_URL)

    # Rejestracja funkcji callback do nasłuchiwania aktualizacji
    connection.on('TodosUpdated', on_todos_updated)

    # Rozpoczęcie połączenia
    connection.start()

    try:
        while True:
            time.sleep(1)  # Pętla do nasłuchiwania
    except KeyboardInterrupt:
        print("Stopping SignalR connection...")
        connection.stop()

# Komunikacja z REST API
def get_todos():
    try:
        response = requests.get(API_URL)
        response.raise_for_status()  # Sprawdzanie błędów HTTP
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching todos: {e}")
        return []

def add_todo(name):
    todo = {"name": name, "isComplete": False}
    try:
        response = requests.post(API_URL, json=todo)
        response.raise_for_status()
        print(f"Todo '{name}' added successfully")
    except requests.exceptions.RequestException as e:
        print(f"Error adding todo: {e}")

def delete_todo(todo_id):
    try:
        response = requests.delete(f"{API_URL}/{todo_id}")
        response.raise_for_status()
        print(f"Todo with id {todo_id} deleted successfully")
    except requests.exceptions.RequestException as e:
        print(f"Error deleting todo: {e}")

def toggle_complete(todo_id):
    # First get the todo
    try:
        todo = requests.get(f"{API_URL}/{todo_id}").json()
        todo['isComplete'] = not todo['isComplete']

        response = requests.put(f"{API_URL}/{todo_id}", json=todo)
        response.raise_for_status()
        print(f"Todo with id {todo_id} updated successfully")
    except requests.exceptions.RequestException as e:
        print(f"Error updating todo: {e}")

def print_todos():
    todos = get_todos()
    print("\nCurrent Todo List:")
    for todo in todos:
        print(f"{todo['id']}. {todo['name']} - {'Completed' if todo['isComplete'] else 'Incomplete'}")

def user_input():
    while True:
        action = input("\nChoose action (add, delete, toggle, exit): ")
        if action == "add":
            name = input("Enter todo name: ")
            add_todo(name)
        elif action == "delete":
            todo_id = int(input("Enter todo id to delete: "))
            delete_todo(todo_id)
        elif action == "toggle":
            todo_id = int(input("Enter todo id to toggle: "))
            toggle_complete(todo_id)
        elif action == "exit":
            print("Exiting program...")
            break

if __name__ == "__main__":
    # Start SignalR connection in a separate thread or process
    import threading
    signalr_thread = threading.Thread(target=start_signalr_connection, daemon=True)
    signalr_thread.start()

    # Main application loop for user input
    print_todos()
    user_input()
