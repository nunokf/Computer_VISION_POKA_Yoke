class FrameProcessor:
    def __init__(self):
        # Inicializar todas as variáveis de estado
        self.gate_start = 0
        self.start_frames = []
        self.gate_end = 0
        self.end_frames = []
        self.end_frame_numbers = []  # Guarda o número do frame onde `end` ocorreu
        self.duration = []  # Duração de cada operação `end`
        self.count_poke = 0
        self.hits_poke = 0
        self.poke_prev = 0
        self.count_pen = 0
        self.hits_pen = 0
        self.pen_prev = 0
        self.total_hits = 0
        self.percentage_hits = 0
        self.success_count = 0  # Contador de sucessos
        self.total_experiments = 0  # Contador de ensaios
        self.current_color = "blue"  # Cor padrão
        self.previous_labels = {}  # Guarda os valores das fases anteriores

    def update_state(self, labels, frame_number):
        # Obter cores e atualizar estado com base em cada função
        color_start, self.gate_start = start(labels, self.gate_start, self.start_frames, frame_number)
        color_end, self.gate_end = end(labels, self.gate_end, self.end_frames, self.duration, self.start_frames,
                                       frame_number)
        color_poke, self.count_poke, self.hits_poke, self.poke_prev = poke(labels, self.count_poke, self.hits_poke,
                                                                           self.poke_prev)
        color_pen, self.count_pen, self.hits_pen, self.pen_prev = pen(labels, self.count_pen, self.hits_pen,
                                                                      self.pen_prev)
        self.total_hits, self.percentage_hits = metrics(self.total_hits, self.percentage_hits, labels,
                                                        self.start_frames)

        # Verificar mudanças nos rótulos e definir a cor atual
        color_changed = self.compare_labels(labels)
        if color_changed:
            self.current_color = "yellow"
        else:
            self.current_color = "blue"

        # Atualizar o contador de sucessos e total de experimentos
        if labels.get('poke', 0) == 2 and labels.get('pen', 0) == 2:
            self.success_count += 1
        self.total_experiments += 1

        # Armazenar rótulos atuais para comparação no próximo frame
        self.previous_labels = labels.copy()

    def compare_labels(self, labels):
        color_changed = False

        # Comparar fases específicas
        if 'start' in labels and 'start' in self.previous_labels:
            if labels['start'] != self.previous_labels['start']:
                color_changed = True
        if 'end' in labels and 'end' in self.previous_labels:
            if labels['end'] != self.previous_labels['end']:
                color_changed = True
        if 'poke' in labels and labels['poke'] != self.previous_labels.get('poke', 0):
            color_changed = True
        if 'pen' in labels and labels['pen'] != self.previous_labels.get('pen', 0):
            color_changed = True

        return color_changed

    def process_frame(self, image_path, detections, output_path, labels, frame_number, font_size=50):
        # Atualizar estado antes de processar o frame
        self.update_state(labels, frame_number)

        # Chamar a função de anotação
        annotate_image_with_boxes_and_labels(image_path, detections, output_path, labels, frame_number, font_size, self)


from PIL import Image, ImageDraw, ImageFont


def annotate_image_with_boxes_and_labels(image_path, detections, output_path, labels, frame_number, font_size=50,
                                         processor=None):
    # Carregar a imagem
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)

    # Definir a cor padrão para caixas e texto
    box_color = processor.current_color if processor else "blue"
    text_color = "yellow"  # Cor do texto

    # Desenhar as caixas de detecção
    for detection in detections:
        class_id, x_center, y_center, box_width, box_height = detection
        x_center *= image.width
        y_center *= image.height
        box_width *= image.width
        box_height *= image.height
        x_min = int(x_center - box_width / 2)
        y_min = int(y_center - box_height / 2)
        x_max = int(x_center + box_width / 2)
        y_max = int(y_center + box_height / 2)
        draw.rectangle([x_min, y_min, x_max, y_max], outline=box_color, width=2)

    if processor:
        # Configurar a fonte
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Supplemental/AppleMyungjo.ttf", size=font_size)
        except IOError:
            font = ImageFont.load_default()

        # Definir a posição e tamanho da caixa fixa
        box_x = 100
        box_y = 100
        box_width = 700
        box_height = 500

        # Desenhar a caixa de tamanho fixo
        draw.rectangle([box_x, box_y, box_x + box_width, box_y + box_height], outline=box_color, width=5)

        # Desenhar os rótulos e seus valores dentro da caixa
        label_y = box_y + 10
        phase_values = {
            "Start": labels.get('start', 0),
            "Poke": labels.get('poke', 0),
            "Pen": labels.get('pen', 0),
            "End": labels.get('end', 0)
        }

        for label, value in phase_values.items():
            text = f"{label}: {value}"
            draw.text((box_x + 10, label_y), text, font=font, fill="black")
            label_y += font_size + 5

        # Calcular e desenhar a duração média das operações e a duração atual
        if processor.end_frames and processor.start_frames:
            avg_duration = sum([end - start for end, start in zip(processor.end_frames, processor.start_frames)]) / len(
                processor.end_frames)
            current_duration = processor.duration[-1] if processor.duration else 0
        else:
            avg_duration = 0
            current_duration = 0

        # convert to s
        avg_duration = avg_duration * 0.167
        current_duration = current_duration * 0.167
        avg_duration_text = f"Avg Duration: {avg_duration:.2f} s"
        current_duration_text = f"Current Duration: {current_duration:.2f} s"
        success_ratio_text = f"Success Ratio: {(processor.success_count / processor.total_experiments * 100) if processor.total_experiments > 0 else 0:.0f}%"

        draw.text((box_x + 10, label_y), avg_duration_text, font=font, fill="black")
        label_y += font_size + 5
        draw.text((box_x + 10, label_y), current_duration_text, font=font, fill="black")
        label_y += font_size + 5
        draw.text((box_x + 10, label_y), success_ratio_text, font=font, fill="black")
        label_y += font_size + 5

    # Salvar a imagem anotada
    image.save(output_path)