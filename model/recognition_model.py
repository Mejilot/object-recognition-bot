import io
import torch
from torchvision.io.image import read_image
from torchvision.utils import draw_bounding_boxes
from torchvision.transforms.functional import to_pil_image
from torchvision.models.detection import fasterrcnn_resnet50_fpn, FasterRCNN_ResNet50_FPN_Weights
from torchvision.models import ResNet50_Weights
from torchvision import transforms
from PIL import Image


class RecognitionModel:
    def __init__(self):
        # стандартные веса для модели fastercnn with resnet backbone
        weights = FasterRCNN_ResNet50_FPN_Weights.DEFAULT
        # вычисление по возможности будет производиться на видеокарте
        device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu")
        # детектор объектов
        self.model = fasterrcnn_resnet50_fpn(weights=weights, num_classes=len(
            weights.meta["categories"]), weights_backbone=ResNet50_Weights.DEFAULT).to(device)
        # включаю режим распознавания - evaluation
        self.model.eval()
        self.preprocess = weights.transforms()
        # в будущем можно поставить это как параметр
        self.threshold = 0.75
        self.categories = weights.meta["categories"]

    def process_image(self, img_bytes):
        # битовое изображение перевожу в два тензора со значениями [0-255], [0-1]
        img_tensor_i, img_tensor_f = self.byte_image_to_tensors(img_bytes)
        # добавляю alpha канал чтобы все тензора изображения имели одинаковую размерность
        prep_img = self.preprocess(img_tensor_f).unsqueeze_(0)
        prediction = self.model(prep_img)[0]
        # отбираю предсказания с определенным % успеха, как параметр в этой модели не работает
        prediction['boxes'] = prediction['boxes'][prediction['scores']
                                                  > self.threshold]
        prediction['labels'] = prediction['labels'][prediction['scores']
                                                    > self.threshold]
        prediction['scores'] = prediction['scores'][prediction['scores']
                                                    > self.threshold]
        # создаю ярлыки для объектов на изображении
        labels = ["{}: {:.2f}%".format(self.categories[prediction["labels"][i]],
                                       round(float(prediction['scores'][i]) * 100, 0))
                  for i in range(len(prediction["labels"]))]
        # рисуем-с boxes
        box = draw_bounding_boxes(image=img_tensor_i, boxes=prediction["boxes"], labels=labels,
                                  colors=(0, 255, 42), width=2,
                                  font_size=17, font='Arial')
        # преобразование тензора обратно в байтовое изображение
        im = to_pil_image(box.detach())
        img_byte_arr = io.BytesIO()
        im.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        # список информации об объектах по указанному формату
        pred_list = ["{}. {} - {} - {}%".format(i + 1,
                                                self.categories[prediction["labels"][i]],
                                                prediction['boxes'][i].tolist(),
                                                round(float(prediction['scores'][i]) * 100, 0))
                     for i in range(len(prediction["labels"]))]
        return (img_byte_arr, '\n'.join(pred_list))
    # битовое изображение в тензоры

    def byte_image_to_tensors(self, img_bytes):
        raw_img = Image.open(io.BytesIO(img_bytes))
        img = raw_img.convert('RGB')
        img_tensor_i = transforms.Compose([
            transforms.PILToTensor()
        ])(img)
        img_tensor_f = transforms.ToTensor()(img)
        return img_tensor_i, img_tensor_f
