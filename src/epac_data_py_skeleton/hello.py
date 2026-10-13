"""Module-level documentation.

This is a simple demo module
"""


def magic_number() -> int:
    """Return the example answer.

    This is a function to demonstrate unit testing.

    Returns:
        int: The example answer, ``42``.

    Examples:
        >>> magic_number()
        42
    """

    return 42


def print_and_count_message(msg: str) -> int:
    """
    Print the message and return the length of the string.

    Demonstrates a Google-style docstring parsed by Sphinx Napoleon.

    Args:
        msg (str): The message to print and count.

    Returns:
        int: Length of message.

    Examples:
        >>> message = print_and_count_message(msg = "Hello!")
        >>> message
        6
    """

    print(msg)
    return len(msg)


def hello() -> None:
    """Script entry point.

    This is a function to demonstrate the use of a script entry point.
    """

    print("Hello, world")
