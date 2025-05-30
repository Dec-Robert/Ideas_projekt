import io
import base64
from PIL import Image
import torch
from torchvision import transforms
from torchcam.methods import GradCAM, GradCAMpp
from torchcam.utils import overlay_mask
from torchvision.transforms.functional import to_pil_image
from model_def import CNNModel
import torch_directml

device = torch_directml.device()

# Wczytanie modelu
model = CNNModel().to(device)
model.load_state_dict(torch.load("cnn.pth", map_location=device))
model.eval()

transform = transforms.Compose([
    transforms.Resize((128, 128)),
    transforms.ToTensor(),
])

def predict_image(image_bytes: bytes, method: str = "gradcam"):
    pil_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    input_tensor = transform(pil_image).unsqueeze(0).to(device)

    if method == "gradcam++":
        cam_extractor = GradCAMpp(model, target_layer="conv3")
    else:
        cam_extractor = GradCAM(model, target_layer="conv3")

    output = model(input_tensor)
    pred_class = torch.argmax(output, dim=1).item()

    activation_map = cam_extractor(pred_class, output)[0].cpu()

    cam_result = overlay_mask(
        to_pil_image(transform(pil_image)),
        to_pil_image(activation_map, mode='F'),
        alpha=0.5
    )

    buffered = io.BytesIO()
    cam_result.save(buffered, format="PNG")
    cam_b64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

    return {
        "prediction": ["Negative", "Positive"][pred_class],
        "cam_image": f"data:image/png;base64,{cam_b64}"
    }