# cnn_microscope

## Pliki

/obrazy/ - obrazy są podzielone na foldery Negative i Positive, Positive mają widoczne szczeliny na podstawie których uczy się sieć (czy są negative czy positive)

model_def.py - Zawiera definicje modelu CNN (klasa CNNModel)

train.py - Trenuje model na podstawie obrazów z folderu obrazy i zapisuje model do cnn.pth

predict.py - Ładuje model cnn.pth i na podstawie podanego zdjęcia określa klasę i rysuje wykres z mapą aktywacji (GradCAM)

cnn.pth - Zapisane wagi modelu, wymaga klasy CNNModel z model_def.py do załadowania

main.py - serwis - odbiera dane od akwizycji obrazów i wysyła post do bazy danych


## Biblioteki
- torch>=2.0.0
- torchvision>=0.15.0
- torchcam>=0.3.2
- torch-directml (jeśli cpu to można zmienić i to wywalić)
- opencv-python
- numpy
- scikit-learn
- pillow
- fastapi
- uvicorn
- requests