import cv2
import numpy as np
import onnxruntime as ort
import yaml
from PIL import Image, ImageDraw, ImageFont


class YOLOv8:
    """YOLOv8 目标检测模型类，用于处理推理和可视化。"""

    def __init__(self, onnx_model, confidence_thres, iou_thres):
        """
        初始化 YOLOv8 类的实例。

        参数：
            onnx_model: ONNX 模型的路径。
            confidence_thres: 用于过滤检测结果的置信度阈值。
            iou_thres: 非极大值抑制的 IoU（交并比）阈值。
        """
        self.onnx_model = onnx_model
        self.confidence_thres = confidence_thres
        self.iou_thres = iou_thres

        # 从数据集加载类别名称
        self.classes = self.load_yaml("tea.yaml")["names"]

        # 为每个类别生成颜色调色板
        self.color_palette = np.random.uniform(0, 255, size=(len(self.classes), 3))

        # 加载中文字体
        self.font = ImageFont.truetype("simsun.ttc", 100)

    def load_yaml(self, yaml_file):
        """
        加载 YAML 文件并返回内容。

        参数：
            yaml_file: YAML 文件的路径。

        返回：
            dict: YAML 文件的内容。
        """
        with open(yaml_file, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)


    def draw_detections(self, img, box, score, class_id):
        """
        根据检测到的目标在输入图像上绘制边界框和标签。

        参数：
            img: 要绘制检测结果的输入图像。
            box: 检测到的边界框。
            score: 相应的检测置信度分数。
            class_id: 检测到的目标的类别 ID。

        返回：
            None
        """
        x1, y1, w, h = box
        color = tuple(map(int, self.color_palette[class_id]))
        label = f"{self.classes[class_id]}: {score:.2f}"

        height, width, _ = img.shape
        scale_factor = width / 640

        # 计算调整后的目标框粗细
        box_thickness = int(3 * scale_factor)

        font_size = int(30 * scale_factor)  # 初始字体大小为 30，可以根据需要调整
        self.font = ImageFont.truetype(self.font.path, font_size)  # 更新字体大小
        font = self.font

        # 使用 PIL 绘制中文标签
        img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(img_pil)
        draw.rectangle([x1, y1, x1 + w, y1 + h], outline=color, width=box_thickness)

        text_bbox = draw.textbbox((x1, y1 - box_thickness), label, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        draw.rectangle([x1, y1 - text_height, x1 + text_width, y1], fill=color)
        draw.text((x1, y1 - text_height), label, font=font, fill=(0, 0, 0))
        img = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

        return img



    def preprocess(self, img):
        """
        在执行推理之前预处理输入图像。

        返回：
            image_data: 预处理后的图像数据，准备进行推理。
        """
        self.img = img
        self.img_height, self.img_width = self.img.shape[:2]
        img = cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (self.input_width, self.input_height))
        image_data = np.array(img) / 255.0
        image_data = np.transpose(image_data, (2, 0, 1))
        image_data = np.expand_dims(image_data, axis=0).astype(np.float32)
        return image_data

    def postprocess(self, input_image, output):
        """
        对模型输出进行后处理，以提取边界框、置信度分数和类别 ID。

        参数：
            input_image (numpy.ndarray): 输入图像。
            output (numpy.ndarray): 模型的输出。

        返回：
            numpy.ndarray: 带有绘制检测结果的输入图像。
        """
        outputs = np.transpose(np.squeeze(output[0]))
        rows = outputs.shape[0]
        boxes = []
        scores = []
        class_ids = []
        x_factor = self.img_width / self.input_width
        y_factor = self.img_height / self.input_height
        for i in range(rows):
            classes_scores = outputs[i][4:]
            max_score = np.amax(classes_scores)
            if max_score >= self.confidence_thres:
                class_id = np.argmax(classes_scores)
                x, y, w, h = outputs[i][0], outputs[i][1], outputs[i][2], outputs[i][3]
                left = int((x - w / 2) * x_factor)
                top = int((y - h / 2) * y_factor)
                width = int(w * x_factor)
                height = int(h * y_factor)
                class_ids.append(class_id)
                scores.append(max_score)
                boxes.append([left, top, width, height])
        indices = cv2.dnn.NMSBoxes(boxes, scores, self.confidence_thres, self.iou_thres)
        detected_classes = []
        class_counts = {}
        for i in indices:
            box = boxes[i]
            score = scores[i]
            class_id = class_ids[i]
            input_image = self.draw_detections(input_image, box, score, class_id)
            detected_class = self.classes[class_id]
            detected_classes.append(detected_class)
            if detected_class in class_counts:
                class_counts[detected_class] += 1
            else:
                class_counts[detected_class] = 1
        return input_image, detected_classes, class_counts

    def run_inference(self, image):
        """
        使用 ONNX 模型执行推理，并返回带有绘制检测结果的输出图像。

        返回：
            output_img: 带有绘制检测结果的输出图像。
        """
        session = ort.InferenceSession(self.onnx_model, providers=["CUDAExecutionProvider", "CPUExecutionProvider"])
        model_inputs = session.get_inputs()
        input_shape = model_inputs[0].shape
        self.input_width = input_shape[2]
        self.input_height = input_shape[3]
        img_data = self.preprocess(image)
        outputs = session.run(None, {model_inputs[0].name: img_data})
        return self.postprocess(self.img, outputs)
