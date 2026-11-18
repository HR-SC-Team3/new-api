from fastapi import HTTPException, status

NOT_IMPLEMENTED = {501: {"description": "Not implemented"}}

def _not_implemented():
    raise HTTPException(status_code= status.HTTP_501_NOT_IMPLEMENTED, detail = "Not implemented")