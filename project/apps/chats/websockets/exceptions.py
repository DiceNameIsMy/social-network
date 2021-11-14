

class WebSocketException(Exception):
    """ Related to websockets module exceptions
    """


class EmptyFieldException(WebSocketException):
    """ raised when required field was not provided
    """
    def __init__(self, field_name: str, help_text: str = 'was not provided') -> None:
        self.message = f'{field_name} {help_text}'

    def __str__(self) -> str:
        return self.message