from torchvision.io.image import read_image
from torchvision.utils import draw_bounding_boxes
from torchvision.transforms.functional import to_pil_image
from torchvision.models.detection import fasterrcnn_resnet50_fpn, FasterRCNN_ResNet50_FPN_Weights
from torchvision.models import ResNet50_Weights
import torch
from PIL import Image
from torchvision import transforms
import io

class RecognitionModel:
    def __init__(self):
        self.weights = FasterRCNN_ResNet50_FPN_Weights.DEFAULT
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = fasterrcnn_resnet50_fpn(weights=self.weights, num_classes=len(self.weights.meta["categories"]), weights_backbone=ResNet50_Weights.DEFAULT).to(self.device)
        self.model.eval()
        self.preprocess = self.weights.transforms()
    def procces_image(self, img_bytes):
        raw_img = Image.open(io.BytesIO(img_bytes))
        img = raw_img.convert('RGB')
        img_tensor_i = transforms.Compose([
            transforms.PILToTensor()
        ])(img)
        img_tensor_f = transforms.ToTensor()(img)
        prep_img = self.preprocess(img_tensor_f).unsqueeze_(0)
        prediction = self.model(prep_img)[0]
        threshold = 0.75
        prediction['boxes'] = prediction['boxes'][prediction['scores'] > threshold]
        prediction['labels'] = prediction['labels'][prediction['scores'] > threshold]
        prediction['scores'] = prediction['scores'][prediction['scores'] > threshold]
        labels = ["{}: {:.2f}%".format(self.weights.meta["categories"][prediction["labels"][i]], round(float(prediction['scores'][i]) * 100, 0)) for i in range(len(prediction["labels"]))]
        box = draw_bounding_boxes(image = img_tensor_i, boxes=prediction["boxes"],
                                labels=labels,
                                colors=(0, 255, 42),
                                width=2, 
                                font_size=17,
                                font='Arial')

        im = to_pil_image(box.detach())
        img_byte_arr = io.BytesIO()
        im.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        pred_list = ["{}. {} - {} - {:.2f}%".format(i + 1, self.weights.meta["categories"][prediction["labels"][i]], prediction['boxes'][i].tolist(), round(float(prediction['scores'][i]) * 100, 0)) for i in range(len(prediction["labels"]))]
        return (img_byte_arr, '\n'.join(pred_list))