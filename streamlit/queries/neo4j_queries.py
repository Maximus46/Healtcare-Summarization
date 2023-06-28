def get_patient_entities(neo4j_connector, patient_id):
    # Convert patient_id to integer if it's a valid integer value
    try:
        patient_id = int(patient_id)
    except ValueError:
        return None

    query = """
    MATCH (p:Patient {patient_id: $patient_id_param})
    OPTIONAL MATCH (p)-[:HAS_MEDICAL_PROBLEM]->(mp:MedicalProblem)
    OPTIONAL MATCH (p)-[:DONE_TEST]->(t:Test)
    OPTIONAL MATCH (p)-[:RECEIVED_TREATMENT]->(tr:Treatment)
    RETURN COLLECT(DISTINCT mp.text_EN) AS MedicalProblems, COLLECT(DISTINCT t.text_EN) AS Tests, COLLECT(DISTINCT tr.text_EN) AS Treatments
    """
    with neo4j_connector.driver.session() as session:
        result = session.run(query, patient_id_param=patient_id)
        record = result.single()
        
        if record is not None:
            return dict(record)
        else:
            return None