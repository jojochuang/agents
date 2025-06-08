import os
import requests
import json

# --- Configuration ---
# The Jira instance URL is hardcoded here.
JIRA_URL = "https://issues.apache.org/jira"
# The Personal Access Token (PAT) is read from an environment variable.
# Before running, ensure you have set it, e.g., 'export JIRA_API_TOKEN=your_token_here'
JIRA_API_TOKEN = os.environ.get("JIRA_API_TOKEN")

def add_user_to_jira_role(user_to_add, project_key):
    """
    Adds a specified user to the 'Contributors' role in a Jira project.

    This function fetches available roles for a project, finds the 'Contributors'
    role, and then adds the specified user to that role.

    Args:
        user_to_add (str): The username of the user to add to the role.
        project_key (str): The key of the project (e.g., HDDS).

    Returns:
        bool: True if the user was added successfully, False otherwise.
    """
    if not JIRA_API_TOKEN:
        print("Error: JIRA_API_TOKEN environment variable is not set.")
        print("Please export your Personal Access Token before running the script.")
        return False

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {JIRA_API_TOKEN}"
    }
    
    # --- 1. Fetch Roles and Find the 'Contributors' Role ID ---
    roles_url = f"{JIRA_URL}/rest/api/2/project/{project_key}/role"
    print(f"Fetching roles for project '{project_key}' to find 'Contributors'...")
    
    contributor_role_id = None
    try:
        # Note: The 'auth' parameter is removed, authentication is now in the header.
        response = requests.get(roles_url, headers=headers)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)

        roles = response.json()
        if not roles:
            print("No roles found for this project.")
            return False

        # Find the ID for the 'Contributors' role
        for role_name, role_url in roles.items():
            if role_name == 'Contributors':
                contributor_role_id = role_url.split('/')[-1]
                print(f"Found 'Contributors' role with ID: {contributor_role_id}")
                break
        
        if not contributor_role_id:
            print(f"Error: Could not find a role named 'Contributors' in project '{project_key}'.")
            print("Available roles:", ", ".join(roles.keys()))
            return False

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        if response.status_code == 404:
            print(f"Error: Project with key '{project_key}' not found.")
        elif response.status_code in [401, 403]:
             print("Error: Authentication or Permission issue. Please check your Personal Access Token and your account permissions on Jira.")
        # Print the detailed error message from Jira's response
        if response.text:
            print("Jira response:", response.text)
        return False
    except requests.exceptions.RequestException as err:
        print(f"An error occurred: {err}")
        return False

    # --- 2. Add User to the 'Contributors' Role ---
    add_user_url = f"{JIRA_URL}/rest/api/2/project/{project_key}/role/{contributor_role_id}"
    payload = json.dumps({"user": [user_to_add]})

    print(f"\nAdding user '{user_to_add}' to 'Contributors' role (ID: {contributor_role_id}) in project '{project_key}'...")

    try:
        response = requests.post(add_user_url, data=payload, headers=headers)
        response.raise_for_status()
        
        print(f"Successfully added user '{user_to_add}' to the 'Contributors' role.")
        return True

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        print(f"Error: Failed to add user. Status Code: {response.status_code}")
        print("Please check the user, project key, and role ID.")
        # Print more details from Jira's response if available
        if response.text:
            print("Jira response:", response.text)
        return False
    except requests.exceptions.RequestException as err:
        print(f"An error occurred: {err}")
        return False


if __name__ == "__main__":
    """
    This block runs when the script is executed directly from the command line.
    It prompts the user for the necessary information and calls the main function.
    """
    print("--- Jira User Role Assignment Script ---")
    print(f"Using Jira instance: {JIRA_URL}")
    
    # --- Get User Input ---
    username_to_add = input("Enter the username to add: ")
    project_key_input = input("Enter the project key (e.g., HDDS): ")
    
    print("-" * 35)

    # --- Execute the Function ---
    add_user_to_jira_role(username_to_add, project_key_input)

