from fastapi import APIRouter, Depends, HTTPException
from auth import verificar_farmaceutico
from historia_medica import ObtenerHistoriaMedicaPorIdPaciente
from fastapi import FastAPI, HTTPException, Request
import uvicorn
from PatientCrud import GetPatientById, WritePatient, GetPatientByIdentifier
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Middleware para CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todos los orígenes
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permitir todos los encabezados
)

# Definir el router
router = APIRouter()

# Obtener historia médica por ID de paciente
@router.get("/historia-medica/{patient_id}")
def obtener_historia_medica(patient_id: str, usuario=Depends(verificar_farmaceutico)):
    status, historia = GetHistoriaMedicaPorIdPaciente(patient_id)
    if status == "success":
        return historia
    raise HTTPException(status_code=404, detail="Historia médica no encontrada")

# Obtener paciente por ID
@app.get("/patient/{patient_id}", response_model=dict)
async def get_patient_by_id(patient_id: str):
    status, patient = GetPatientById(patient_id)
    if status == 'success':
        return patient  # Return patient
    elif status == 'notFound':
        raise HTTPException(status_code=404, detail="Patient not found")
    else:
        raise HTTPException(status_code=500, detail=f"Internal error. {status}")

# Obtener paciente por identificador
@app.get("/patient", response_model=dict)
async def get_patient_by_identifier(system: str, value: str):
    status, patient = GetPatientByIdentifier(system, value)
    if status == 'success':
        return patient  # Return patient
    elif status == 'notFound':
        raise HTTPException(status_code=404, detail="Patient not found")
    else:
        raise HTTPException(status_code=500, detail=f"Internal error. {status}")

# Crear nuevo paciente
from fastapi.responses import JSONResponse

@app.post("/patient", response_model=dict)
async def add_patient(request: Request):
    try:
        new_patient_dict = await request.json()
        print("JSON recibido:", new_patient_dict)
        status, patient_id = WritePatient(new_patient_dict)
        if status == 'success':
            return {"_id": patient_id}
        elif status.startswith("errorValidating"):
            return JSONResponse(status_code=400, content={"detail": status})
        else:
            return JSONResponse(status_code=500, content={"detail": f"Error en el backend: {status}"})
    except Exception as e:
        print("Error inesperado:", e)
        return JSONResponse(status_code=500, content={"detail": "Error interno del servidor"})


# Obtener sugerencias de medicamentos compatibles
@app.get("/medicamentos/sugerencias/{patient_id}")
async def obtener_sugerencias_medicamentos(patient_id: str):
    status, sugerencias = ObtenerSugerenciasMedicamentosCompatibles(patient_id)
    if status == "success":
        return {"medicamentos_recomendados": sugerencias}
    elif status == "notFound":
        raise HTTPException(status_code=404, detail="No hay medicamentos compatibles disponibles")
    else:
        raise HTTPException(status_code=500, detail=f"Error interno: {status}")

# Raíz de la API
@app.get("/")
def read_root():
    return {"message": "Servidor backend funcionando correctamente"}

# Correr el servidor
if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
