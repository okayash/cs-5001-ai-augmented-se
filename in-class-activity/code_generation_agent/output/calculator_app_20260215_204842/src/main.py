"""Simple command-line calculator application.

Usage:
    Run the program and enter calculations in the format:
    number operator number (e.g., "5 + 3")
    Type "exit" to quit the program.
"""

def add(a: float, b: float) -> float:
    """Return the sum of two numbers."""
    return a + b

def subtract(a: float, b: float) -> float:
    """Return the difference between two numbers."""
    return a - b

def multiply(a: float, b: float) -> float:
    """Return the product of two numbers."""
    return a * b

def divide(a: float, b: float) -> float | None:
    """Return the quotient of two numbers or None if division by zero."""
    if b == 0:
        return None
    return a / b

def parse_input(input_str: str) -> tuple[float, str, float] | None:
    """Parse input string into operands and operator.

    Args:
        input_str: String in format "number operator number"

    Returns:
        Tuple of (operand1, operator, operand2) or None if parsing fails
    """
    try:
        parts = input_str.split()
        if len(parts) != 3:
            return None

        operand1 = float(parts[0])
        operator = parts[1]
        operand2 = float(parts[2])

        return operand1, operator, operand2
    except ValueError:
        return None

def calculate(operand1: float, operator: str, operand2: float) -> float | str:
    """Perform calculation based on operator.

    Args:
        operand1: First number
        operator: Arithmetic operator (+, -, *, /)
        operand2: Second number

    Returns:
        Result of calculation or error message
    """
    operations = {
        '+': add,
        '-': subtract,
        '*': multiply,
        '/': divide
    }

    if operator not in operations:
        return "Error: Invalid operator. Use +, -, *, or /"

    result = operations[operator](operand1, operand2)

    if result is None:
        return "Error: Division by zero"

    return result

def main():
    """Main calculator loop."""
    print("Welcome to the Calculator App!")
    print("Enter a calculation (or \"exit\" to quit): ", end='')

    while True:
        user_input = input().strip()

        if user_input.lower() == "exit":
            print("Goodbye!")
            break

        parsed = parse_input(user_input)

        if parsed is None:
            print("Error: Invalid input. Please enter numbers only.")
        else:
            operand1, operator, operand2 = parsed
            result = calculate(operand1, operator, operand2)

            if isinstance(result, str):
                print(result)
            else:
                print(f"Result: {result}")

        print("Enter a calculation (or \"exit\" to quit): ", end='')

if __name__ == "__main__":
    main()
