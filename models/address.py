from pydantic import BaseModel

class Address(BaseModel):
    ip_address: str
    port: int