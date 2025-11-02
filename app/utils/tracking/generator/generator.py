import os
import json
from datetime import datetime, timezone, timedelta
from huggingface_hub import InferenceClient

from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch, cm

from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from app.utils.const import TOKEN_HUGGINGFACE

current_dir = os.path.dirname(os.path.abspath(__file__))
# Assurez-vous que ce chemin est correct
font_path = os.path.join(current_dir, "..", "..", "..", "..", "assets", "DejaVuSans.ttf")
font_path = os.path.abspath(font_path)

# Enregistrement de la police (Déjà fait, mais s'assurer qu'il est en haut)
pdfmetrics.registerFont(TTFont("DejaVu", font_path))


def generate_intrusion_report(input_json_path: str,
                               output_folder: str = "reports",
                               model_name: str = "openai/gpt-oss-120b",
                               hf_token: str = TOKEN_HUGGINGFACE) -> dict:

    os.makedirs(output_folder, exist_ok=True)
    outputs_folder = os.path.join(output_folder, "outputs")
    os.makedirs(outputs_folder, exist_ok=True)

    with open(input_json_path, "r", encoding="utf-8") as f:
        logs = json.load(f)

    person = {
        "name": "Suspect inconnu",
        "image_local_path": "./captures/last_capture.jpg"
    }

    # ----------- PDF STYLES IMPROVED -----------
    styles = getSampleStyleSheet()

    # Style pour le corps de texte général
    body_style = ParagraphStyle(
        "Body",
        parent=styles["BodyText"],
        fontName="DejaVu", # Utilisation de la police enregistrée
        fontSize=11.5,
        leading=15,
        spaceAfter=10
    )

    # NOUVEAU STYLE pour les cellules du tableau
    cell_style = ParagraphStyle(
        "TableCell",
        parent=styles["BodyText"],
        fontName="DejaVu",  # CLÉ: Assurez-vous que c'est la police multi-caractères
        fontSize=9,         
        leading=11,
        alignment=0, # Alignement à gauche
        spaceAfter=0
    )


    table_data = [
        [
            Paragraph("Heure (UTC)", cell_style),
            Paragraph("Action", cell_style),
            Paragraph("Détails", cell_style)
        ]
    ] # Note: Utiliser Paragraph pour l'entête est plus sûr pour les accents

    logs_text = ""
    timestamps = []

    for entry in logs:
        ts = entry.get("timestamp", 0)
        timestamps.append(ts)
        dt = datetime.fromtimestamp(ts, timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        action = entry.get("type", "")
        details = {k: v for k, v in entry.items() if k not in ["timestamp", "type"]}
        details_str = ", ".join([f"{k}:{v}" for k, v in details.items()]) or "—"

        logs_text += f"{dt} | {action} | {details_str}\n"

        # MODIFICATION CLÉ: Encapsuler les données du tableau dans des Paragraphs
        table_data.append([
            Paragraph(dt, cell_style),
            Paragraph(action, cell_style),
            Paragraph(details_str, cell_style)
        ])

    start_time = datetime.fromtimestamp(min(timestamps), timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    end_time   = datetime.fromtimestamp(max(timestamps), timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    # ----------- SUMMARY WITH LLM (Reste inchangé) -----------

    prompt = f"""
    Tu es un expert cybersécurité. Voici les actions détectées sur un ordinateur :

    {logs_text}

    Explique clairement en racontant ce que la personne a fait , pourquoi c'est suspect, quels risques pour l'ordinateur,
    et suggère des recommandations simples. Contexte non technique. 
    mets une paragraphe bien écrite,fluide et claire.
    ignore les screenshots,c'est nous qui ont fait les screenshot pour savoir ce qu'il a fait
    Période : {start_time} -> {end_time}.
    """

    client = InferenceClient(api_key=hf_token)
    completion = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000
    )
    summary_paragraph = completion.choices[0].message.content.strip()
    if not summary_paragraph.endswith('.'):
        summary_paragraph += '.'

    intrusion_duration_seconds = max(timestamps) - min(timestamps)
    duration_timedelta = timedelta(seconds=intrusion_duration_seconds)
    
    # Obtenir les secondes totales (en ignorant les microsecondes)
    total_seconds = int(duration_timedelta.total_seconds())

    # Calculer Jours, Heures, Minutes, Secondes
    days = total_seconds // (3600 * 24)
    hours = (total_seconds // 3600) % 24
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    # Formater la durée en HH:MM:SS ou Jours, HH:MM:SS si nécessaire
    if days > 0:
        intrusion_duration = f"{days} jour{'s' if days > 1 else ''}, {hours:02}:{minutes:02}:{seconds:02}"
    else:
        # Format standard HH:MM:SS
        intrusion_duration = f"{hours:02}:{minutes:02}:{seconds:02}" 

    summary_json = {
        "total_actions": len(logs), # Utiliser len(logs) car table_data a une ligne d'entête
        "intrusion_start": start_time,
        "intrusion_duration": intrusion_duration
    }

    summary_json_path = os.path.join(outputs_folder, "intrusion_summary.json")
    with open(summary_json_path, "w", encoding="utf-8") as f:
        json.dump(summary_json, f, indent=4, ensure_ascii=False)

    # ----------- PDF STYLES SUITE (Styles déjà définis) -----------

    title_style = ParagraphStyle(
        "Title",
        parent=styles["Title"],
        fontName="DejaVu",
        fontSize=24,
        textColor=colors.HexColor("#D91E18"),
        alignment=1,  # center
        spaceAfter=20
    )

    header_style = ParagraphStyle(
        "Header",
        parent=styles["Heading2"],
        fontName="DejaVu",
        fontSize=15,
        textColor=colors.HexColor("#004C99"),
        spaceAfter=10
    )
    
    pdf_path = os.path.join(outputs_folder, "intrusion_report.pdf")
    doc = SimpleDocTemplate(
        pdf_path, pagesize=A4,
        rightMargin=1.8*cm, leftMargin=1.8*cm,
        topMargin=1.8*cm, bottomMargin=2*cm
    )

    elements = []

    # Le contenu du résumé (summary_paragraph) est aussi encapsulé par Paragraph,
    # donc il utilisera correctement la police "DejaVu"
    elements.append(Paragraph("⚠️ RAPPORT D'INTRUSION INFORMATIQUE", title_style))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph(f"Suspect identifié : <b>{person['name']}</b>", body_style))
    elements.append(Paragraph(f"Période d'activité : <b>{start_time}</b> → <b>{end_time}</b>", body_style))
    elements.append(Paragraph(f"Durée : {intrusion_duration}", body_style))
    elements.append(Spacer(1, 10))

    if os.path.isfile(person["image_local_path"]):
        img = Image(person["image_local_path"], width=2.2*inch, height=2.2*inch)
        img.hAlign = "CENTER"
        elements.append(img)
        elements.append(Spacer(1, 14))

    elements.append(Paragraph("1️-Résumé des actions suspectes", header_style))
    elements.append(Paragraph(summary_paragraph, body_style))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("2️-Détails des activités détectées", header_style))

    # ----------- TABLEAU FINAL (Reste inchangé) -----------

    col_widths = [4*cm, 5*cm, 7*cm]

    table = Table(table_data, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#2C3E50")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTNAME", (0,0), (-1,0), "DejaVu"), # Entête utilise "DejaVu"
        # La ligne suivante n'est plus nécessaire car le contenu est déjà Paragraph(..., cell_style)
        # ("FONTNAME", (0,1), (-1,-1), "DejaVu"), 
        ("FONTSIZE", (0,0), (-1,-1), 9),
        ("GRID", (0,0), (-1,-1), 0.3, colors.grey),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.whitesmoke, colors.lightgrey]),
        ("LEFTPADDING", (0,0), (-1,-1), 3),
        ("RIGHTPADDING", (0,0), (-1,-1), 3),
    ]))

    elements.append(table)

    doc.build(elements)

    print(f" PDF généré ➜ {pdf_path}")
    print(f"Résumé JSON généré ➜ {summary_json_path}")

    return pdf_path, summary_json_path


if __name__ == "__main__":
    # Assurez-vous que les chemins et le token sont corrects pour le test local
    try:
        result = generate_intrusion_report(
            "/home/ubuntu/shacks-2025/logs/json_final.json",
            output_folder="/home/ubuntu/shacks-2025/my_reports",
            model_name="openai/gpt-oss-120b",
            hf_token=os.getenv("HF_API_TOKEN")
        )
        print("Résultat :", result)
    except Exception as e:
        print(f"Erreur lors de la génération du rapport : {e}")
        print("Vérifiez le chemin vers 'DejaVuSans.ttf' et la validité du HF_API_TOKEN.")