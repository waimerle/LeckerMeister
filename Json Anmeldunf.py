import json
import os

def save_user(username, user_data, directory='users'):
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    filename = os.path.join(directory, f"{username}.json")
    with open(filename, 'w') as file:
        json.dump(user_data, file, indent=4)
    print(f"User data for {username} saved successfully in {filename}.")

def add_user(username, email, age, directory='users'):
    user_data = {
        'username': username,
        'email': email,
        'age': age
    }
    save_user(username, user_data, directory)

def main():
    while True:
        username = input("Enter username: ")
        email = input("Enter email: ")
        age = int(input("Enter age: "))
        
        add_user(username, email, age)
        
        another = input("Do you want to add another user? (yes/no): ")
        if another.lower() != 'yes':
            break

if __name__ == "__main__":
    main()
