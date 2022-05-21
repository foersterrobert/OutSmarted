import torch.nn as nn
import torch.nn.functional as F

class Model(nn.Module):
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
            nn.Flatten(),
            nn.Linear(16704, 2, bias=False),
            nn.Sigmoid()
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