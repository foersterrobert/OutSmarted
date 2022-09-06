import torch.nn as nn
import torch.nn.functional as F
from torchvision.transforms.functional import to_tensor
import torch

@torch.no_grad()
def detectGame(image, round_vals=True):
    imageT = to_tensor(image).reshape(1, 1, 168, 168)
    out = torch.exp(classificationModel(imageT))
    game = out.argmax(1).item() + 1
    vals = out.squeeze().detach().numpy().tolist()
    if round_vals:
        vals = [round(val, 4) for val in vals]
    return game, vals
    
class ClassificationModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.seq = nn.Sequential(
            self._block(1, 32, 3),
            self._block(32, 48, 3, 2),
            self._block(48, 64, 3),
            self._block(64, 80, 3),
            self._block(80, 96, 3, 2),
            self._block(96, 112, 3),
            self._block(112, 128, 3),
            self._block(128, 144, 3, 2),
            self._block(144, 154, 3),
            self._block(154, 116, 3),
            Flatten(),
            nn.Linear(16704, 2, bias=False),
            nn.BatchNorm1d(2), 
        ) 

    def _block(self, input_dim, output_dim, kernel_size, stride=1):
        return nn.Sequential(
            nn.Conv2d(input_dim, output_dim, kernel_size, stride, bias=False),
            nn.BatchNorm2d(output_dim),
            nn.ReLU()
        )

    def forward(self, x):
        x = self.seq(x)
        return F.log_softmax(x, dim=1)

class Flatten(nn.Module):
    def forward(self, x):
        return torch.flatten(x.permute(0, 2, 3, 1), 1)

# classification model
classificationModel = ClassificationModel()
classificationModel.load_state_dict(torch.load('app/Classification/classificaton.pth', map_location='cpu'))
classificationModel.eval()
