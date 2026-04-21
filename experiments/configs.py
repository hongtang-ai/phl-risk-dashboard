"""超参网格：宽度、深度与结构开关。"""

WIDTHS = [8, 16, 32, 64, 128]
DEPTHS = [1, 2, 3, 4]

CONFIGS = [
    {"bn": False, "res": False},
    {"bn": True, "res": False},
    {"bn": False, "res": True},
]

EPOCHS = 15
BATCH_SIZE = 256
LR = 1e-3
SEED = 42
