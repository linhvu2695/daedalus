from flask import request

class OptionList:
    def __init__(self) -> None:
        self.options = {}

    def add_option(self, value: int, text: str):
        self.options[value] = text

    def to_list(self):
        result = [{"value": value, "text": text} for value, text in self.options.items()]
        result.sort(key=lambda x: x["value"])
        return result

# Check if request if an AJAX request
def is_ajax_request(request) -> bool:
    return request.headers.get("X-Requested-With") == "XMLHttpRequest"