# Practical Work 2: Super-Resolution CNN

This is a supporting repository you'll use for the Practical Work 2 on the chapter about Super-Resolution you'll find [here](https://cpcdoy.github.io/articles/tp-2/)

## Usage:

### Train

`sh run_train.sh`

You can modify the parameters inside this file:
- --upscale_factor (int): How much to upscale the image
- --batch_size (int): Batch size 
- --test_batch_size (int): Batch size for testing
- --nb_epochs (int): How many train epochs
- --lr (float): The Learning Rate (LR) for training

### Run on an image

`sh run_test.sh`

You can modify the parameters inside this file:
- --input_image (str): The image you want to upscale
- --model (str): The path to your model
- --output_filename (str): The final upscaled image to be saved