
import argparse
import json
import logging
import os
import subprocess
from uuid import uuid4
from unittest.mock import patch
from openai import OpenAI

os.environ['OPENAI_API_KEY'] = 'your-api-key'

# Constants and templates
EXAMPLE_UNIT_TEST = r"""
import unittest
from unittest.mock import patch
from generated_script import add_event_to_google_calendar  # Assuming your function is named this

class TestAddEventToGoogleCalendar(unittest.TestCase):

    def setUp(self):
        self.valid_input = {
            "apiKey": "valid_api_key",
            "oauthToken": "valid_oauth_token",
            "calendarId": "primary",
            "event": {
                "summary": "Test Event",
                "description": "This is a test event",
                "start": {
                    "dateTime": "2023-10-01T09:00:00-07:00",
                    "timeZone": "America/Los_Angeles"
                },
                "end": {
                    "dateTime": "2023-10-01T10:00:00-07:00",
                    "timeZone": "America/Los_Angeles"
                },
                "attendees": [
                    {
                        "email": "attendee1@example.com",
                        "displayName": "Attendee 1",
                        "responseStatus": "accepted"
                    }
                ],
                "reminders": {
                    "useDefault": False,
                    "overrides": [
                        {
                            "method": "email",
                            "minutes": 30
                        },
                        {
                            "method": "popup",
                            "minutes": 10
                        }
                    ]
                }
            }
        }

        self.valid_output = {
            "status": "success",
            "eventId": "unique_event_id"
        }

        self.error_output = {
            "status": "failed",
            "error": {
                "code": 401,
                "message": "Invalid OAuth token"
            }
        }

    @patch('generated_script.create_google_calendar_event')  # Mock whatever function actually makes the API call
    def test_add_event_success(self, mock_create_google_calendar_event):
        mock_create_google_calendar_event.return_value = self.valid_output
        
        response = add_event_to_google_calendar(self.valid_input)
        self.assertEqual(response, self.valid_output)

    @patch('generated_script.create_google_calendar_event')
    def test_add_event_invalid_oauth(self, mock_create_google_calendar_event):
        mock_create_google_calendar_event.return_value = self.error_output
        
        response = add_event_to_google_calendar(self.valid_input)
        self.assertEqual(response, self.error_output)

    def test_missing_api_key(self):
        invalid_input = dict(self.valid_input)
        invalid_input.pop('apiKey')
        
        with self.assertRaises(KeyError):
            add_event_to_google_calendar(invalid_input)

    def test_missing_oauth_token(self):
        invalid_input = dict(self.valid_input)
        invalid_input.pop('oauthToken')
        
        with self.assertRaises(KeyError):
            add_event_to_google_calendar(invalid_input)

    def test_missing_event_summary(self):
        invalid_input = dict(self.valid_input)
        invalid_input['event'].pop('summary')
        
        with self.assertRaises(KeyError):
            add_event_to_google_calendar(invalid_input)
            
    def test_invalid_datetime_format(self):
        invalid_input = dict(self.valid_input)
        invalid_input['event']['start']['dateTime'] = "invalid-datetime-format"
        
        with self.assertRaises(ValueError):
            add_event_to_google_calendar(invalid_input)

    @patch('generated_script.create_google_calendar_event')
    def test_missing_optional_fields(self, mock_create_google_calendar_event):
        input_without_optional = {
            "apiKey": "valid_api_key",
            "oauthToken": "valid_oauth_token",
            "calendarId": "primary",
            "event": {
                "summary": "Test Event",
                "start": {
                    "dateTime": "2023-10-01T09:00:00-07:00",
                    "timeZone": "America/Los_Angeles"
                },
                "end": {
                    "dateTime": "2023-10-01T10:00:00-07:00",
                    "timeZone": "America/Los_Angeles"
                }
            }
        }
        mock_create_google_calendar_event.return_value = {
            "status": "success",
            "eventId": "unique_event_id"
        }
        
        response = add_event_to_google_calendar(input_without_optional)
        self.assertEqual(response, {
            "status": "success",
            "eventId": "unique_event_id"
        })


if __name__ == '__main__':
    unittest.main()
"""

CONSTANT_FUNCTIONAL_GENERATION_GUIDELINES_PROMPT = """
1. The script should read JSON input from a file named in the format: (unique identifier)_(timestamp)_(script_name)_input.json.
2. The script should write JSON output to a file named in the format: (unique identifier)_(timestamp)_(script_name)_output.json.
3. Error logs should be stored in a file named (unique identifier)_error.json, containing the input data that caused the error, the error message, the script name, and the file location.
4. All scripts should handle input and output data in JSON format to ensure easy chaining.
5. The scripts should include detailed logging and error handling to facilitate debugging.
6. Use return_gpt_response(prompt: str, return_json: bool) to outsource complex tasks to an LLM.
"""

EXAMPLE_CODE = r"""
import json
import requests
import datetime
from utils import return_gpt_response

def read_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def write_json(data, file_path):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

def log_error(unique_id, input_data, error_message, script_name):
    error_log = {
        "script_name": script_name,
        "input_data": input_data,
        "error_message": error_message,
        "file_location": __file__
    }
    error_file_path = f"{unique_id}_error.json"
    write_json(error_log, error_file_path)

def main(input_file, output_file, unique_id):
    try:
        # Read input JSON
        input_data = read_json(input_file)
        
        # Example task 1: API Call
        api_url = input_data['api_url']
        api_response = requests.get(api_url)
        if api_response.status_code != 200:
            raise Exception(f"API call failed with status code {api_response.status_code}")
        api_data = api_response.json()
        
        # Example task 2: Data Processing with LLM Assistance
        prompt = f"Process the following data and extract relevant information: {json.dumps(api_data, indent=4)}"
        processed_data = return_gpt_response(prompt=prompt, return_json=True)
        processed_data = json.loads(processed_data)
        
        # Example task 3: Further Processing
        processed_data['timestamp'] = datetime.datetime.now().isoformat()
        
        # Write output JSON
        write_json(processed_data, output_file)
        
    except Exception as e:
        log_error(unique_id, input_data, str(e), 'example_script.py')
        raise

if __name__ == "__main__":
    unique_id = "unique_series_identifier"
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    input_file = f"{unique_id}_{timestamp}_example_script_input.json"
    output_file = f"{unique_id}_{timestamp}_example_script_output.json"
    main(input_file, output_file, unique_id)
"""

GENERATED_SCRIPTS_FOLDER = "generated_scripts"
METADATA_FILE = "metadata.json"
UNIQUE_FOLDER = os.path.join(GENERATED_SCRIPTS_FOLDER, uuid4().hex[:8])
os.makedirs(UNIQUE_FOLDER, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(UNIQUE_FOLDER, "function_generation.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


client = OpenAI()


def return_gpt_response(message_log=[], prompt="", model="gpt-4o", system_content="", return_json=False, post_response_requirements="", pre_prompt_requirements="", sleep=0, max_tokens=4096): 
    if message_log == [] and prompt == "":
        raise ValueError("Both message_log and prompt cannot be empty when calling return_gpt_response.")
    
    if message_log == []:
        message_log.append({"role": "system", "content": system_content})
    else:
        if message_log[0]["role"] != "system":
            message_log.insert(0, {"role": "system", "content": system_content})

    if prompt != "":
        message_log.append({"role": "user", "content": prompt})

    try:
        if sleep:
            sleep_time = random.randint(sleep, sleep*2)
            time.sleep(sleep_time)

        completion_args = {
            "model": model,
            "messages": message_log,
            "max_tokens": max_tokens
        }
        
        if return_json:
            completion_args["response_format"] = {"type": "json_object"}

        chat_completion = client.chat.completions.create(**completion_args)
        
    except Exception as e:
        print("An error occurred")
        print(e)
        return

    response = chat_completion.choices[0].message.content
    return response


def create_directory(path: str):
    os.makedirs(path, exist_ok=True)


class FunctionGenerationError(Exception):
    pass


class SpecGathering:
    def __init__(self):
        self.specifications = ""
        self.input_schema = {}
        self.output_schema = {}

    def gather_requirements(self):
        prompt = "Welcome! Let's gather requirements by using the dialectic method -- the LLM will ask one question at a time. Oh user, please describe the key functionality:"
        print("Please provide the key functionality of the script. Don't worry about being brief, the script will keep asking you questions until you're satisfied.")
        while True:
            user_input = input("Your input (or type 'done' to finish): ")
            self.specifications += f"\nUser: {user_input}"
            prompt = f"Given the current specifications, clarify further details or add new aspects. Only ask exactly one question. This process will continue until the user finishes. At NO point in time may you stop asking questions.: {self.specifications}\nRemember, you are NOT allowed to stop asking questions -- though you should still ask questions that add further clarity to the specifications."
            if user_input.lower() == "done":
                break
            response = return_gpt_response(prompt=prompt)
            print(f"LLM: {response}")
            self.specifications += f"\nLLM: {response}"
            
            logger.info(f"Gathering requirements: {self.specifications}")

    def generate_schema(self, schema_type="input"):
        assert schema_type in ["input", "output"], "Invalid schema type"
        prompt = f"Create a JSON schema for the {schema_type} of a function/script that follows this specification: {self.specifications}"
        schema_response = return_gpt_response(prompt=prompt, return_json=True)
        schema = json.loads(schema_response)
        if schema_type == "input":
            self.input_schema = schema
        else:
            self.output_schema = schema
        logger.info(f"Generated {schema_type} schema: {schema}")

    def save_schema(self, schema, schema_type="input"):
        filename = os.path.join(UNIQUE_FOLDER, f"{schema_type}_schema.json")
        with open(filename, "w") as file:
            json.dump(schema, file, indent=4)
        logger.info(f"Saved {schema_type} schema to {filename}")


def escape_code(code: str) -> str:
    return repr(code)


def unescape_code(escaped_string: str) -> str:
    decoded_string = escaped_string.replace("\\n", "\n").replace("\\'", "'").replace('\\"', '"')
    return decoded_string


class UnitTestGenerator:
    def __init__(self, input_schema, output_schema):
        self.input_schema = input_schema
        self.output_schema = output_schema
        self.unit_tests = []

    def generate_unit_tests(self, requirements):
        prompt = f"""
        Create a series of unit tests for a function/script. 
        The function/script specification:
        {json.dumps(self.input_schema, indent=4)}
        The expected output schema:
        {json.dumps(self.output_schema, indent=4)}
        The tests should cover typical cases, edge cases, and erroneous cases. 
        Provide the tests in Python unittest format.

        Note that these schemas are the expected input and output for the function/script that meet these requirements:
        {requirements}

        You MUST return a json object that contains the unit tests in Python unittest format, Make sure that the escaped code can be put through the 'unescape_code' function to get the results. Put those tests in the 'unit_tests' key of the json object.

        Example:
        {{"unit_tests": {escape_code(EXAMPLE_UNIT_TEST)}}}

        Make special note that the tests should be escaped like they are in the example.

        Assume that the function being tested has the same name as used in the unit tests. This function will be defined in: 'generated_script.py' so the tests should import the functions from that file.
        """

        logger.info(f"Generating unit tests with prompt:\n{prompt}")

        response = return_gpt_response(prompt=prompt, return_json=True)

        logger.info(f"Raw LLM response: {response}")

        try:
            response_json = json.loads(response)
            escaped_unit_tests = response_json['unit_tests']
            self.unit_tests = unescape_code(escaped_unit_tests)
            logger.info(f"Generated unit tests: {self.unit_tests}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON response: {e}")
            logger.error(f"Response content: {response}")
            raise
        except KeyError as e:
            logger.error(f"Missing expected key in JSON response: {e}")
            logger.error(f"Response content: {response}")
            raise

    def save_unit_tests(self):
        file_name = os.path.join(UNIQUE_FOLDER, "test_script.py")
        with open(file_name, "w") as file:
            file.write(self.unit_tests)
        logger.info(f"Saved unit tests to {file_name}")


class ScriptGenerator:
    def __init__(self, specifications, input_schema, output_schema, unit_tests):
        self.specifications = specifications
        self.input_schema = input_schema
        self.output_schema = output_schema
        self.unit_tests = unit_tests
        self.function_code = ""

    def generate_script(self):
        prompt = f"""
        Here are the guidelines for the python script you'll be generating:
        {CONSTANT_FUNCTIONAL_GENERATION_GUIDELINES_PROMPT}
        
        Following this specification:
        {self.specifications}

        The input schema:
        {json.dumps(self.input_schema, indent=4)}
        The output schema:
        {json.dumps(self.output_schema, indent=4)}

        Your code must pass the following unit tests:
        {self.unit_tests}

        You must return a JSON object with the generated function/script in the python_code property.

        Here's an example of the returned json object:

        {{"python_code": "{escape_code(EXAMPLE_CODE)}"}}

        Just respond with the code such that it can be run directly after escaping it -- it should include all python libraries required to run the code.
        """
        
        logger.info(f"Generating script with prompt:\n{prompt}")

        try:
            response = return_gpt_response(prompt=prompt, return_json=True)
            logger.info(f"Raw LLM response: {response}")

            response_json = json.loads(response)
            escaped_function_code = response_json['python_code']
            function_code = unescape_code(escaped_function_code)
            # strip the leading and trailing quotes
            function_code = function_code.strip('"').strip("'")
            self.function_code = function_code

            logger.info(f"Generated function code: {self.function_code}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON response: {e}")
            logger.error(f"Response content: {response}")
            raise
        except KeyError as e:
            logger.error(f"Missing expected key in JSON response: {e}")
            logger.error(f"Response content: {response}")
            raise

    def test_generated_script(self, script):
        script_path = os.path.join(UNIQUE_FOLDER, "generated_script.py")
        with open(script_path, "w") as file:
            file.write(script)
        result = subprocess.run(
            ["python", os.path.join(UNIQUE_FOLDER, "test_script.py")], capture_output=True, text=True
        )
        if result.returncode == 0:
            logger.info("Generated script passes all unit tests.")
            return True
        else:
            logger.error(f"Generated script failed some tests: {result.stderr}")
            return False

    def save_generated_script(self):
        filename = os.path.join(UNIQUE_FOLDER, "final_script.py")
        with open(filename, "w") as file:
            file.write(self.function_code)
        logger.info(f"Saved generated script to {filename}")


def workflow(requirements):
    spec_gatherer = SpecGathering()
    if requirements:
        spec_gatherer.specifications = requirements
    else:
        spec_gatherer.gather_requirements()
    
    spec_gatherer.generate_schema(schema_type="input")
    spec_gatherer.generate_schema(schema_type="output")
    spec_gatherer.save_schema(spec_gatherer.input_schema, schema_type="input")
    spec_gatherer.save_schema(spec_gatherer.output_schema, schema_type="output")
    
    test_generator = UnitTestGenerator(
        spec_gatherer.input_schema, spec_gatherer.output_schema
    )
    test_generator.generate_unit_tests(spec_gatherer.specifications)
    test_generator.save_unit_tests()
    
    script_generator = ScriptGenerator(
        specifications=spec_gatherer.specifications,
        input_schema=spec_gatherer.input_schema,
        output_schema=spec_gatherer.output_schema,
        unit_tests=test_generator.unit_tests,
    )
    script_generator.generate_script()
    if script_generator.test_generated_script(script_generator.function_code):
        script_generator.save_generated_script()
    else:
        logger.error("The generated script did not pass all the unit tests.")


def main():
    parser = argparse.ArgumentParser(
        description="Generate Python functions based on user requirements."
    )
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument(
        "-r",
        "--requirements",
        help="High-level user requirements for the function as a direct string.",
    )
    group.add_argument(
        "-f",
        "--file",
        help="Path to a text file containing the high-level user requirements.",
    )
    args = parser.parse_args()
    try:
        if args.file:
            with open(args.file, "r") as file:
                requirements = file.read().strip()
            logger.info("Requirements read from file.")
        else:
            requirements = args.requirements
            logger.info("Requirements provided as a direct string.")
        workflow(requirements)
    except Exception as e:
        logger.error("Execution failed", exc_info=True)
        raise e


if __name__ == "__main__":
    main()