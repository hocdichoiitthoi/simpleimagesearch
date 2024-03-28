import torch
import torch.nn as nn
import torch.hub

model = torch.hub.load("pytorch/vision:v0.10.0", "vgg16", pretrained=True)

for param in model.parameters():
    param.requires_grad = False

class CustomModel(nn.Module):
    def __init__(self, base_model, output_layer):
        super(CustomModel, self).__init__()
        self.base_model = base_model
        self.output_layer = output_layer

    def forward(self, x):
        x = self.base_model(x)
        x = x.view(-1)
        x = self.output_layer(x)
        return x

output_layer = model.classifier[0]


custom_model = CustomModel(model.features, output_layer)
traced_custom_model = torch.jit.trace(custom_model, torch.randn(1, 3, 224, 224).to("cpu"))

torch.jit.save(traced_custom_model, r"D:\\image-search-engine\\server\\model_repository\\vgg16\\1\\model.pt")
