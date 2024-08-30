import cv2
import numpy as np
import os
import json
from config import Config
import generate_pdf

def find_tangents_using_hough(skeleton, point, roi_size=20):
    x, y = point
    roi = skeleton[max(y - roi_size, 0):min(y + roi_size, skeleton.shape[0]),
          max(x - roi_size, 0):min(x + roi_size, skeleton.shape[1])]
    edges = cv2.Canny(roi, 50, 150, apertureSize=3)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=10, minLineLength=10, maxLineGap=5)
    tangents = []

    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            tangents.append((x2 - x1, y2 - y1))
    return tangents

def calculate_angle_between_vectors(v1, v2):
    dx1, dy1 = v1
    dx2, dy2 = v2

    dot_product = dx1 * dx2 + dy1 * dy2

    norm_v1 = np.hypot(dx1, dy1)
    norm_v2 = np.hypot(dx2, dy2)

    cosine_angle = dot_product / (norm_v1 * norm_v2)
    cosine_angle = np.clip(cosine_angle, -1.0, 1.0)

    angle_deg = np.degrees(np.arccos(cosine_angle))
    return angle_deg, dot_product

def calculate_average_vector(vectors):
    if not vectors:
        return None
    avg_vector = (sum(v[0] for v in vectors) / len(vectors), sum(v[1] for v in vectors) / len(vectors))
    return avg_vector

def draw_extended_line(image, point, vector, length=200, color=(255, 0, 0), thickness=2, reverse=False):
    x, y = point
    dx, dy = vector
    norm = np.hypot(dx, dy)
    dx, dy = dx / norm, dy / norm

    if reverse:
        start_point = (int(x + length * dx), int(y + length * dy))
        end_point = (int(x - length * dx), int(y - length * dy))
    else:
        start_point = (int(x - length * dx), int(y - length * dy))
        end_point = (int(x + length * dx), int(y + length * dy))

    cv2.line(image, start_point, end_point, color, thickness)

def draw_line(image, start_point, end_point, color, thickness):
    cv2.line(image, start_point, end_point, color, thickness)

def draw_vector(image, start_point, vector, color=(0, 0, 0), thickness=2):
    x, y = start_point
    dx, dy = vector
    end_point = (int(x + dx), int(y + dy))
    cv2.arrowedLine(image, (x, y), end_point, color, thickness)

def find_intersection(P1, v1, P2, v2):
    x1, y1 = P1
    x2, y2 = P2
    dx1, dy1 = v1
    dx2, dy2 = v2

    A = np.array([[dx1, -dx2], [dy1, -dy2]])
    b = np.array([x2 - x1, y2 - y1])

    try:
        t = np.linalg.solve(A, b)
        intersection = (int(x1 + t[0] * dx1), int(y1 + t[0] * dy1))
        return intersection
    except np.linalg.LinAlgError:
        return None

def draw_arc(image, center, radius, start_angle, end_angle, color, thickness):
    axes = (radius, radius)
    cv2.ellipse(image, center, axes, 0, start_angle, end_angle, color, thickness)

def draw_intersection_point(image, point, radius=5, color=(0, 255, 0)):
    cv2.circle(image, point, radius, color, -1)

def draw_border(image, direction, color=(0, 0, 255), thickness=2):
    height, width = image.shape[:2]
    if direction == 'up':
        cv2.line(image, (0, 0), (width - 1, 0), color, thickness)
    elif direction == 'down':
        cv2.line(image, (0, height - 1), (width - 1, height - 1), color, thickness)
    elif direction == 'left':
        cv2.line(image, (0, 0), (0, height - 1), color, thickness)
    elif direction == 'right':
        cv2.line(image, (width - 1, 0), (width - 1, height - 1), color, thickness)

def show_results(gray_image, skeleton_overlay, P1_skeleton, P3_skeleton, roi, save_directory, direction):
    result_image = cv2.cvtColor(gray_image, cv2.COLOR_GRAY2BGR)
    result_image[skeleton_overlay == 255] = (0, 255, 0)

    tangents_P1 = find_tangents_using_hough(skeleton_overlay, P1_skeleton)
    tangents_P3 = find_tangents_using_hough(skeleton_overlay, P3_skeleton)
    avg_vector_P1 = calculate_average_vector(tangents_P1)
    avg_vector_P3 = calculate_average_vector(tangents_P3)

    if avg_vector_P1:
        draw_extended_line(result_image, P1_skeleton, avg_vector_P1, length=600, color=(255, 0, 0), thickness=2,
                           reverse=False)
    if avg_vector_P3:
        draw_extended_line(result_image, P3_skeleton, avg_vector_P3, length=600, color=(0, 0, 255), thickness=4,
                           reverse=False)

    if avg_vector_P1 and avg_vector_P3:
        intersection = find_intersection(P1_skeleton, avg_vector_P1, P3_skeleton, avg_vector_P3)
        if intersection:
            draw_intersection_point(result_image, intersection, radius=5, color=(0, 255, 255))

            # Calculer v'_1 (vecteur translanté de avg_vector_P1 au point d'intersection)
            v_prime_1 = (P1_skeleton[0] - intersection[0], P1_skeleton[1] - intersection[1])

            # Ajuster v'_1 pour qu'il pointe vers le bord rouge selon la direction
            if direction == 'up' and v_prime_1[1] > 0:
                v_prime_1 = (-v_prime_1[0], -v_prime_1[1])
            elif direction == 'down' and v_prime_1[1] < 0:
                v_prime_1 = (-v_prime_1[0], -v_prime_1[1])
            elif direction == 'left' and v_prime_1[0] > 0:
                v_prime_1 = (-v_prime_1[0], -v_prime_1[1])
            elif direction == 'right' and v_prime_1[0] < 0:
                v_prime_1 = (-v_prime_1[0], -v_prime_1[1])

            # draw_vector(result_image, intersection, v_prime_1, color=(0, 0, 0), thickness=2)

            # Calculer v'_2 (vecteur translanté de avg_vector_P3 au point d'intersection)
            v_prime_2 = (intersection[0] - P3_skeleton[0], intersection[1] - P3_skeleton[1])

            # Ajuster v'_2 pour qu'il pointe vers le bord rouge selon la direction
            if direction == 'up' and v_prime_2[1] < 0:
                v_prime_2 = (-v_prime_2[0], -v_prime_2[1])
            elif direction == 'down' and v_prime_2[1] > 0:
                v_prime_2 = (-v_prime_2[0], -v_prime_2[1])
            elif direction == 'left' and v_prime_2[0] < 0:
                v_prime_2 = (-v_prime_2[0], -v_prime_2[1])
            elif direction == 'right' and v_prime_2[0] > 0:
                v_prime_2 = (-v_prime_2[0], -v_prime_2[1])

            # Calculer le produit scalaire entre v'_1 et v'_2
            _, dot_product = calculate_angle_between_vectors(v_prime_1, v_prime_2)

            # Inverser v'_2 si le produit scalaire est négatif
            if dot_product < 0:
                v_prime_2 = (-v_prime_2[0], -v_prime_2[1])

            # draw_vector(result_image, intersection, v_prime_2, color=(0, 0, 0), thickness=2)

            # Calculer l'angle θ entre v'_1 et v'_2
            theta, _ = calculate_angle_between_vectors(v_prime_1, v_prime_2)
            theta = round(theta, 2)  # Arrondir l'angle θ
            print(f"Angle de déviation θ : {theta} degrés")  # Afficher l'angle dans le terminal

            # Calculer les angles pour dessiner l'arc
            angle_alpha = np.degrees(np.arctan2(v_prime_1[1], v_prime_1[0])) % 360
            angle_beta = np.degrees(np.arctan2(v_prime_2[1], v_prime_2[0])) % 360

            # Arrondir les angles alpha et beta
            angle_alpha = round(angle_alpha)
            angle_beta = round(angle_beta)

            # Afficher les valeurs des angles
            # print(f"angle_alpha : {angle_alpha} degrés")
            # print(f"angle_beta : {angle_beta} degrés")

            # Calculer le produit vectoriel en 2D pour déterminer la position relative des vecteurs
            cross_product = v_prime_1[0] * v_prime_2[1] - v_prime_1[1] * v_prime_2[0]

            # Si le produit vectoriel est positif, v'_1 est à gauche de v'_2, sinon l'inverse
            if cross_product > 0:
                # v'_1 est à gauche de v'_2
                start_angle = angle_alpha
                end_angle = angle_alpha + theta
            else:
                # v'_2 est à gauche de v'_1
                start_angle = angle_beta
                end_angle = angle_beta + theta

            # Dessiner l'arc
            draw_arc(result_image, intersection, radius=100, start_angle=start_angle, end_angle=end_angle,
                     color=(0, 255, 255), thickness=5)

            # Calculer l'angle θ entre v'_1 et v'_2
            theta, _ = calculate_angle_between_vectors(v_prime_1, v_prime_2)
            theta = round(theta, 2)  # Arrondir l'angle θ
            print(f"Angle de déviation θ : {theta} degrés")  # Afficher l'angle dans le terminal

            # Calculer les angles pour dessiner l'arc

    # Dessiner la bordure en fonction de la direction
    draw_border(result_image, direction)

    result_image_path = os.path.join(save_directory, "result_image.png")
    cv2.imwrite(result_image_path, result_image)

    cv2.imshow('Resultats', result_image)
    key = cv2.waitKey(0)
    cv2.destroyAllWindows()

    if key == ord('r'):
        config_path = os.path.join(save_directory, 'config.json')

        # Créer le fichier config.json avec un contenu par défaut si il n'existe pas
        config_data = {
            'theta': theta,
            'save_directory': save_directory
        }

        # Sauvegarder les données dans config.json
        with open(config_path, 'w') as f:
            json.dump(config_data, f, indent=4)

        # Générer le PDF
        generate_pdf.generate_pdf(config_path)

        # Afficher la direction dans le terminal
        print(f"Direction : {direction}")

