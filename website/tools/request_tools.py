from flask import request

# Check if request if an AJAX request
def is_ajax_request(request) -> bool:
    return request.headers.get("X-Requested-With") == "XMLHttpRequest"