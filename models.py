import torch
import torch.nn as nn

class ResidualBlock(nn.Module):
    def __init__(self, in_channels, out_channels):
        super().__init__()
        self.conv1 = nn.Conv2d(in_channels, out_channels, 3, padding=1)
        self.bn1 = nn.BatchNorm2d(out_channels)
        self.relu = nn.ReLU(inplace=True)
        self.conv2 = nn.Conv2d(out_channels, out_channels, 3, padding=1)
        self.bn2 = nn.BatchNorm2d(out_channels)
        
        self.shortcut = nn.Sequential()
        if in_channels != out_channels:
            self.shortcut = nn.Sequential(
                nn.Conv2d(in_channels, out_channels, 1, bias=False),
                nn.BatchNorm2d(out_channels)
            )

    def forward(self, x):
        residual = self.shortcut(x)
        out = self.relu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))
        return self.relu(out + residual)

class AttentionGate(nn.Module):
    def __init__(self, F_g, F_l, F_int):
        super().__init__()
        self.W_g = nn.Sequential(
            nn.Conv2d(F_g, F_int, kernel_size=1, stride=1, padding=0, bias=True),
            nn.BatchNorm2d(F_int)
        )
        self.W_x = nn.Sequential(
            nn.Conv2d(F_l, F_int, kernel_size=1, stride=1, padding=0, bias=True),
            nn.BatchNorm2d(F_int)
        )
        self.psi = nn.Sequential(
            nn.Conv2d(F_int, 1, kernel_size=1, stride=1, padding=0, bias=True),
            nn.BatchNorm2d(1),
            nn.Sigmoid()
        )
        self.relu = nn.ReLU(inplace=True)

    def forward(self, g, x):
        g1 = self.W_g(g)
        x1 = self.W_x(x)
        psi = self.relu(g1 + x1)
        psi = self.psi(psi)
        return x * psi

class StegoEncoder(nn.Module):
    def __init__(self, in_channels=4, out_channels=3):
        super().__init__()
        self.enc1 = ResidualBlock(in_channels, 64)
        self.pool1 = nn.Conv2d(64, 64, kernel_size=3, stride=2, padding=1)
        self.enc2 = ResidualBlock(64, 128)
        self.pool2 = nn.Conv2d(128, 128, kernel_size=3, stride=2, padding=1)
        self.enc3 = ResidualBlock(128, 256)
        
        self.up2 = nn.ConvTranspose2d(256, 128, kernel_size=2, stride=2)
        self.att2 = AttentionGate(F_g=128, F_l=128, F_int=64)
        self.dec2 = ResidualBlock(256, 128)
        
        self.up1 = nn.ConvTranspose2d(128, 64, kernel_size=2, stride=2)
        self.att1 = AttentionGate(F_g=64, F_l=64, F_int=32)
        self.dec1 = ResidualBlock(128, 64)
        
        self.out_conv = nn.Conv2d(64, out_channels, kernel_size=1)

    def forward(self, cover, secret):
        x = torch.cat([cover, secret], dim=1)
        e1 = self.enc1(x)
        e2 = self.enc2(self.pool1(e1))
        e3 = self.enc3(self.pool2(e2))
        
        d2 = self.up2(e3)
        a2 = self.att2(g=d2, x=e2)
        d2 = torch.cat((a2, d2), dim=1)
        d2 = self.dec2(d2)
        
        d1 = self.up1(d2)
        a1 = self.att1(g=d1, x=e1)
        d1 = torch.cat((a1, d1), dim=1)
        d1 = self.dec1(d1)
        
        out = self.out_conv(d1)
        return torch.tanh(out)

class StegoDecoder(nn.Module):
    def __init__(self, in_channels=3, out_channels=1):
        super().__init__()
        self.conv1 = ResidualBlock(in_channels, 64)
        self.conv2 = ResidualBlock(64, 128)
        self.conv3 = ResidualBlock(128, 256)
        self.conv4 = ResidualBlock(256, 128)
        self.conv5 = ResidualBlock(128, 64)
        self.out_conv = nn.Conv2d(64, out_channels, kernel_size=1)

    def forward(self, stego):
        x = self.conv1(stego)
        x = self.conv2(x)
        x = self.conv3(x)
        x = self.conv4(x)
        x = self.conv5(x)
        out = self.out_conv(x)
        return torch.tanh(out)
