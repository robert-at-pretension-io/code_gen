
import unittest
from generated_script import add_two_numbers

class TestAddTwoNumbers(unittest.TestCase):

    def test_positive_numbers(self):
        input_data = {
            "number1": 10,
            "number2": 20,
            "language": "Python"
        }
        expected_output = {
            "sum": 30
        }
        self.assertEqual(add_two_numbers(input_data), expected_output)

    def test_negative_numbers(self):
        input_data = {
            "number1": -10,
            "number2": -5,
            "language": "Python"
        }
        expected_output = {
            "sum": -15
        }
        self.assertEqual(add_two_numbers(input_data), expected_output)

    def test_mixed_sign_numbers(self):
        input_data = {
            "number1": 15,
            "number2": -5,
            "language": "Python"
        }
        expected_output = {
            "sum": 10
        }
        self.assertEqual(add_two_numbers(input_data), expected_output)

    def test_zero_sum(self):
        input_data = {
            "number1": 0,
            "number2": 0,
            "language": "Python"
        }
        expected_output = {
            "sum": 0
        }
        self.assertEqual(add_two_numbers(input_data), expected_output)

    def test_large_numbers(self):
        input_data = {
            "number1": 1e15,
            "number2": 1e15,
            "language": "Python"
        }
        expected_output = {
            "sum": 2e15
        }
        self.assertEqual(add_two_numbers(input_data), expected_output)

    def test_missing_number1(self):
        input_data = {
            "number2": 10,
            "language": "Python"
        }
        with self.assertRaises(KeyError):
            add_two_numbers(input_data)

    def test_missing_number2(self):
        input_data = {
            "number1": 10,
            "language": "Python"
        }
        with self.assertRaises(KeyError):
            add_two_numbers(input_data)

    def test_missing_language(self):
        input_data = {
            "number1": 10,
            "number2": 10,
        }
        with self.assertRaises(KeyError):
            add_two_numbers(input_data)

    def test_invalid_language(self):
        input_data = {
            "number1": 10,
            "number2": 10,
            "language": "InvalidLang"
        }
        with self.assertRaises(ValueError):
            add_two_numbers(input_data)

    def test_non_numeric_number1(self):
        input_data = {
            "number1": "ten",
            "number2": 10,
            "language": "Python"
        }
        with self.assertRaises(ValueError):
            add_two_numbers(input_data)

    def test_non_numeric_number2(self):
        input_data = {
            "number1": 10,
            "number2": "ten",
            "language": "Python"
        }
        with self.assertRaises(ValueError):
            add_two_numbers(input_data)


if __name__ == '__main__':
    unittest.main()
