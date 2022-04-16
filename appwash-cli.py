#!/usr/bin/env python3

import requests
import sys
import os
from datetime import datetime
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

# Initialize console
console = Console()
prompt = Prompt()

logged_in = False
user_agent = "appwash-cli github.com/omfj/appwash-cli"

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
    login_response_json = login_response.json()

    # Get the token from the response, if it doesn't exist, print the error.
    try:
        console.print("Login successful.")
        logged_in = True
        login_token = login_response_json["login"]["token"]
        account_info["token"] = login_token
    except Exception:
        console.print(f"Error {login_response_json['errorCode']}: Could not get login token")

        if login_response_json["errorCode"] == 63:
            console.print("Please check your email and password.")

        exit()


def logout():
    global logged_in, account_info

    if not logged_in:
        console.print("You are already logged out.")
        return

    logged_in = False
    account_info = {}
    console.print("You are now logged out.")


def get_machines():
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
        return

    return machine_data

def print_machines():
    if not logged_in:
        console.print("You are not logged in.")
        return

    machine_data = get_machines()

    for machine in machine_data:
        machine_id = machine["externalId"]
        machine_state = machine["state"]
        if machine_state in ["OCCUPIED", "STOPPABLE"]:
            last_session_start = machine["lastSessionStart"]
            last_session_start = datetime.fromtimestamp(last_session_start).strftime("%Y-%m-%d %H:%M:%S")

            if machine_state == "STOPPABLE":
                console.print(f"-> {machine_id} - [bold green]{machine_state}[/bold green] - STARTED: {last_session_start}")
            else:
                console.print(f"{machine_id} - {machine_state} - STARTED: {last_session_start}")
        else:
            console.print(f"{machine_id} - {machine_state}")



def reserve_machine():
    if not logged_in:
        console.print("You are not logged in.")
        return

    console.print("What machine do you want to reserve?")
    machine_id = prompt.ask("Machine ID")

    are_you_sure = prompt.ask("Are you sure you want to reserve machine {machine_id}? (y/N)")

    if not are_you_sure == "y":
        return

    reserve_machine_headers = { 'User-Agent': f"{user_agent}", 'Referer': 'https://appwash.com/', 'language': 'NO', 'token': f"{account_info['token']}", 'platform': 'appWash', 'Origin': 'https://appwash.com', 'DNT': '1' }
    reserve_machine_json_data = { 'objectId': None, 'objectLength': None, 'objectName': None, 'nrOfPersons': None, 'freeFormQuestionValue': None, 'comment': None, 'sourceChannel': 'WEBSITE' }
    reserve_machine_response = requests.post(f'https://www.involtum-services.com/api-rest/connector/{machine_id}/start', headers=reserve_machine_headers, json=reserve_machine_json_data)

    error_code = reserve_machine_response.json()["errorCode"]

    if error_code == 0:
        console.print(f"Successfully reserved machine {machine_id}")
    else:
        console.print(f"Error {error_code}: Could not reserve machine {machine_id}")


def stop_machine():
    if not logged_in:
        console.print("You are not logged in.")
        return

    console.print("What machine do you want to stop?")
    machine_id = prompt.ask("Machine ID")

    are_you_sure = prompt.ask("Are you sure you want to stop machine {machine_id}? (y/N)")

    if not are_you_sure == "y":
        return

    reserve_machine_headers = { 'User-Agent': f"{user_agent}", 'Referer': 'https://appwash.com/', 'language': 'NO', 'token': f"{account_info['token']}", 'platform': 'appWash', 'Origin': 'https://appwash.com', 'DNT': '1' }
    reserve_machine_json_data = { 'objectId': None, 'objectLength': None, 'objectName': None, 'nrOfPersons': None, 'freeFormQuestionValue': None, 'comment': None, 'sourceChannel': 'WEBSITE' }
    reserve_machine_response = requests.post(f'https://www.involtum-services.com/api-rest/connector/{machine_id}/stop', headers=reserve_machine_headers, json=reserve_machine_json_data)

    error_code = reserve_machine_response.json()["errorCode"]
    print(reserve_machine_response.json())

    if error_code == 0:
        console.print(f"Successfully stopped machine {machine_id}")
    else:
        console.print(f"Error {error_code}: Could not stop machine {machine_id}")


def print_balance():
    if not logged_in:
        console.print("You are not logged in.")
        return


    balance_headers = { 'User-Agent': f"{user_agent}", 'Referer': 'https://appwash.com/', 'token': f"{account_info['token']}", 'language': 'NO', 'platform': 'appWash', 'Origin': 'https://appwash.com', 'DNT': '1' }

    response = requests.get('https://www.involtum-services.com/api-rest/account/getprepaid', headers=balance_headers)
    response_json = response.json()

    error_code = response_json["errorCode"]

    if error_code == 0:
        balance = response_json["balanceCents"] / 100
        currency = response_json["currency"]

        console.print(f"Your balance is {balance} {currency}.")
    else:
        console.print(f"Error {error_code}: Could not get balance.")


def get_history():
    history_headers = { 'User-Agent': f"{user_agent}", 'Referer': 'https://appwash.com/', 'token': f"{account_info['token']}", 'language': 'NO', 'platform': 'appWash', 'Origin': 'https://appwash.com', 'DNT': '1' }

    history_response = requests.get('https://www.involtum-services.com/api-rest/account/getprepaidmutations', headers=history_headers)

    try:
        print("Successfully fetched purchase history.", end="\n\n")
        purchase_history = history_response.json()
    except Exception:
        print(f"Error {data_response.status_code}: Could not get machine list", end="\n\n")
        return

    return purchase_history


def print_history():
    if not logged_in:
        console.print("You are not logged in.")
        return

    purchase_history = get_history()

    purchase_history_table = Table(title="Purchase history")
    purchase_history_table.add_column("Description", justify="center")
    purchase_history_table.add_column("Date",        justify="center")
    purchase_history_table.add_column("Amount",      justify="center")
    purchase_history_table.add_column("Bal. Before", justify="center")
    purchase_history_table.add_column("Bal. After",  justify="center")

    for purchase_info in purchase_history["data"]:
        time = str(datetime.fromtimestamp(purchase_info["mutationTimestamp"]).strftime("%Y-%m-%d %H:%M:%S"))
        currency = purchase_info["currency"]
        amount = str(purchase_info["mutationCents"] / 100)
        balance_before = str(purchase_info["balanceCentsBefore"] / 100)
        balance_after = str(purchase_info["balanceCentsAfter"] / 100)
        description = purchase_info["mutationDescription"].capitalize()

        purchase_history_table.add_row(description, time, f"{amount} {currency}", balance_before, balance_after)

    console.print(purchase_history_table)

def print_help():
    console.print("Available commands:")
    console.print("'list'    - List all machines")
    console.print("'stop'    - Stop the program")
    console.print("'restart' - Restarts the program")
    console.print("'help'    - Print this help")
    console.print("'whoami'  - Print your account information")
    console.print("'login'   - Login to the appwash service")
    console.print("'reserve' - Reserve a machine")
    console.print("'stop' .  - Stops a machine")
    console.print("'balance' - Print your balance")
    console.print("'history' - Print your purchase history")
    console.print("'clear'   - Clears the screen")


def restart():
    os.execv(sys.argv[0], sys.argv)


def clear():
    os.system("clear")


def exec_command(command):
    try:
        command, *args = command.split()
    except Exception:
        command = command
        args = []

    match (command):
        case "list":
            print_machines()
        case "exit" | "quit" | "q" | "e":
            print("Bye bye!")
            exit()
        case "restart" | "r":
            restart()
        case "clear":
            clear()
        case "help":
            print_help()
        case "reserve" | "re":
            reserve_machine()
        case "stop" | "s":
            stop_machine()
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
        case "logout":
            logout()
        case "balance" | "bal":
            print_balance()
        case "history" | "h":
            print_history()
        case _:
            console.print("Unknown command")


def main():
    console.print("Welcome to AppWash CLI!", style="bold green")
    console.print("Type 'help' for commands.", end="\n\n")
    while (command := input(f">>> ")):
        exec_command(command)
        print() # For new line after executed command


if __name__ == "__main__":
    main()