from datasets import load_dataset
import pandas as pd

dataset = load_dataset("QuyenAnhDE/Diseases_Symptoms")
df = pd.DataFrame(dataset['train'])  # Assumes 'train' split

# Clean the dataframe
df = df.rename(columns={"Name": "disease", "Symptoms": "symptoms"})
df['symptoms'] = df['symptoms'].apply(lambda x: [s.strip().lower() for s in x.split(",")])
import sqlite3

conn = sqlite3.connect("disease.db")
cur = conn.cursor()

# Create tables
with open("schema.sql") as f:
    cur.executescript(f.read())

disease_id_map = {}
symptom_id_map = {}

for _, row in df.iterrows():
    disease = row["disease"]
    symptoms = row["symptoms"]

    # Insert disease
    cur.execute("INSERT OR IGNORE INTO disease(name) VALUES(?)", (disease,))
    cur.execute("SELECT id FROM disease WHERE name=?", (disease,))
    disease_id = cur.fetchone()[0]

    for symptom in symptoms:
        cur.execute("INSERT OR IGNORE INTO symptom(name) VALUES(?)", (symptom,))
        cur.execute("SELECT id FROM symptom WHERE name=?", (symptom,))
        symptom_id = cur.fetchone()[0]

        cur.execute(
            "INSERT OR IGNORE INTO disease_symptom(disease_id, symptom_id) VALUES(?, ?)",
            (disease_id, symptom_id)
        )

conn.commit()
conn.close()
