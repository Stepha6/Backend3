from fastapi import FastAPI, APIRouter, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from auth import verificar_farmaceutico
from historia_medica import ObtenerHistoriaMedicaPorIdPaciente
from PatientCrud import (
    GetPatientById,
    WritePatient,
    GetPatientByIdentifier,
    WriteMedicationRequest
)
from sugerencias import ObtenerSugerenciasMedicamentosCompatibles  

app = FastAPI()

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://frontend3-jluw.onrender.com"],  # Origen del frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Router principal
router = APIRouter()

# Endpoint raíz
@app.get("/")
def read_root():
    return {"message": "Servidor backend funcionando correctamente"}

# Obtener historia médica
@app.get("/historia-medica/{patient_id}")
def obtener_historia_medica(patient_id: str, usuario=Depends(verificar_farmaceutico)):
    status, historia = ObtenerHistoriaMedicaPorIdPaciente(patient_id)
    if status == "success":
        return historia
    raise HTTPException(status_code=404, detail="Historia médica no encontrada")

# Obtener paciente por ID
@app.get("/patient/{patient_id}", response_model=dict)
async def get_patient_by_id(patient_id: str):
    status, patient = GetPatientById(patient_id)
    if status == 'success':
        return patient
    elif status == 'notFound':
        raise HTTPException(status_code=404, detail="Patient not found")
    else:
        raise HTTPException(status_code=500, detail=f"Internal error. {status}")

# Obtener paciente por identificador
@app.get("/patient", response_model=dict)
async def get_patient_by_identifier(system: str, value: str):
    status, patient = GetPatientByIdentifier(system, value)
    if status == 'success':
        return patient
    elif status == 'notFound':
        raise HTTPException(status_code=404, detail="Patient not found")
    else:
        raise HTTPException(status_code=500, detail=f"Internal error. {status}")

# Crear nuevo paciente
@app.post("/patient")
def create_patient(patient: dict = Body(...)):
    try:
        status, inserted_id = WritePatient(patient)
        if status == "success":
            return JSONResponse(status_code=200, content={"status": status, "id": inserted_id})
        else:
            return JSONResponse(status_code=400, content={"status": status})
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "detail": str(e)})


@app.post("/medicationrequest")
def create_medication_request(request: dict = Body(...)):
    try:
        status, inserted_id = WriteMedicationRequest(request)
        if status == "success":
            return JSONResponse(status_code=200, content={"status": status, "id": inserted_id})
        else:
            return JSONResponse(status_code=400, content={"status": status})
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "detail": str(e)})


# Crear solicitud de medicam

