# cnn_microscope

## Pliki

/obrazy/ - obrazy są podzielone na foldery Negative i Positive, Positive mają widoczne szczeliny na podstawie których uczy się sieć (czy są negative czy positive)

model_def.py - Zawiera definicje modelu CNN (klasa CNNModel)

train.py - Trenuje model na podstawie obrazów z folderu obrazy i zapisuje model do cnn.pth

predict.py - Ładuje model cnn.pth i na podstawie podanego zdjęcia określa klasę i rysuje wykres z mapą aktywacji (GradCAM)

cnn.pth - Zapisane wagi modelu, wymaga klasy CNNModel z model_def.py do załadowania

main.py - serwis - odbiera dane od akwizycji obrazów i wysyła post do bazy danych


## Biblioteki
- torch
- torch-directml (jeśli używany directml, można cpu - wtedy zmienić kod gdzie jest device)
- torchvision
- torchcam
- matplotlib
- numpy
- opencv-python
- scikit-learn
- fastapi