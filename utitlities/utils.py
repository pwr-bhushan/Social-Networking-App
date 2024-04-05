from rest_framework.response import Response


def get_api_response(success, response_content, status):
    response = {"success": success, "response": response_content}

    return Response(response, status=status)
