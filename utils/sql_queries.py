import sqlite3

def get_diseases_by_symptoms(symptoms):
    """
    Get diseases that have ALL the given symptoms.
    
    Parameters:
    - symptoms: List of symptom names
    """
    if not symptoms:
        return []
        
    conn = sqlite3.connect("disease.db")
    cur = conn.cursor()

    try:
        placeholder = ",".join(["?"] * len(symptoms))
        
        # Find diseases that have ALL the symptoms
        query = f"""
            SELECT d.name
            FROM disease d
            WHERE (
                SELECT COUNT(DISTINCT s.name)
                FROM disease_symptom ds
                JOIN symptom s ON s.id = ds.symptom_id
                WHERE ds.disease_id = d.id AND s.name IN ({placeholder})
            ) = ?
        """
        
        cur.execute(query, symptoms + [len(symptoms)])
        result = [row[0] for row in cur.fetchall()]
        return result
    except Exception as e:
        print(f"SQL Error in get_diseases_by_symptoms: {e}")
        return []
    finally:
        conn.close()

def get_related_symptoms(disease_names, exclude=[]):
    """
    Get ALL symptoms from the specified diseases, excluding the ones provided.
    
    Parameters:
    - disease_names: List of disease names to get symptoms from
    - exclude: List of symptom names to exclude from the results
    """
    if not disease_names:
        return []

    conn = sqlite3.connect("disease.db")
    cur = conn.cursor()

    try:
        placeholder = ",".join(["?"] * len(disease_names))
        exclude_clause = ""
        if exclude:
            exclude_placeholder = ",".join(["?"] * len(exclude))
            exclude_clause = f"AND s.name NOT IN ({exclude_placeholder})"
        
        # Get ALL OTHER symptoms from the matching diseases
        query = f"""
            SELECT DISTINCT s.name 
            FROM symptom s
            JOIN disease_symptom ds ON s.id = ds.symptom_id
            JOIN disease d ON d.id = ds.disease_id
            WHERE d.name IN ({placeholder}) {exclude_clause}
        """
        
        cur.execute(query, disease_names + (exclude if exclude else []))
        result = [row[0] for row in cur.fetchall()]
        return result
    except Exception as e:
        print(f"SQL Error in get_related_symptoms: {e}")
        return []
    finally:
        conn.close()
