import os
import cv2
import time
import numpy as np
import torch
from torch.utils.data import DataLoader, TensorDataset
from sklearn.model_selection import train_test_split
from torch import nn
from model_def import CNNModel

IMG_SIZE = 128
neg_path = 'obrazy/Negative'
pos_path = 'obrazy/Positive'
MODEL_PATH = 'cnn.pth'
EPOCHS = 25

device = torch.device("cpu")

try:
    import torch_directml

    device = torch_directml.device()
    _ = torch.tensor([1.0], device=device)
except Exception:
    print("DirectML niedostepny – uzywany CPU")

print(f"Uzywane urzadzenie: {device}")


def load_images_from_folder(folder, label):
    images, labels = [], []
    for filename in os.listdir(folder):
        img_path = os.path.join(folder, filename)
        img = cv2.imread(img_path)
        if img is not None:
            img = cv2.resize(img, (IMG_SIZE, IMG_SIZE))
            images.append(img)
            labels.append(label)
    return images, labels


# wczytywanie i przygotowanie danych
neg_images, neg_labels = load_images_from_folder(neg_path, 0)
pos_images, pos_labels = load_images_from_folder(pos_path, 1)

images = np.array(neg_images + pos_images)
labels = np.array(neg_labels + pos_labels)

images_tensor = torch.tensor(images.astype(np.float32) / 255.0).permute(0, 3, 1, 2)
labels_tensor = torch.tensor(labels).long()

X_temp, X_test, y_temp, y_test = train_test_split(images_tensor, labels_tensor, test_size=0.2, random_state=42)
X_train, X_val, y_train, y_val = train_test_split(X_temp, y_temp, test_size=0.25, random_state=42)

train_loader = DataLoader(TensorDataset(X_train, y_train), batch_size=32, shuffle=True)
val_loader = DataLoader(TensorDataset(X_val, y_val), batch_size=32)

# trening modelu
model = CNNModel().to(device)
optimizer = torch.optim.Adam(model.parameters())
criterion = nn.CrossEntropyLoss()

start_time = time.time()

# early stopping
best_val_loss = float('inf')
epochs_no_improve = 0
early_stop_patience = 5
min_delta = 0.001

for epoch in range(EPOCHS):
    model.train()
    train_correct, train_total, epoch_loss = 0, 0, 0

    for batch_x, batch_y in train_loader:
        batch_x, batch_y = batch_x.to(device), batch_y.to(device)

        optimizer.zero_grad()
        output = model(batch_x)
        loss = criterion(output, batch_y)
        loss.backward()
        optimizer.step()

        epoch_loss += loss.item()
        preds = torch.argmax(output, dim=1)
        train_correct += (preds == batch_y).sum().item()
        train_total += batch_y.size(0)

    train_acc = train_correct / train_total * 100
    avg_loss = epoch_loss / len(train_loader)

    # walidacja
    model.eval()
    val_loss = 0
    val_correct, val_total = 0, 0
    with torch.no_grad():
        for val_x, val_y in val_loader:
            val_x, val_y = val_x.to(device), val_y.to(device)
            val_output = model(val_x)
            loss = criterion(val_output, val_y)
            val_loss += loss.item()

            val_preds = torch.argmax(val_output, dim=1)
            val_correct += (val_preds == val_y).sum().item()
            val_total += val_y.size(0)

    val_loss /= len(val_loader)
    val_acc = val_correct / val_total * 100

    print(
        f"Epoch {epoch + 1}/{EPOCHS} - Loss: {avg_loss:.4f} - Train Acc: {train_acc:.2f}% - Val Loss: {val_loss:.4f} - Val Acc: {val_acc:.2f}%")

    # wczesne zatrzymanie
    if best_val_loss - val_loss > min_delta:
        best_val_loss = val_loss
        epochs_no_improve = 0
        torch.save(model.state_dict(), MODEL_PATH)
        print("Poprawa - zapisano model")
    else:
        epochs_no_improve += 1
        print(f"Brak poprawy: {epochs_no_improve}/{early_stop_patience} epok")

    if epochs_no_improve >= early_stop_patience:
        print("Wczesne zatrzymanie - trening przerwany")
        break

end_time = time.time()
print(f"\nCzas uczenia: {end_time - start_time:.2f} sekund")
print(f"Model zapisany do: {MODEL_PATH}")

# ewaluacja na zbiorze testowym
test_loader = DataLoader(TensorDataset(X_test, y_test), batch_size=32)
model.load_state_dict(torch.load(MODEL_PATH, weights_only=False))
model.eval()

test_correct, test_total = 0, 0

with torch.no_grad():
    for test_x, test_y in test_loader:
        test_x, test_y = test_x.to(device), test_y.to(device)
        output = model(test_x)
        preds = torch.argmax(output, dim=1)
        test_correct += (preds == test_y).sum().item()
        test_total += test_y.size(0)

test_acc = test_correct / test_total * 100
print(f"\nTest Acc: {test_acc:.2f}%")
