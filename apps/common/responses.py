class CustomResponse:
    def success(message, data=None, status_code=200):
        response = {
            "status": "success",
            "message": message,
            "data": data,
            "status_code": status_code,
        }
        if data is None:
            response.pop("data", None)
        return status_code, response

    def error(message, err_code, data=None, status_code=400):
        response = {
            "status": "failure",
            "message": message,
            "code": err_code,
            "data": data,
        }
        if data is None:
            response.pop("data", None)
        return status_code, response
