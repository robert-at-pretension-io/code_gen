
import json
import datetime
import os


# Function to read JSON input from a file

def read_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)


# Function to write JSON output to a file

def write_json(data, file_path):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)


# Function to log errors

def log_error(unique_id, input_data, error_message, script_name, timestamp):
    error_log = {
        "script_name": script_name,
        "input_data": input_data,
        "error_message": error_message,
        "file_location": os.path.abspath(__file__)
    }
    error_file_path = f"{unique_id}_{timestamp}_error.json"
    write_json(error_log, error_file_path)


# Main function to add two numbers

def add_two_numbers(input_data):
    try:
        number1 = input_data['number1']
        number2 = input_data['number2']
        language = input_data['language']

        if language not in ["Python", "JavaScript", "Java", "C++", "Ruby", "Go", "C#", "PHP", "Swift"]:
            raise ValueError("Unsupported language")

        if not isinstance(number1, (int, float)):
            raise ValueError("number1 must be a number")

        if not isinstance(number2, (int, float)):
            raise ValueError("number2 must be a number")

        result = {
            "sum": number1 + number2
        }

        return result
    except KeyError as e:
        raise KeyError(f"Missing key: {e}")
    except ValueError as e:
        raise ValueError(str(e))


# Entry point of the script

def main():
    unique_id = "unique_series_identifier"
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    script_name = "add_two_numbers"
    input_file = f"{unique_id}_{timestamp}_{script_name}_input.json"
    output_file = f"{unique_id}_{timestamp}_{script_name}_output.json"

    try:
        input_data = read_json(input_file)
        output_data = add_two_numbers(input_data)
        write_json(output_data, output_file)
    except Exception as e:
        log_error(unique_id, input_data, str(e), script_name, timestamp)
        raise


if __name__ == "__main__":
    main()
