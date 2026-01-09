import os

todos = []

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def show_todos():
    if not todos:
        print("No todos yet!")
        return
    print("\nYour Todos:")
    for i, t in enumerate(todos, 1):
        print(f"{i}. {t}")
    print()

def add_todo():
    todo = input("Enter a new todo: ").strip()
    if todo:
        todos.append(todo)
        print(f"Added: {todo}")
    else:
        print("Nothing added!")

def delete_todo():
    show_todos()
    try:
        idx = int(input("Enter number to delete: "))
        removed = todos.pop(idx-1)
        print(f"Removed: {removed}")
    except (IndexError, ValueError):
        print("Invalid number!")

def main():
    while True:
        print("\nOptions:")
        print("1. Show Todos")
        print("2. Add Todo")
        print("3. Delete Todo")
        print("4. Quit")

        choice = input("Choose option: ").strip()
        if choice == "1":
            show_todos()
        elif choice == "2":
            add_todo()
        elif choice == "3":
            delete_todo()
        elif choice == "4":
            print("Bye!")
            break
        else:
            print("Invalid option, try again.")

if __name__ == "__main__":
    clear_screen()
    main()
