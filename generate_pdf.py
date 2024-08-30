from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image, Spacer, PageBreak
from reportlab.graphics.shapes import Drawing, Line
from reportlab.lib.units import inch
import json
import os
from PIL import Image as PILImage


def create_separator(width, line_length, stroke_width=1, color=colors.HexColor("#333333")):
    """Crée un dessin avec une ligne horizontale de longueur spécifiée."""
    drawing = Drawing(width, 1)  # Hauteur du dessin fixée à 1 pour le séparateur
    x_start = (width - line_length) / 2
    x_end = x_start + line_length
    drawing.add(Line(x_start, 0.5, x_end, 0.5, strokeWidth=stroke_width, strokeColor=color))
    return drawing


def generate_pdf(config_path):
    # Charger les données de configuration
    with open(config_path, 'r') as f:
        config_data = json.load(f)

    # Récupération des informations de configuration
    save_directory = config_data.get('save_directory', '')
    angle_deviation = config_data.get('theta', 0)

    # Construction des chemins vers les images
    color_image_path = os.path.join(save_directory, "color_image.png")
    grey_image_path = os.path.join(save_directory, "grey_image.png")
    result_image_path = os.path.join(save_directory, "result_image.png")

    output_pdf_path = os.path.join(save_directory, "report.pdf")

    # Chemins des images fixes
    fixed_image2_path = r"C:\Users\anton\Analyse_angulaire\peyronie2.jpg"

    # Réduire les marges
    doc = SimpleDocTemplate(output_pdf_path, pagesize=A4,
                            rightMargin=20, leftMargin=20,
                            topMargin=20, bottomMargin=20)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'Title', parent=styles['Title'],
        fontName='Helvetica-Bold',
        fontSize=22, textColor=colors.HexColor("#333333"),
        alignment=1, spaceAfter=12)

    subtitle_style = ParagraphStyle(
        'Subtitle', parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=14, textColor=colors.HexColor("#555555"),
        alignment=1, spaceAfter=6)

    caption_style = ParagraphStyle(
        'Caption', parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=12, textColor=colors.HexColor("#555555"),
        alignment=1, spaceAfter=6, leading=18 * 1.2)

    # Page de couverture
    cover_title_style = ParagraphStyle(
        'CoverTitle', parent=styles['Title'],
        fontSize=26, alignment=1, spaceAfter=12,
        textColor=colors.HexColor("#333333"))

    cover_subtitle_style = ParagraphStyle(
        'CoverSubtitle', parent=styles['Normal'],
        fontSize=18, alignment=1, spaceAfter=6,
        textColor=colors.HexColor("#555555"))

    cover_text_style = ParagraphStyle(
        'CoverText', parent=styles['Normal'],
        fontSize=12, alignment=1, spaceAfter=12,
        textColor=colors.HexColor("#555555"),
        leftIndent=20, rightIndent=20, leading=18 * 1.2)

    # Nouveau style pour le grand titre
    grand_title_style = ParagraphStyle(
        'GrandTitle', parent=styles['Title'],
        fontSize=60, alignment=1, spaceAfter=36,
        textColor=colors.HexColor("#333333"))

    story = []

    # Ajouter le grand titre en haut de la page de couverture
    story.append(Paragraph("SEXOLOGIE", grand_title_style))
    story.append(Spacer(1, 50))  # Réduit l'espacement sous le grand titre

    # Ajouter la page de couverture
    story.append(Paragraph("Rapport d'Analyse Angulaire", cover_title_style))
    story.append(Spacer(1, 12))  # Espacement après le séparateur
    # story.append(create_separator(A4[0], 150))  # Séparateur
    story.append(Spacer(1, 12))
    story.append(Paragraph("Calcul de l'angle de déviation du pénis", title_style))
    story.append(Spacer(1, 12))
    # story.append(create_separator(A4[0], 150))  # Séparateur
    story.append(Spacer(1, 12))
    story.append(Paragraph("Antony, Sexologue bénévole retraité", subtitle_style))
    story.append(Spacer(1, 12))
   # story.append(create_separator(A4[0], 150))  # Séparateur
    story.append(Spacer(1, 12))
    story.append(Paragraph(
        "Ce résultat ne peut être interprété que par un médecin"
        "<br/>à consulter en cas de gêne ou de douleurs au niveau du pénis"
        "<br/>ou de douleurs pour la partenaire sexuelle.", cover_text_style))
    story.append(Spacer(1, 12))
    # story.append(create_separator(A4[0], 150))  # Séparateur
    story.append(Spacer(1, 12))
    story.append(Paragraph(
        "<br/><br/><br/><br/>Antony, sexologue bénévole à la retraite"
        "<br/>Passionné par la photographie et l'intelligence artificielle,"
        "<br/>j'ai créé cette IA à usage personnel que je supervise."
        "<br/>N'hésitez pas à me contacter par mail pour toute question sexuelle."
        "<br/>C'est gratuit, sans engagement,"
        "<br/>le secret professionnel est une garantie fondamentale."
        "<br/><br/>antony.sexolog@gmail.com", cover_text_style))

    # Ajouter le texte supplémentaire après l'adresse e-mail
    story.append(Spacer(1, 12))
    story.append(Paragraph(
        "L'angle de déviation du pénis au lieu d'être mesuré avec un 'rapporteur' est calculé par une IA à partir d'une photo prise à l'aide d'un smartphone. C'est une première mondiale",
        cover_text_style))
    story.append(PageBreak())

    # Dimensions maximales disponibles pour une image dans la page (moins un espace de sécurité)
    max_width = A4[0] - 60  # Réduire encore un peu la largeur maximale pour laisser un espace
    max_height = A4[1] - 120  # Réduire plus la hauteur maximale pour les autres contenus

    # Fonction pour redimensionner une image pour s'adapter à la page
    def add_image(image_path, caption):
        if os.path.exists(image_path):
            with PILImage.open(image_path) as img:
                width, height = img.size
                aspect_ratio = width / height

                # Redimensionner si nécessaire
                if width > max_width or height > max_height:
                    if width / max_width > height / max_height:
                        width = max_width
                        height = width / aspect_ratio
                    else:
                        height = max_height
                        width = height * aspect_ratio

                # Insérer l'image dans le document
                pdf_image = Image(image_path, width=width, height=height)
                story.append(pdf_image)
                story.append(Paragraph(caption, caption_style))
                story.append(Spacer(1, 12))
        else:
            print(f"Image non trouvée: {image_path}")

    # Ajouter les images fixes avec leurs légendes
    fixed_images = [
        (fixed_image2_path,
         "<br/><br/>L'IA (Intelligence Artificielle) calcule l'angle de déviation, pour toute courbure du pénis.")
    ]

    for image_path, caption in fixed_images:
        add_image(image_path, caption)

    # Ajouter les autres images avec leurs légendes
    images = [
        (color_image_path,
         "Image en couleur après segmentation sémantique<br/> c'est à dire après détourage et découpe"),
        (result_image_path,
         "<br/><br/>L'IA (Intelligence Artificielle) a dessiné<br/>en vert : l'axe médian obtenu par squelettisation<br/>"
         "en rouge : une tangente en un point du chemin médian<br/> en bleu : une seconde tangente en un autre point du chemin médian"
         "<br/> un point jaune qui représente l'intersection des tangentes"
         "<br/> un arc jaune entre les tangentes et qui représente l'angle de courbure")
    ]

    for image_path, caption in images:
        add_image(image_path, caption)

    # Ajouter l'angle de déviation comme conclusion
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"La courbure du pénis est de {angle_deviation:.0f} degrés.", title_style))

    # Générer le PDF
    doc.build(story)

    print(f"PDF généré avec succès : {output_pdf_path}")


if __name__ == "__main__":
    config_path = r"C:\Users\anton\Analyse_angulaire\Dossier_0013\config.json"
    generate_pdf(config_path)
