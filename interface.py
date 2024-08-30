import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import cv2
import os
import numpy as np
from skimage import morphology
import calculs  # Importer le module calculs pour afficher les résultats

class ImageProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sélectionneur d'image")

        self.image_path = tk.StringVar()
        self.save_directory = None  # Ajouter la variable save_directory
        self.direction = None  # Ajouter la variable direction

        # Bouton pour ouvrir la boîte de dialogue de sélection de fichier
        self.select_button = tk.Button(root, text="Choisir une image", command=self.select_image)
        self.select_button.pack(pady=20)

        # Étiquette pour afficher le chemin de l'image sélectionnée
        self.path_label = tk.Label(root, textvariable=self.image_path, wraplength=400)
        self.path_label.pack(pady=20)

        # Section pour choisir la direction
        self.direction_frame = tk.Frame(root)
        self.direction_frame.pack(pady=20)

        self.up_button = tk.Button(self.direction_frame, text="Up", command=lambda: self.set_direction("up"))
        self.up_button.grid(row=0, column=1)

        self.left_button = tk.Button(self.direction_frame, text="Left", command=lambda: self.set_direction("left"))
        self.left_button.grid(row=1, column=0)

        self.right_button = tk.Button(self.direction_frame, text="Right", command=lambda: self.set_direction("right"))
        self.right_button.grid(row=1, column=2)

        self.down_button = tk.Button(self.direction_frame, text="Down", command=lambda: self.set_direction("down"))
        self.down_button.grid(row=2, column=1)

        # Bouton pour lancer le traitement de l'image
        self.process_button = tk.Button(root, text="Traiter l'image", command=self.process_image)
        self.process_button.pack(pady=20)

        # Étiquette pour afficher les touches de commande disponibles
        self.command_label = tk.Label(root, text="Commandes disponibles:\n"
                                                 "p - Déplacer P1 vers la gauche/haut\n"
                                                 "m - Déplacer P1 vers la droite/bas\n"
                                                 "u - Déplacer P3 vers la droite/bas\n"
                                                 "d - Déplacer P3 vers la gauche/haut\n"
                                                 "r - Générer un rapport\n"
                                                 "k - Afficher les résultats\n"
                                                 "q ou Esc - Quitter", justify=tk.LEFT, anchor="w")
        self.command_label.pack(pady=20)

    def set_direction(self, direction):
        self.direction = direction
        messagebox.showinfo("Direction", f"La direction choisie est : {direction}")

    def select_image(self):
        file_path = filedialog.askopenfilename(
            title="Sélectionner une image",
            filetypes=[("Fichiers image", "*.jpg *.jpeg *.png *.bmp *.gif")]
        )
        if file_path:
            self.image_path.set(file_path)
            self.save_directory = os.path.dirname(file_path)  # Définir le répertoire de sauvegarde
        else:
            messagebox.showinfo("Information", "Aucun fichier sélectionné")

    def process_image(self):
        # Chemin de l'image d'origine
        image_path = self.image_path.get()
        if not image_path:
            messagebox.showerror("Erreur", "Veuillez sélectionner une image avant de procéder.")
            return

        if not self.direction:
            messagebox.showerror("Erreur", "Veuillez choisir une direction avant de procéder.")
            return

        # Utiliser save_directory pour obtenir le répertoire de sauvegarde
        directory = self.save_directory

        # Renommer l'image sélectionnée en 'color_image.png'
        color_image_path = os.path.join(directory, "color_image.png")
        os.rename(image_path, color_image_path)

        # Charger l'image renommée
        image = cv2.imread(color_image_path)
        if image is None:
            messagebox.showerror("Erreur", f"Image non trouvée à l'emplacement : {color_image_path}")
            return

        # Convertir l'image en niveaux de gris et la sauvegarder sous 'grey_image.png'
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray_image_path = os.path.join(directory, "grey_image.png")
        cv2.imwrite(gray_image_path, gray_image)

        # Traitement de l'image
        median_filtered = cv2.medianBlur(gray_image, 3)
        gaussian_filtered = cv2.GaussianBlur(median_filtered, (3, 3), 0.25)
        _, binary_mask = cv2.threshold(gaussian_filtered, 0, 255, cv2.THRESH_BINARY)
        binary_mask = binary_mask // 255
        skeleton = morphology.skeletonize(binary_mask)
        skeleton_overlay = np.uint8(skeleton * 255)
        kernel = np.ones((3, 3), np.uint8)
        thick_skeleton = cv2.dilate(skeleton_overlay, kernel, iterations=1)

        height, width = gray_image.shape
        horizontal = width > height

        side = max(width, height)
        self.P1_pos = side // 4
        self.P3_pos = 3 * side // 4

        def calculate_intersection_points():
            intersection_points = {
                'P1_skeleton': None, 'P1_top_border': None, 'P1_bottom_border': None,
                'P3_skeleton': None, 'P3_top_border': None, 'P3_bottom_border': None
            }
            if horizontal:
                x1, x3 = self.P1_pos, self.P3_pos
                intersection_points['P1_top_border'] = (x1, 0)
                intersection_points['P1_bottom_border'] = (x1, height - 1)
                for y in range(height):
                    if thick_skeleton[y, x1] == 255:
                        intersection_points['P1_skeleton'] = (x1, y)
                        break
                intersection_points['P3_top_border'] = (x3, 0)
                intersection_points['P3_bottom_border'] = (x3, height - 1)
                for y in range(height):
                    if thick_skeleton[y, x3] == 255:
                        intersection_points['P3_skeleton'] = (x3, y)
                        break
            else:
                y1, y3 = self.P1_pos, self.P3_pos
                intersection_points['P1_top_border'] = (0, y1)
                intersection_points['P1_bottom_border'] = (width - 1, y1)
                for x in range(width):
                    if thick_skeleton[y1, x] == 255:
                        intersection_points['P1_skeleton'] = (x, y1)
                        break
                intersection_points['P3_top_border'] = (0, y3)
                intersection_points['P3_bottom_border'] = (width - 1, y3)
                for x in range(width):
                    if thick_skeleton[y3, x] == 255:
                        intersection_points['P3_skeleton'] = (x, y3)
                        break
            return intersection_points

        def update_display():
            overlay_image = cv2.cvtColor(gray_image, cv2.COLOR_GRAY2BGR)
            overlay_image[thick_skeleton == 255] = (255, 255, 255)
            if horizontal:
                line_positions = [(self.P1_pos, 0, self.P1_pos, height), (self.P3_pos, 0, self.P3_pos, height)]
            else:
                line_positions = [(0, self.P1_pos, width, self.P1_pos), (0, self.P3_pos, width, self.P3_pos)]
            for (x1, y1, x2, y2) in line_positions:
                cv2.line(overlay_image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            intersection_points = calculate_intersection_points()
            for label in ['P1', 'P3']:
                for point_type in ['top_border', 'skeleton', 'bottom_border']:
                    point_name = f"{label}_{point_type}"
                    point = intersection_points[point_name]
                    if point is not None:
                        cv2.circle(overlay_image, point, 5, (0, 0, 255), -1)
            cv2.imshow('Fenetre Interactive', overlay_image)
            return intersection_points

        def handle_key(event):
            if event == ord('p'):
                self.P1_pos = max(0, self.P1_pos - 5)
            elif event == ord('m'):
                self.P1_pos = min(self.P3_pos - 1, self.P1_pos + 5)
            elif event == ord('u'):
                self.P3_pos = min(side - 1, self.P3_pos + 5)
            elif event == ord('d'):
                self.P3_pos = max(self.P1_pos + 1, self.P3_pos - 5)
            elif event == ord('r'):
                # Ajouter la logique pour générer un rapport
                self.generate_report()
            intersection_points = update_display()
            return intersection_points

        def generate_report(self):
            # Exemple de logique pour générer un rapport
            report_path = os.path.join(self.save_directory, "rapport.txt")
            with open(report_path, 'w') as report_file:
                report_file.write("Rapport généré\n")
                report_file.write(f"Direction: {self.direction}\n")
                report_file.write(f"Positions P1: {self.P1_pos}, P3: {self.P3_pos}\n")
            messagebox.showinfo("Rapport", f"Rapport sauvegardé à l'emplacement : {report_path}")

        intersection_points = update_display()

        while True:
            key = cv2.waitKey(0)
            if key == ord('q') or key == 27:
                cv2.destroyAllWindows()
                break
            elif key == ord('k'):
                calculs.show_results(
                    gray_image=gray_image,
                    skeleton_overlay=thick_skeleton,
                    P1_skeleton=intersection_points['P1_skeleton'],
                    P3_skeleton=intersection_points['P3_skeleton'],
                    roi={
                        'P1_top_border': intersection_points['P1_top_border'],
                        'P1_bottom_border': intersection_points['P1_bottom_border'],
                        'P3_top_border': intersection_points['P3_top_border'],
                        'P3_bottom_border': intersection_points['P3_bottom_border']
                    },
                    save_directory=directory,  # Passer save_directory à show_results
                    direction=self.direction  # Passer la direction à show_results
                )
                cv2.destroyAllWindows()
                break
            else:
                intersection_points = handle_key(key)

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageProcessorApp(root)
    root.mainloop()
