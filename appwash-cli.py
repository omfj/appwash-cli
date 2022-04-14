import requests
from datetime import datetime
from rich.console import Console
from rich.prompt import Prompt

# Functions
# =========
# login
# print_help
# print_machines
# print_whoami


# Initialize console
console = Console()
prompt = Prompt()

logged_in = False
user_agent = "appwash cli github.com/omfj/appwash-cli"

def print_whoami(secrets=False):
    try:
        console.print(f"'Account': {account_info['email']}")
        if secrets:
            console.print(f"'Password': {account_info['password']}")
            console.print(f"'Token': {account_info['token']}")
        else:
            console.print("Add '--secrets' to see the password and token.")
    except NameError:
        console.print("You are not logged in.")


def login(*args):
    global account_info, logged_in

    if logged_in:
        console.print("You are already logged in.")
        re_login = input("Do you want to re-login? (y/N): ")

    if not logged_in or re_login == "y":
        try:
            email = args[0]
            password = args[1]
        except IndexError:
            email = prompt.ask("Email")
            password = prompt.ask("Password", password=True)

    # Headers for request
    login_headers = { "Content-Type": "application/json", "User-Agent": f"{user_agent}", "language": "en", "platform": "appWash" }

    # Login data
    account_info = { "email": email, "password": password }
    login_data = f'{{ "email": "{account_info["email"]}", "password": "{account_info["password"]}" }}'

    # Get the login token
    login_response = requests.post("https://www.involtum-services.com/api-rest/login", headers=login_headers, data=login_data, verify=True)

    # Get the token from the response, if it doesn't exist, print the error.
    try:
        console.print("Login successful.")
        logged_in = True
        login_response_json = login_response.json()
        login_token = login_response_json["login"]["token"]
        account_info["token"] = login_token
    except Exception:
        console.print(f"Error {login_response.status_code}: Could not get login token")
        exit()


def print_machines():

    if not logged_in:
        console.print("You are not logged in.")
        return

    # Login headers
    headers = { "User-Agent": f"{user_agent}", "Referer": "https://appwash.com/", "token": f"{account_info['token']}", "language": "NO", "platform": "appWash", "DNT": "1" }
    json_data = { "serviceType": "WASHING_MACHINE" }

    # Get machine list
    data_response = requests.post("https://www.involtum-services.com/api-rest/location/9944/connectorsv2", headers=headers, json=json_data, verify=True)

    # Get the machine list from the response, if it doesn't exist, print the error.
    try:
        print("Successfully fetched machine list", end="\n\n")
        data_response_json = data_response.json()
        machine_data = data_response_json["data"]
    except Exception:
        print(f"Error {data_response.status_code}: Could not get machine list", end="\n\n")
        exit()

    # Print all machines in the list
    for machine in machine_data:
        machine_id = machine["externalId"]
        machine_state = machine["state"]
        if machine_state == "OCCUPIED":
            last_session_start = machine["lastSessionStart"]
            last_session_start = datetime.fromtimestamp(last_session_start).strftime("%Y-%m-%d %H:%M:%S")
            console.print(f"{machine_id} - {machine_state} - STARTED: {last_session_start}")
        else:
            console.print(f"{machine_id} - {machine_state}")


def print_help():
    console.print("Available commands:")
    console.print("'list' - List all machines")
    console.print("'stop' - Stop the program")
    console.print("'help' - Print this help")
    console.print("'whoami' - Print your account information")
    console.print("'login' - Login to the appwash service")


def exec_command(command):

    try:
        command, *args = command.split()
    except Exception:
        command = command
        args = []

    match (command):
        case "list":
            print_machines()
        case "stop" | "exit" | "quit" | "q" | "e":
            print("Bye bye!")
            exit()
        case "help":
            print_help()
        case "whoami":
            if "--secrets" in args:
                print_whoami(True)
            else:
                print_whoami()
        case "login":
            try:
                login(args[0], args[1])
            except IndexError:
                login()
        case _:
            console.print("Unknown command")


def main():
    while (command := input(f">>> ")):
        exec_command(command)


if __name__ == "__main__":
    main()