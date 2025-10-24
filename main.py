import pygame
from pygame.locals import *
import sys
from PIL import Image

pygame.init()




# Dimensiones de la ventana
WIDTH, HEIGHT = 900, 600
window = pygame.display.set_mode((WIDTH, HEIGHT))

# Nombre del juegos
pygame.display.set_caption("Brujúla")

# Colores
BROWN = (139, 69, 19)  
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (200, 200, 200)  
BEIGE = (213, 195, 153)


# Tamaño del cuadro de diálogo y personaje
DIALOG_WIDTH, DIALOG_HEIGHT = 850, 320
ARROW_SIZE = 20
MARGIN = 5
CHARACTER_WIDTH, CHARACTER_HEIGHT = 130, 150


# Redimensionar fondo
fondo = Image.open('Assets/imagenes/Fondofinal.png')
max_tamano = (900, 620)
fondo.thumbnail(max_tamano)
fondo.save("Assets/imagenes/Fondofinal_redimensionar.png")
background_image = pygame.image.load("Assets/imagenes/Fondofinal.png")



class Character:
    def __init__(self, images_right, images_left, idle_images_right, idle_images_left, speed):
        self.images_right = images_right
        self.images_left = images_left
        self.idle_images_right = idle_images_right
        self.idle_images_left = idle_images_left
        self.image = self.images_right[0]
        self.rect = self.image.get_rect(topleft=(2, 440))
        self.speed = 6
        self.x = float(self.rect.x)
        self.frame_count = 60
        self.frame_delay = 4
        self.frame_delay1 = 10
        self.moving = False
        self.can_move = True

    @staticmethod
    def load_images(folder, character_number):
        images_right = []
        images_left = []
        for num in range(4):
            img_path = f'Assets/Imagenes/{folder}{character_number}/imagen{num}.png'
            img_right = pygame.image.load(img_path)
            if folder == 'pers_idle':
                if num % 2 == 0:
                    img_right = pygame.transform.scale(img_right, (CHARACTER_WIDTH, CHARACTER_HEIGHT - 10))
                else:
                    img_right = pygame.transform.scale(img_right, (CHARACTER_WIDTH, CHARACTER_HEIGHT + 10))
            else:
                img_right = pygame.transform.scale(img_right, (CHARACTER_WIDTH, CHARACTER_HEIGHT))
            img_left = pygame.transform.flip(img_right, True, False)
            images_right.append(img_right)
            images_left.append(img_left)
        return images_right, images_left

    def move(self, keys):
        if keys[K_LEFT] and self.can_move:
            self.x -= self.speed
            self.image = self.images_left[self.frame_count // self.frame_delay % len(self.images_left)]
            self.moving = True
        elif keys[K_RIGHT] and self.can_move:
            self.x += self.speed
            self.image = self.images_right[self.frame_count // self.frame_delay % len(self.images_right)]
            self.moving = True
        self.frame_count += 1
        if not self.moving:
            idle_frame = self.frame_count // self.frame_delay1 % len(self.idle_images_right)
            old_midbottom = self.rect.midbottom
            self.image = self.idle_images_right[idle_frame]
            self.rect = self.image.get_rect()
            self.rect.midbottom = old_midbottom
        self.rect.x = int(self.x)

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        

class Dialogue:
    def __init__(self, question, options, pos):
        self.question = question
        self.options = options  # Lista de diccionarios con "options", "points_humanas", "points_exactas"
        self.pos = pos
        self.dialogue_shown = False
        self.selected_option = None

    def wrap_text(self, text, font, max_width):
        words = text.split(' ')
        lines = []
        current_line = []

        for word in words:
            current_line.append(word)
            width, _ = font.size(' '.join(current_line))
            if width > max_width:
                current_line.pop()
                lines.append(' '.join(current_line))
                current_line = [word]

        lines.append(' '.join(current_line))
        return lines

    def handle_selection(self, selected_option_index):
        """Manejar selección de respuesta."""
        self.selected_option = selected_option_index
        # El cálculo de puntos se hace fuera de esta clase, ya no es necesario devolver ningún valor aquí.

    def draw(self, surface, selected_option=None):
        x, y = self.pos
        box_rect = pygame.Rect(x, y, DIALOG_WIDTH, DIALOG_HEIGHT)
        arrow_points = [
            (x + DIALOG_WIDTH // 2 - ARROW_SIZE // 2, y + DIALOG_HEIGHT),
            (x + DIALOG_WIDTH // 2 + ARROW_SIZE // 2, y + DIALOG_HEIGHT),
            (x + DIALOG_WIDTH // 2, y + DIALOG_HEIGHT + ARROW_SIZE)
        ]
        
        pygame.draw.rect(surface, BLACK, box_rect)
        pygame.draw.rect(surface, BROWN, box_rect.inflate(-1 * MARGIN, -1 * MARGIN))
        pygame.draw.polygon(surface, BLACK, arrow_points)

        question_rect_height = DIALOG_HEIGHT // 3
        options_rect_height = (DIALOG_HEIGHT - question_rect_height) // 2
        part_width = DIALOG_WIDTH // 2
        font = pygame.font.SysFont(None, 24)
        
        # Dibujar la pregunta
        question_rect = pygame.Rect(x, y, DIALOG_WIDTH, question_rect_height)
        pygame.draw.rect(surface, BLACK, question_rect, 1)
        wrapped_question = self.wrap_text(self.question, font, DIALOG_WIDTH - 1 * MARGIN)
        for i, line in enumerate(wrapped_question):
            question_surf = font.render(line, True, BLACK)
            question_text_rect = question_surf.get_rect(topleft=(x + MARGIN, y + i * 30))
            surface.blit(question_surf, question_text_rect.topleft)
        
        # Dibujar las opciones
        option_rects = []
        for i, option in enumerate(self.options):
            option_text = option['options']
            part_x = x + (i % 2) * part_width
            part_y = y + question_rect_height + (i // 2) * options_rect_height
            option_rect = pygame.Rect(part_x, part_y, part_width, options_rect_height)
            
            # Resaltar opción seleccionada
            if i == selected_option:
                pygame.draw.rect(surface, BROWN, option_rect.inflate(-5 * MARGIN, -5 * MARGIN)) 
            pygame.draw.rect(surface, BLACK, option_rect, 1)
            
            # Ajustar el texto de la opción
            wrapped_option = self.wrap_text(option_text, font, part_width - 2 * MARGIN)
            for j, line in enumerate(wrapped_option):
                option_color = GREEN if i == selected_option else BLACK
                option_surf = font.render(line, True, option_color)
                option_text_rect = option_surf.get_rect(topleft=(part_x + MARGIN, part_y + j * 30))
                surface.blit(option_surf, option_text_rect.topleft)
            
            option_rects.append(option_rect) 
        
        return question_rect, option_rects



def draw_start_screen():
    background_image = pygame.image.load('Assets/imagenes/portada.png')
    window.blit(background_image, (0, 0))
    pygame.display.flip()  # Actualizar la pantalla

    # Configurar fuente y botón "Iniciar Juego"
    button_font = pygame.font.SysFont(None, 48)
    button_text = button_font.render("Iniciar", True, GREY)
    button_rect = pygame.Rect(20, 480, 120, 60)
    pygame.draw.rect(window, WHITE, button_rect)
    pygame.draw.rect(window, GREY, button_rect, 2)
    text_rect = button_text.get_rect(center=button_rect.center)
    window.blit(button_text, text_rect)
    
    # Configurar fuente y botón "Ayuda"
    help_text = button_font.render("Ayuda", True, GREY)
    help_rect = pygame.Rect(768, 480, 120, 60)
    pygame.draw.rect(window, WHITE, help_rect)
    pygame.draw.rect(window, GREY, help_rect, 2)
    help_text_rect = help_text.get_rect(center=help_rect.center)
    window.blit(help_text, help_text_rect)
    
    pygame.display.flip()
    
    return button_rect, help_rect



def show_help_screen(window):
    """Muestra una pantalla con instrucciones del juego y un botón de 'Volver'."""
    help_running = True
    font = pygame.font.Font(None, 30)
    title_font = pygame.font.Font(None, 40)  # Fuente más grande para el título
    help_text = [
        "Instrucciones de Juego:",
        "",
        "1. Usa las flechas (<- | ->) para moverte, solo podrás hacerlo de izquierda a derecha.",
        "",
        "2. Llega hasta la mitad del pasillo de la biblioteca para activar el cuadro de dialogo.",
        "",
        "3. Selecciona respuestas haciendo clic en ellas, recuerda que si no haces clic en alguna respuesta no podrás avanzar a la siguiente.",
        "",
        "4. Para retroceder solo basta con ir hacia atrás con nuestro personaje.", 
        "",
        "5. Completa todos los niveles para obtener un puntaje.",
        "",
        "6. Estas preguntas son diseñadas con el fin de ayudarte como estudiante a coger tú énfasis ideal, no hay respuesta incorrecta y diviértete."
    ]
    
    # Configurar el botón "Volver" 
    button_font = pygame.font.SysFont(None, 48)
    button_text = button_font.render("Volver", True, GREY)
    back_rect = pygame.Rect(768, 480, 120, 60) 
    back_text_rect = button_text.get_rect(center=back_rect.center)

    while help_running:
        window.fill(BEIGE)

        # Dibujar el título
        title_surface = title_font.render(help_text[0], True, (0, 0, 0))
        window.blit(title_surface, (50, 50))
        y_offset = 50 + title_surface.get_height() + 20  # Ajustar el offset para el título y el espacio adicional

        # Dibujar el texto de instrucciones
        for line in help_text[1:]:  # Saltar el título
            if line == "":  # Si la línea está vacía, agregar un espacio extra
                y_offset += 10  # Espacio adicional entre pasos
                continue
            
            # Dividir la línea si es necesario
            words = line.split(' ')
            current_line = ""
            for word in words:
                test_line = current_line + word + ' '
                text_surface = font.render(test_line, True, (0, 0, 0))
                if text_surface.get_width() > window.get_width() - 100:  # Resta un margen de 100 píxeles
                    # Si excede, dibujar la línea actual y comenzar una nueva línea
                    text_surface = font.render(current_line, True, (0, 0, 0))
                    window.blit(text_surface, (50, y_offset))
                    current_line = word + ' '  # Reiniciar con la nueva palabra
                    y_offset += text_surface.get_height() + 10  # Incrementar el offset con espacio extra
                else:
                    current_line = test_line  # Continuar construyendo la línea actual
            
            # Dibuja la última línea si existe
            if current_line:
                text_surface = font.render(current_line, True, (0, 0, 0))
                window.blit(text_surface, (50, y_offset))
                y_offset += text_surface.get_height() + 10  # Incrementar el offset con espacio extra

        # Dibujar el botón de "Volver"
        pygame.draw.rect(window, WHITE, back_rect) 
        pygame.draw.rect(window, GREY, back_rect, 2)  
        window.blit(button_text, back_text_rect)  

        pygame.display.flip()  

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if back_rect.collidepoint(event.pos):
                    print("Botón 'Volver' presionado")
                    help_running = False 
                    return  




def final_level(window, total_points_humanas, total_points_exactas):
    """Muestra el personaje final en movimiento y el mensaje final."""
    
    # Cargar y redimensionar el fondo
    fondo = Image.open('Assets/imagenes/Fondofinal.png')
    max_tamano = (900, 620)
    fondo.thumbnail(max_tamano)
    fondo.save("Assets/imagenes/Fondofinal_redimensionar.png")
    background_image = pygame.image.load("Assets/imagenes/Fondofinal_redimensionar.png")

    # Determinar el énfasis basado en la puntuación final
    if total_points_humanas > total_points_exactas:
        enfasis = "Humanas"
    elif total_points_exactas > total_points_humanas:
        enfasis = "Exactas"
    else:
        enfasis = "Empate"

    # Dividir el mensaje en tres partes
    part1 = "!Felicitaciones, acabaste la prueba con éxito¡"
    part2 = f"Puntos para humanas: {total_points_humanas}   |   Puntos para exactas: {total_points_exactas}"
    part3 = f"Tú énfasis ideal es: !{enfasis}¡"

    # Cargar las imágenes de animación del personaje en reposo
    idle_images_right, _ = Character.load_images('pers_idle', 1) 
    # Crear una instancia del personaje
    character = Character(idle_images_right, [], [], [], speed=1)
    frame_index = 0


    # Configurar la fuente
    font = pygame.font.Font(None, 24) 
    # Crear una lista con las partes del mensaje
    lines = [part1, part2, part3]
    # Ajustar el tamaño del cuadro de diálogo según la cantidad de líneas
    dialogue_height = 150
    dialogue_width = max(440, max(len(line) for line in lines) * 10 + 20)  # Ancho del texto más margen
    # Calcular la posición para centrar el cuadro en la pantalla
    final_dialogue_rect = pygame.Rect((WIDTH - dialogue_width) // 2, (HEIGHT - dialogue_height) // 2, dialogue_width, dialogue_height)
    exit_button_rect = pygame.Rect((770, HEIGHT - 500, 100, 50))
    exit_button_text = font.render("Salir", True, GREY)

    # Bucle para mostrar la animación y el mensaje final
    running = True
    while running:
        # Limpiar la pantalla con el fondo
        window.blit(background_image, (0, 0))

        current_image = idle_images_right[frame_index]
        frame_index = (frame_index + 2) % len(idle_images_right)

        # Dibujar el personaje en el centro de la pantalla
        character_rect = current_image.get_rect(center=(WIDTH // 2, HEIGHT - 80))
        window.blit(current_image, character_rect)

        # Dibujar el cuadro de diálogo
        pygame.draw.rect(window, BROWN, final_dialogue_rect)  
        pygame.draw.rect(window, BLACK, final_dialogue_rect, 2)  

        # Dibujar cada parte del mensaje
        for i, line in enumerate(lines):
            line_surface = font.render(line, True, BLACK)
            window.blit(line_surface, (final_dialogue_rect.x + 10, final_dialogue_rect.y + 10 + i * 30))

        # Dibujar el botón de salir
        pygame.draw.rect(window, WHITE, exit_button_rect)  # Color del botón
        pygame.draw.rect(window, GREY, exit_button_rect, 2)  # Borde del botón
        help_text_rect = exit_button_text.get_rect(center=exit_button_rect.center)
        window.blit(exit_button_text, help_text_rect)  # Dibuja el texto centrado en el botón

        # Manejar eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if exit_button_rect.collidepoint(event.pos): 
                    running = False

        # Actualizar la pantalla
        pygame.display.flip()
        pygame.time.delay(150)

    pygame.quit()

def main_game():
    
    
    character_images_right, character_images_left = Character.load_images('pers', 1)
    idle_images_right, idle_images_left = Character.load_images('pers_idle', 1)
    character = Character(character_images_right, character_images_left, idle_images_right, idle_images_left, 4)

    # Niveles con preguntas y opciones
    levels = [

        {
            "question": "1. Imagina que estás trabajando en un proyecto grupal donde cada miembro aporta diferentes habilidades. A medida que avanzas en el proyecto, surge la siguiente pregunta: ¿Se logró un objetivo eficaz al combinar habilidades personales contrapropuestas?",
            "options": [
                {"options": "A. Sí, la combinación de habilidades permitió una mejor comprensión de los aspectos sociales y humanos del proyecto, lo que llevó a un enfoque más integral y empático. ", "points_humanas": 26, "points_exactas": 0},
                {"options": "B. Sí, al integrar diferentes perspectivas, logramos abordar los desafíos desde un punto de vista más colaborativo y comunicativo, lo que enriqueció el resultado final. ", "points_humanas": 20, "points_exactas": 0},
                {"options": "C. Sí, la diversidad de habilidades permitió una optimización de los recursos y una solución más eficiente desde un punto de vista lógico y estructurado.  ", "points_humanas": 0, "points_exactas": 22},
                {"options": "D. Sí, la integración de habilidades analíticas y técnicas mejoró la precisión en la toma de decisiones y la implementación de soluciones más concretas y medibles. ", "points_humanas": 0, "points_exactas": 32}
            ]
            
        },
        
        {
            "question": "2. Estas decidiendo  tu enfoque académico y profesional, considerando cómo tus intereses y habilidades actuales pueden influir en tu futuro. Esta decisión es crucial, ya que determinará en gran medida las áreas en las que te especializarás y el tipo de impacto que deseas tener en tu carrera.¿En un futuro, cómo enfocas tu carrera profesional?",
            "options": [
                {"options": "A. Me veo trabajando en áreas que promuevan el bienestar social, la educación, y la comunicación, utilizando mis habilidades para entender y mejorar las dinámicas humanas y sociales", "points_humanas": 24, "points_exactas": 0},
                {"options": "B. Planeo enfocarme en una carrera que me permita influir en la sociedad a través del liderazgo, la gestión de proyectos comunitarios, y la promoción de la cultura y el conocimiento.  ", "points_humanas": 17, "points_exactas": 0},
                {"options": "C. Me gustaría enfocarme en la tecnología y la ingeniería, donde pueda aplicar mi pasión por las ciencias y mi capacidad analítica para resolver problemas complejos. ", "points_humanas": 0, "points_exactas": 34},
                {"options": "D. Quiero construir una carrera en áreas técnicas como la biotecnología, la arquitectura, o la física, donde pueda utilizar mis habilidades matemáticas y científicas para innovar y crear soluciones tangibles.", "points_humanas": 0, "points_exactas": 25}
            ]
            
        },

        {
            "question": "3. En un proyecto grupal, cada persona asume un rol que puede influir en la dinámica y el éxito del equipo. ¿Cuál es tu rol ideal en un trabajo grupal?",
            "options": [
                {"options": "A. Aseguro que todos participen y colaboren efectivamente.", "points_humanas": 34, "points_exactas": 0},
                {"options": "B. Busco consenso y valoro las aportaciones de todos.", "points_humanas": 17, "points_exactas": 0},
                {"options": "C. Organizo tareas y mantengo el enfoque en los objetivos.", "points_humanas": 0, "points_exactas": 25},
                {"options": "D. Abordo desafíos mediante análisis y soluciones prácticas", "points_humanas": 0, "points_exactas": 24}
            ]
            
        },
        
        {
            "question": "4. Cuando comienzas una nueva actividad o proyecto, la forma en que se reparten los temas o tareas puede influir en el resultado final.¿Cuál es tu primera acción al momento de realizar una actividad? ",
            "options": [
                {"options": "A. Propongo que todos compartan sus ideas para decidir juntos cómo se repartirán los temas.", "points_humanas": 20, "points_exactas": 0},
                {"options": "B. Sugiero una discusión inicial para identificar los intereses de cada miembro antes de asignar temas.", "points_humanas": 25, "points_exactas": 0},
                {"options": "C. Organizo una lista de tareas y propongo que los temas se repartan según las habilidades de cada uno. ", "points_humanas": 0, "points_exactas": 20},
                {"options": "D. Divido los temas de manera lógica y equitativa, asegurándome de que cada uno reciba una parte que domine.", "points_humanas": 0, "points_exactas": 35}
            ]
            
        },

        {
            "question": "5. En un trabajo grupal, los conflictos pueden surgir. La forma en que los manejes afectará el ambiente y el éxito del proyecto.¿Cómo resolverías un conflicto en un trabajo grupal? ",
            "options": [
                {"options": "A. Iniciaría un diálogo abierto donde todos puedan expresar sus opiniones antes de llegar a un acuerdo conjunto.", "points_humanas": 30, "points_exactas": 0},
                {"options": "B. Actuaría como mediador, buscando un punto medio que sea aceptable para todos los involucrados.", "points_humanas": 21, "points_exactas": 0},
                {"options": "C. Analizaría los hechos y las evidencias para encontrar la solución más lógica y eficiente.", "points_humanas": 0, "points_exactas": 24},
                {"options": "D. Desglosaría el problema en partes más pequeñas, abordando cada una con un enfoque sistemático hasta resolver el conflicto.", "points_humanas": 0, "points_exactas": 25}
            ]
            
        },
        
        {
            "question": "6. Un nuevo descubrimiento científico ha sacudido el mundo, prometiendo cambiar tanto nuestra tecnología como nuestra comprensión del universo y de nosotros mismos.Ante un descubrimiento científico revolucionario, ¿qué te emociona más? ",
            "options": [
                {"options": "A. Me entusiasma cómo este avance podría profundizar nuestra comprensión de la condición humana y el mundo que nos rodea.", "points_humanas": 20, "points_exactas": 0},
                {"options": "B. Me motiva el impacto que este descubrimiento tendrá en la forma en que entendemos nuestras sociedades y culturas.", "points_humanas": 26, "points_exactas": 0},
                {"options": "C. Me emociona imaginar las nuevas tecnologías que podrían surgir a partir de este avance y sus aplicaciones prácticas.", "points_humanas": 0, "points_exactas": 34},
                {"options": "D. Estoy interesado en cómo este descubrimiento puede ser utilizado para resolver problemas reales y mejorar nuestras vidas diarias.", "points_humanas": 0, "points_exactas": 20}
            ]
            
        },
        
        {
            "question": "7. En una exposición, la manera en que te expresas puede influir en la claridad y el impacto de tu mensaje. ¿Cómo prefieres expresar tus ideas durante una exposición?",
            "options": [
                {"options": "A. Prefiero comunicar mis ideas de manera directa y sin rodeos, asegurando que el mensaje sea claro para todos.", "points_humanas": 18, "points_exactas": 0},
                {"options": "B. Me gusta involucrar a la audiencia mediante preguntas y discusiones para hacer la exposición más interactiva.", "points_humanas": 27, "points_exactas": 0},
                {"options": "C. trato de ser preciso y sigo un esquema claro para asegurar que todos los puntos se presenten.", "points_humanas": 0, "points_exactas": 22},
                {"options": "D. Prefiero proporcionar detalles y datos específicos, abordando cada punto con un enfoque basado en evidencias.", "points_humanas": 0, "points_exactas": 32}
            ]
            
        },
        
        {
            "question": "8. Los estudios sobre el cerebro sugieren que el desarrollo desigual de los hemisferios cerebrales puede influir en las habilidades y características cognitivas de una persona.¿Cuál hemisferio del cerebro crees que desarrollas más y cómo crees que esto influye en tus habilidades?",
            "options": [
                {"options": "A. Considero que mi hemisferio izquierdo está más desarrollado, lo que mejora mis habilidades en comunicación verbal y en la organización y estructuración de la información.", "points_humanas": 21, "points_exactas": 0},
                {"options": "B. Creo que desarrollo más mi hemisferio derecho, lo que potencia mi creatividad, imaginación y capacidad para pensar en términos visuales y abstractos.", "points_humanas": 24, "points_exactas": 0},
                {"options": "C. Creo que mi hemisferio derecho está más desarrollado, lo que mejora mi capacidad para la percepción espacial, alta facilidad de compresion y adacptación.", "points_humanas": 0, "points_exactas": 23},
                {"options": "D. Creo que desarrollo más mi hemisferio izquierdo, lo que me ayuda en tareas de análisis, razonamiento lógico y resolución de problemas estructurados.", "points_humanas": 0, "points_exactas": 32}
            ]
            
        },
        
        {
            "question": "9. La forma en que seguimos y analizamos los eventos globales y políticos puede reflejar nuestros intereses y enfoques en la comprensión del mundo y la influencia en la sociedad.¿Cómo prefieres seguir los eventos actuales y políticos en tu país y en el mundo?",
            "options": [
                {"options": "A. Me interesa estudiar los eventos internacionales y sus implicaciones, buscando entender su impacto global y regional.", "points_humanas": 32, "points_exactas": 0},
                {"options": "B. Prefiero concentrarme en las noticias políticas y sociales de mi país, analizando cómo afectan a mi comunidad y contexto.", "points_humanas": 23, "points_exactas": 0},
                {"options": "C. Me enfoco en recolectar y analizar datos sobre eventos globales para identificar patrones y tendencias relevantes.", "points_humanas": 0, "points_exactas": 21},
                {"options": "D. Me interesa en profundidad el análisis de políticas y sus proyecciones futuras, usando métodos estructurados para entender sus posibles efectos.", "points_humanas": 0, "points_exactas": 24}
            ]
            
        },
        
        {
            "question": "10. Brian Tracy enfatiza la importancia de establecer objetivos claros, gestionar el tiempo eficazmente y liderar con un enfoque estratégico para el éxito en todo. ¿Cuál es tu enfoque preferido para alcanzar objetivos y resolver desafíos en tu entorno diario?",
            "options": [
                {"options": "A.	Establezco metas claras y desarrollo un plan estratégico para alcanzarlas", "points_humanas": 26, "points_exactas": 0},
                {"options": "B. Me enfoco en la gestión eficiente del tiempo y priorizo tareas clave para maximizar la productividad.", "points_humanas": 23, "points_exactas": 0},
                {"options": "C. Implemento técnicas organizativas para asegurar que todos los pasos sean seguidos meticulosamente.", "points_humanas": 0, "points_exactas": 21},
                {"options": "D. Analizo datos y resultados para ajustar estrategias y optimizar continuamente el enfoque hacia los objetivos.", "points_humanas": 0, "points_exactas": 30}
            ]
            
        },
        
                {
            "question": "11. Cuando piensas en tu futuro profesional, puedes visualizarte en un campo que se ajuste a tus intereses y habilidades. Esto podría significar trabajar en áreas técnicas y analíticas, o en roles enfocados en la comprensión de las interacciones humanas y sociales, dependiendo de tus pasiones, habilidades y experiencias previas.",
            "options": [
                {"options": "A. Me veo trabajando como ingeniero de software, diseñando algoritmos complejos y desarrollando soluciones tecnológicas innovadoras. ", "points_humanas": 0, "points_exactas": 30},
                {"options": "B. Imagino mi futuro en el ámbito de la investigación matemática, resolviendo problemas teóricos y aplicando modelos matemáticos a diversas áreas. ", "points_humanas": 0, "points_exactas": 25},
                {"options": "C. Visualizo mi carrera como psicólogo clínico, ayudando a las personas a entender y superar sus desafíos emocionales y mentales. ", "points_humanas": 20, "points_exactas": 0},
                {"options": "D. Me imagino trabajando como sociólogo, investigando las dinámicas sociales y contribuyendo a políticas que mejoren la cohesión y bienestar comunitario. ", "points_humanas": 25, "points_exactas": 32}
            ]
            
        },
        
        {
            "question": "12. Al planear unas vacaciones, tus decisiones pueden estar influenciadas por una variedad de factores, desde la logística y la eficiencia hasta la cultura y las experiencias personales. La forma en que abordas esta tarea puede reflejar tu estilo de planificación y tus prioridades.",
            "options": [
                {"options": "A. Elijo un destino basándome en un análisis de costos .", "points_humanas": 24, "points_exactas": 0},
                {"options": "B. Planeo enfocarme en una carrera que me permita influir en la sociedad a través del liderazgo, la gestión de proyectos comunitarios, y la promoción de la cultura y el conocimiento.  ", "points_humanas": 17, "points_exactas": 0},
                {"options": "C. Mi objetivo es desarrollarme en campos relacionados con la tecnología y la ingeniería, donde pueda aplicar mi pasión por las ciencias y mi razonamiento analitico. ", "points_humanas": 0, "points_exactas": 34},
                {"options": "D. Quiero construir una carrera en áreas técnicas como la biotecnología, la arquitectura, o la física, donde pueda utilizar mis habilidades matemáticas y científicas para innovar y crear soluciones tangibles.", "points_humanas": 0, "points_exactas": 25}
            ]
            
        },
        
        {
            "question": "13. Tomar decisiones importantes puede implicar diferentes estrategias, desde análisis de datos y métodos estructurados hasta la consideración de aspectos emocionales y sociales. La forma en que eliges proceder refleja tus prioridades y estilo de toma de decisiones.",
            "options": [
                {"options": "A. Recojo y analizo datos ", "points_humanas": 0, "points_exactas": 28},
                {"options": "B. Implemento un enfoque sistemático y estructurado.", "points_humanas": 0, "points_exactas": 22},
                {"options": "C. Consulto con personas cercanas y expertos para entender diferentes perspectivas y considerar cómo la decisión afectará a los involucrados. ", "points_humanas": 30, "points_exactas": 0},
                {"options": "D. Reflexiono sobre mis experiencias pasadas y emociones actúa.", "points_humanas":20, "points_exactas": 0}
            ]
            
        },
        
        {
            "question": "14. Cada persona tiene diferentes preferencias sobre el tipo de trabajo que le gustaría hacer en el futuro. Algunas personas prefieren trabajos que les permitan resolver problemas de manera lógica y técnica, mientras otras buscan roles de interacción y comprensión de las personas y sus comportamientos.",
            "options": [
                {"options": "A. Utilices tus habilidades para resolver problemas complejos y desarrollar soluciones prácticas.", "points_humanas": 0, "points_exactas": 27},
                {"options": "B. Trabajes en un entorno que requiera precisión y análisis detallado para alcanzar objetivos específicos.", "points_humanas": 0, "points_exactas": 23},
                {"options": "C. Te involucres en actividades que te permitan explorar ideas y comprender cómo interactúan las personas en diferentes contextos.", "points_humanas":30, "points_exactas": 0},
                {"options": "D. D.	Colabores con otros para entender y mejorar aspectos de la vida cotidiana y las dinámicas sociales.", "points_humanas": 20, "points_exactas": 0}
            ]
            
        },
        
        {
            "question": "15. Cuando comienzas un proyecto nuevo, diferentes personas abordan la tarea de distintas maneras. Algunos prefieren hacer una planificación minuciosa y tener una estructura clara desde el principio, otras son flexibles según avanza el proyecto, basándose en su intuición y experiencia.",
            "options": [
                {"options": "A. Prefiero crear un plan detallado con pasos específicos y mantenerme organizado para alcanzar los objetivos.", "points_humanas": 0, "points_exactas": 32},
                {"options": "B. Me gusta definir una estructura inicial, pero estoy dispuesto a ajustar el enfoque según sea necesario mientras avanzo.", "points_humanas": 0, "points_exactas": 21},
                {"options": "C. Tiende a confiar en mi intuición y hacer ajustes sobre la marcha, adaptándome a nuevas situaciones a medida que surgen.", "points_humanas": 25, "points_exactas": 0},
                {"options": "D. Comienzo con una idea general y me enfoco en adaptarme y resolver problemas a medida que se presentan durante el proyecto.", "points_humanas": 22, "points_exactas": 0}
            ]
            
        },
        
        {
            "question": "16. Se ha demostrado que los intereses personales y las habilidades influyen fuertemente en las decisiones académicas.¿Qué áreas de conocimiento te resultan más atractivas en tu día a día académico? ",
            "options": [
                {"options": "A. Resolver problemas que involucran análisis numérico o matemático .", "points_humanas": 0, "points_exactas": 28},
                {"options": "B. Diseñar o simular fenómenos utilizando herramientas científicas o tecnológicas.", "points_humanas": 0, "points_exactas": 12},
                {"options": "C. Comprender mejor las dinámicas sociales y el comportamiento humano .", "points_humanas": 25, "points_exactas": 0},
                {"options": "D. Investigar temas relacionados con la cultura, historia o interacción social .", "points_humanas": 35, "points_exactas": 0}
            ]
            
        },
        
        {
            "question": "17. El proceso de toma de decisiones implica elegir actividades que contribuyan a tu desarrollo profesional.¿Qué tipo de actividades te ayudan más a sentir que estás construyendo tu futuro profesional?",
            "options": [
                {"options": "A. Participar en discusiones o proyectos que aborden problemas sociales y humanos.", "points_humanas": 34, "points_exactas": 0},
                {"options": "B. Investigar y analizar cómo las sociedades evolucionan y enfrentan desafíos.", "points_humanas": 16, "points_exactas": 0},
                {"options": "C. Participar en experimentos o proyectos que involucren el uso de herramientas científicas.", "points_humanas": 0, "points_exactas": 32},
                {"options": "D. Desarrollar habilidades analíticas mediante el uso de matemáticas avanzadas.", "points_humanas": 0, "points_exactas": 18}
            ]
            
        },
        
        {
            "question": "18. Las experiencias previas juegan un papel importante en la decisión de qué énfasis elegir.¿Qué tipo de experiencia previa te ha motivado más en tu decisión sobre el énfasis?",
            "options": [
                {"options": "A. Involucrarme en actividades relacionadas con el estudio de la cultura, sociedad o historia.", "points_humanas": 35, "points_exactas": 0},
                {"options": "B. Haber trabajado en proyectos comunitarios o sociales enfocados en el bienestar humano.", "points_humanas": 15, "points_exactas": 0},
                {"options": "C. Haber participado en proyectos o competencias científicas o tecnológicas.", "points_humanas": 0, "points_exactas": 33},
                {"options": "D. Realizar trabajos en matemáticas o ciencias donde resolví problemas cuantitativos.", "points_humanas": 0, "points_exactas": 17}
            ]
            

        },         
    
    ]

    # Acumuladores de puntos para Humanas y Exactas
    total_points_humanas = 0
    total_points_exactas = 0
    current_level = 0
    selected_option = None
    dialogue = Dialogue(levels[current_level]['question'], levels[current_level]['options'], (WIDTH // 2 - DIALOG_WIDTH // 2, 5))

    # Variables de control del juego
    running = True
    show_dialog = False
    dialog_triggered = False
    level_complete = False

    # Bucle principal del juego
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if show_dialog:
                    mouse_pos = pygame.mouse.get_pos()
                    for i, rect in enumerate(dialogue.draw(window, selected_option)[1]):
                        if rect.collidepoint(mouse_pos):
                            selected_option = i
                            total_points_humanas += levels[current_level]['options'][selected_option]['points_humanas']
                            total_points_exactas += levels[current_level]['options'][selected_option]['points_exactas']
                            level_complete = True
                            show_dialog = True

        # Actualización y dibujo de la pantalla
        keys = pygame.key.get_pressed()
        character.moving = False
        window.blit(background_image, (0, 0))

        if show_dialog:
            dialogue.draw(window, selected_option)

        character.move(keys)
        character.draw(window)

        # Activar el cuadro de dialogo
        if character.rect.centerx >= WIDTH // 2 and not dialog_triggered:
            show_dialog = True
            dialog_triggered = True             

        # Lógica para avanzar de nivel
        if level_complete and character.rect.left > WIDTH:
            current_level += 1
            if current_level < len(levels):
                # Cargar el siguiente nivel y el personaje correspondiente
                character_images_right, character_images_left = Character.load_images('pers', current_level + 1)
                idle_images_right, idle_images_left = Character.load_images('pers_idle', current_level + 1)
                character = Character(character_images_right, character_images_left, idle_images_right, idle_images_left, 4)
                dialogue = Dialogue(levels[current_level]['question'], levels[current_level]['options'], (WIDTH // 2 - DIALOG_WIDTH // 2, 5))
                selected_option = None
                level_complete = False
                dialog_triggered = False
                show_dialog = False
            else:
                final_level(window, total_points_humanas, total_points_exactas)
                running = False

        # Lógica para retroceder de nivel
        elif character.rect.right < 0:
            if current_level > 0:
                current_level -= 1
                # Cargar el nivel anterior y el personaje correspondiente
                character_images_right, character_images_left = Character.load_images('pers', current_level + 1)
                idle_images_right, idle_images_left = Character.load_images('pers_idle', current_level + 1)
                character = Character(character_images_right, character_images_left, idle_images_right, idle_images_left, 4)
                character.rect.x = WIDTH - character.rect.width  # Mover al borde derecho
                character.x = float(character.rect.x)
                dialogue = Dialogue(levels[current_level]['question'], levels[current_level]['options'], (WIDTH // 2 - DIALOG_WIDTH // 2, 5))
                selected_option = None
                level_complete = False
                dialog_triggered = False
                show_dialog = False

        # Actualización de la pantalla y control de FPS
        pygame.display.flip()
        pygame.time.Clock().tick(60)

    pygame.quit()
    sys.exit()





def main():
    button_rect, help_rect = draw_start_screen()
    game_started = False 
    show_dialog = False 
    selected_option = None
    show_help = False

    while not game_started:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if button_rect.collidepoint(mouse_pos):
                    game_started = True  # Cambia a True para salir del bucle
                elif help_rect.collidepoint(mouse_pos):
                    show_help = True 
                # Si hay un diálogo de selección
                        # Mostrar pantalla de ayuda si está activada
                if show_help:
                    show_help_screen(window)
                    show_help = False 
                    draw_start_screen()  # Redibuja la pantalla inicial después de mostrar ayuda
                if show_dialog:
                    for i, rect in enumerate(Dialogue.draw(window, selected_option)[1]):
                        if rect.collidepoint(mouse_pos):
                            selected_option = i
                            # Obtener el énfasis
                            enfasis = Dialogue.handle_selection(selected_option)
                            print(f"Énfasis seleccionado: {enfasis}")  # Mostrar el énfasis
                            level_complete = True
                            show_dialog = False

    main_game()

if __name__ == "__main__":
    main()

