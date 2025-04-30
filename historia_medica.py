from connection import connect_to_mongodb

# Conexión a la colección
collection = connect_to_mongodb("EntregaDeMedicamentos", "historiaMedica")

def GetHistoriaMedicaPorIdPaciente(patient_id: str):
    if not patient_id:
        return "error", "El ID del paciente no puede estar vacío."
    
    try:
        # Realizar la consulta en la base de datos
        historia = collection.find_one({"patient_id": patient_id})
        
        if historia:
            historia["_id"] = str(historia["_id"])  # Convertir el ObjectId a string
            return "success", historia
        else:
            return "notFound", None  # No se encontró historia médica para el paciente
        
    except Exception as e:
        # Manejo de excepciones más detallado
        return "error", f"Error al obtener la historia médica: {str(e)}"
