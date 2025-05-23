from connection import connect_to_mongodb
from bson import ObjectId
from fhir.resources.patient import Patient
from fhir.resources.medicationrequest import MedicationRequest
import json
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

# Conexión a colecciones
pacientes_collection = connect_to_mongodb("SamplePatientService3", "pacientes")
historia_collection = connect_to_mongodb("SamplePatientService3", "historiaMedica")
medicamentos_collection = connect_to_mongodb("SamplePatientService3", "medicamentos")
medication_request_collection = connect_to_mongodb("SamplePatientService3", "medicationRequests")# Nueva colección para medicamentos

# Obtener paciente por ID
def GetPatientById(patient_id: str):
    try:
        patient = pacientes_collection.find_one({"_id": ObjectId(patient_id)})
        if patient:
            patient["_id"] = str(patient["_id"])
            return "success", patient
        return "notFound", None
    except Exception as e:
        return "error", None

# Escribir nuevo paciente
def WritePatient(patient_dict: dict):
    try:
        pat = Patient.model_validate(patient_dict)
    except Exception as e:
        return f"errorValidating: {str(e)}", None

    validated_patient_json = pat.model_dump()
    result = pacientes_collection.insert_one(validated_patient_json)
    if result:
        inserted_id = str(result.inserted_id)
        return "success", inserted_id
    else:
        return "errorInserting", None

def WriteMedicationRequest(request_dict: dict):
    try:
        # Validación FHIR
        med_request = MedicationRequest.model_validate(request_dict)
        validated_data = med_request.model_dump()

        # Insertar en MongoDB
        result = medication_request_collection.insert_one(validated_data)
        return JSONResponse(
            status_code=201,
            content=jsonable_encoder({
                "status": "success",
                "id": str(result.inserted_id)
            })
        )
    except Exception as e:
        return JSONResponse(
            status_code=422,
            content=jsonable_encoder({
                "status": "error",
                "detail": f"errorValidating: {str(e)}"
            })
        )


# Obtener paciente por identificador
def GetPatientByIdentifier(patientSystem, patientValue):
    try:
        patient = pacientes_collection.find_one({
            "identifier.system": patientSystem,
            "identifier.value": patientValue
        })
        if patient:
            patient["_id"] = str(patient["_id"])
            return "success", patient
        return "notFound", None
    except Exception as e:
        return f"error: {str(e)}", None

# Obtener historia médica por ID de paciente
def GetHistoriaMedicaPorIdPaciente(patient_id: str):
    try:
        historia = historia_collection.find_one({"patient_id": patient_id})
        if historia:
            historia["_id"] = str(historia["_id"])
            return "success", historia
        return "notFound", None
    except Exception as e:
        return f"error: {str(e)}", None

# 🔹 NUEVA FUNCIÓN: Obtener medicamentos prescritos al paciente
def GetMedicamentosPrescritos(patient_id: str):
    try:
        historia_medica = historia_collection.find_one({"patient_id": patient_id})
        if historia_medica and "medicamentos" in historia_medica:
            medicamentos = historia_medica["medicamentos"]
            return "success", medicamentos
        return "notFound", None
    except Exception as e:
        return f"error: {str(e)}", None

# 🔹 NUEVA FUNCIÓN: Obtener recomendaciones de medicamentos compatibles
def ObtenerSugerenciasMedicamentosCompatibles(patient_id: str):
    try:
        # Obtener los medicamentos prescritos al paciente
        status, medicamentos_prescritos = GetMedicamentosPrescritos(patient_id)
        if status != "success":
            return "error", "No se pudieron obtener los medicamentos prescritos"

        # Obtener todos los medicamentos disponibles en la base de datos
        todos_medicamentos = medicamentos_collection.find()
        medicamentos_recomendados = []

        # Lógica de compatibilidad de medicamentos
        for medicamento in todos_medicamentos:
            medicamento_interacciones = medicamento.get("interacciones", [])
            compatible = True
            for medicamento_prescrito in medicamentos_prescritos:
                if medicamento_prescrito in medicamento_interacciones:
                    compatible = False
                    break

            if compatible:
                medicamentos_recomendados.append(medicamento)

        if medicamentos_recomendados:
            return "success", medicamentos_recomendados
        return "notFound", "No hay medicamentos compatibles"

    except Exception as e:
        return f"error: {str(e)}", None
