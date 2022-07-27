from flask import escape
import functions_framework

@functions_framework.http
def upcase_http(request):
    """Simple HTTP Cloud Function that returns the upper case version of any string 
    it is passed.
    Args:
        request (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    """
    request_json = request.get_json(silent=True)
    request_args = request.args

    if request_json and 'string' in request_json:
        string = request_json['string']
    elif request_args and 'string' in request_args:
        string = request_args['string']
    else:
        string = ""
    return escape(string).upper()