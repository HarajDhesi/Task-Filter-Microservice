"""
Task Filter Service Test Suite

This test suite validates the Task Filter microservice which handles:
1. Filtering tasks by various criteria (priority, completion status, due date)
2. Saving and managing filter preferences
3. Retrieving and clearing saved preferences

Microservice Endpoints Tested:
-----------------------------
Task Filter Service (http://localhost:5003):
    - GET /filter_tasks: Filters tasks based on query parameters
    - POST /save_filter_preferences: Saves user's filter preferences
    - GET /get_saved_preferences: Retrieves saved filter preferences
    - POST /clear_preferences: Clears all saved filter preferences
"""

import requests
import json
from datetime import datetime, timedelta
from colorama import init, Fore, Style

# Initialize colorama for Windows compatibility
init()

# Base URL for task filter service
BASE_URL = "http://localhost:5003"

def print_test_result(passed: bool, test_name: str):
    """Helper function to print test results"""
    if passed:
        print(f"{Fore.GREEN}[PASS] {test_name}{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}[FAIL] {test_name}{Style.RESET_ALL}")

def validate_service():
    """Validate task_filter service is accessible"""
    print(f"\n{Fore.CYAN}=== Validating Service ==={Style.RESET_ALL}")
    try:
        response = requests.get(f"{BASE_URL}/filter_tasks")
        if response.ok:
            print(f"{Fore.GREEN}✓ Task Filter service is accessible{Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.RED}✗ Task Filter service returned error: {response.status_code}{Style.RESET_ALL}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"{Fore.RED}✗ Cannot connect to Task Filter service at {BASE_URL}{Style.RESET_ALL}")
        return False

def test_filter_tasks():
    """Tests the task filtering functionality"""
    print(f"\n{Fore.CYAN}=== Testing Filter Tasks Endpoint ==={Style.RESET_ALL}")
    all_tests_passed = True
    
    # Test 1: Filter by priority (high)
    print(f"\n{Fore.YELLOW}Test 1: Filter by priority (high){Style.RESET_ALL}")
    response = requests.get(f"{BASE_URL}/filter_tasks", params={"priority": "high"})
    if response.ok:
        tasks = response.json().get("filtered_tasks", [])
        all_high = all(task['priority'] == 'high' for task in tasks)
        print(f"Found {len(tasks)} high priority tasks")
        print(f"All tasks have high priority: {all_high}")
        print_test_result(all_high, "Priority Filter Test")
        all_tests_passed = all_tests_passed and all_high
    
    # Test 2: Filter by completion status
    print(f"\n{Fore.YELLOW}Test 2: Filter completed tasks{Style.RESET_ALL}")
    response = requests.get(f"{BASE_URL}/filter_tasks", params={"completed": "true"})
    if response.ok:
        tasks = response.json().get("filtered_tasks", [])
        all_completed = all(task['completed'] for task in tasks)
        print(f"Found {len(tasks)} completed tasks")
        print(f"All tasks are completed: {all_completed}")
        print_test_result(all_completed, "Completion Status Filter Test")
        all_tests_passed = all_tests_passed and all_completed
    
    # Test 3: Filter by due date
    today = datetime.now().strftime("%Y-%m-%d")
    print(f"\n{Fore.YELLOW}Test 3: Filter by due date (today: {today}){Style.RESET_ALL}")
    response = requests.get(f"{BASE_URL}/filter_tasks", params={"due_date": today})
    if response.ok:
        tasks = response.json().get("filtered_tasks", [])
        all_today = all(task['due_date'] == today for task in tasks)
        print(f"Found {len(tasks)} tasks due today")
        print(f"All tasks are due today: {all_today}")
        print_test_result(all_today, "Due Date Filter Test")
        all_tests_passed = all_tests_passed and all_today
    
    return all_tests_passed

def test_preferences():
    """Tests the preference management functionality"""
    print(f"\n{Fore.CYAN}=== Testing Preferences Endpoints ==={Style.RESET_ALL}")
    all_tests_passed = True
    
    # Test 1: Save preferences
    print(f"\n{Fore.YELLOW}Test 1: Save preferences{Style.RESET_ALL}")
    test_preferences = {
        "priority": "high",
        "due_date": datetime.now().strftime("%Y-%m-%d"),
        "completed": "pending"
    }
    save_response = requests.post(f"{BASE_URL}/save_filter_preferences", json=test_preferences)
    save_success = save_response.ok and save_response.json().get("message") == "Filter preferences saved successfully"
    print(f"Attempted to save preferences: {test_preferences}")
    print_test_result(save_success, "Save Preferences Test")
    all_tests_passed = all_tests_passed and save_success
    
    # Test 2: Get saved preferences
    print(f"\n{Fore.YELLOW}Test 2: Get saved preferences{Style.RESET_ALL}")
    get_response = requests.get(f"{BASE_URL}/get_saved_preferences")
    if get_response.ok:
        saved_prefs = get_response.json().get("saved_preferences", [])
        has_prefs = len(saved_prefs) == 1 and saved_prefs[0].get("priority") == test_preferences["priority"]
        print(f"Retrieved preferences: {json.dumps(saved_prefs, indent=2)}")
        print_test_result(has_prefs, "Get Preferences Test")
        all_tests_passed = all_tests_passed and has_prefs
    
    # Test 3: Clear preferences
    print(f"\n{Fore.YELLOW}Test 3: Clear preferences{Style.RESET_ALL}")
    clear_response = requests.post(f"{BASE_URL}/clear_preferences")
    if clear_response.ok:
        verify_response = requests.get(f"{BASE_URL}/get_saved_preferences")
        if verify_response.ok:
            is_empty = len(verify_response.json().get("saved_preferences", [])) == 0
            print(f"Preferences after clearing: {verify_response.json()}")
            print_test_result(is_empty, "Clear Preferences Test")
            all_tests_passed = all_tests_passed and is_empty
    
    return all_tests_passed

def run_all_tests():
    """Run all tests"""
    print(f"{Fore.CYAN}Starting Task Filter Service Tests{Style.RESET_ALL}")
    
    try:
        if not validate_service():
            print_test_result(False, "Service Validation")
            return
            
        filter_tests_passed = test_filter_tasks()
        preferences_tests_passed = test_preferences()
        
        all_passed = filter_tests_passed and preferences_tests_passed
        print(f"\n{Fore.CYAN}=== Final Test Results ==={Style.RESET_ALL}")
        print_test_result(filter_tests_passed, "Filter Tests")
        print_test_result(preferences_tests_passed, "Preferences Tests")
        print_test_result(all_passed, "Overall Test Suite")
            
    except requests.exceptions.ConnectionError:
        print(f"\n{Fore.RED}✗ Error: Could not connect to the task_filter service.{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Make sure the service is running on http://localhost:5003{Style.RESET_ALL}")
        print_test_result(False, "Connection Test")
    except Exception as e:
        print(f"\n{Fore.RED}✗ Error during testing: {str(e)}{Style.RESET_ALL}")
        print_test_result(False, "Test Execution")

if __name__ == "__main__":
    run_all_tests()