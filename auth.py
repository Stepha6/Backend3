from fastapi import HTTPException, Security, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional

# Definimos el esquema de OAuth2 para obtener el token en la cabecera
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Secreto para codificar y decodificar los tokens
SECRET_KEY = "mi_clave_secreta"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Tiempo de expiración del token

# Base de datos simulada de farmacéuticos (en un entorno real esto debería ser consultado en una base de datos)
FARMACEUTICOS_DB = {
    "farmaceutico1": {"id": "farmaceutico1", "role": "farmaceutico"},
    "farmaceutico2": {"id": "farmaceutico2", "role": "farmaceutico"},
}

# Función para crear un token de acceso
def crear_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Función para verificar el token
def verificar_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload if payload["role"] == "farmaceutico" else None
    except JWTError:
        return None

# Función de verificación de farmacéutico que se usará como dependiente en los endpoints
def verificar_farmaceutico(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="No se pudo validar el token de acceso",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if verificar_token(token) is None:
        raise credentials_exception
    return True  # Si el token es válido, el farmacéutico está autenticado
