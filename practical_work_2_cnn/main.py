import argparse
from math import log10

import torch
import torch.nn as nn
import torch.optim as optim
from model import Net
from torch.utils.data import DataLoader

from data import get_test_set, get_training_set

# Training settings
parser = argparse.ArgumentParser(description="PyTorch Super Res Example")
parser.add_argument(
    "--upscale_factor", type=int, required=True, help="super resolution upscale factor"
)
parser.add_argument("--batch_size", type=int, default=64, help="training batch size")
parser.add_argument("--test_batch_size", type=int, default=10, help="testing batch size")
parser.add_argument(
    "--nb_epochs", type=int, default=2, help="number of epochs to train for"
)
parser.add_argument(
    "--lr", type=float, default=0.01, help="Learning Rate. Default=0.01"
)
parser.add_argument("--cuda", action="store_true", help="use cuda?")
parser.add_argument(
    "--mps", action="store_true", default=False, help="enables macOS GPU training"
)
parser.add_argument(
    "--threads", type=int, default=4, help="number of threads for data loader to use"
)
parser.add_argument(
    "--seed", type=int, default=123, help="random seed to use. Default=123"
)
opt = parser.parse_args()

print(opt)

if opt.cuda and not torch.cuda.is_available():
    raise Exception("No GPU found, please run without --cuda")
if not opt.mps and torch.backends.mps.is_available():
    raise Exception("Found mps device, please run with --mps to enable macOS GPU")

torch.manual_seed(opt.seed)
use_mps = opt.mps and torch.backends.mps.is_available()

if opt.cuda:
    device = torch.device("cuda")
elif use_mps:
    device = torch.device("mps")
else:
    device = torch.device("cpu")

print("===> Loading datasets")
train_set = get_training_set(opt.upscale_factor)
test_set = get_test_set(opt.upscale_factor)
training_data_loader = DataLoader(
    dataset=train_set, num_workers=opt.threads, batch_size=opt.batch_size, shuffle=True
)
testing_data_loader = DataLoader(
    dataset=test_set,
    num_workers=opt.threads,
    batch_size=opt.test_batch_size,
    shuffle=False,
)

print("===> Building model")
model = Net(upscale_factor=opt.upscale_factor).to(device)
criterion = nn.MSELoss()

optimizer = optim.Adam(model.parameters(), lr=opt.lr)


def train(epoch):
    epoch_loss = 0
    for iteration, batch in enumerate(training_data_loader, 1):
        input, target = batch[0].to(device), batch[1].to(device)

        optimizer.zero_grad()
        loss = criterion(model(input), target)
        epoch_loss += loss.item()
        loss.backward()
        optimizer.step()

        print(
            f"===> Epoch[{epoch}]({iteration}/{len(training_data_loader)}): Loss: {loss.item():.4f}"
        )

    print(
        f"===> Epoch {epoch} Complete: Avg. Loss: {epoch_loss / len(training_data_loader):.4f}"
    )


def test():
    avg_psnr = 0
    with torch.no_grad():
        for batch in testing_data_loader:
            input, target = batch[0].to(device), batch[1].to(device)

            prediction = model(input)
            mse = criterion(prediction, target)
            psnr = 10 * log10(1 / mse.item())
            avg_psnr += psnr
    print(f"===> Avg. PSNR: {avg_psnr / len(testing_data_loader):.4f} dB")


def checkpoint(epoch):
    model_out_path = f"model_epoch_{epoch}.pth"
    torch.save(model, model_out_path)
    print(f"Checkpoint saved to {model_out_path}")


for epoch in range(1, opt.nb_epochs + 1):
    train(epoch)
    test()

checkpoint(opt.nb_epochs)
