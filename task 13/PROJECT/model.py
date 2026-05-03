import os
import cv2
import numpy as np
import pickle
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.neighbors import KNeighborsClassifier

MODEL_PATH = "model.pkl"
FACE_CASCADE = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
EMBED_SIZE = (64, 64)
LBP_BINS = 256

# ---- Utility: select the best face when multiple candidates are found ----
def choose_best_face(faces, image_shape):
    if len(faces) == 1:
        return faces[0]
    image_center = np.array([image_shape[1] / 2, image_shape[0] / 2])
    best = None
    best_score = -1
    for (x, y, w, h) in faces:
        face_center = np.array([x + w / 2, y + h / 2])
        area = w * h
        distance = np.linalg.norm(face_center - image_center)
        score = area - distance * 2
        if score > best_score:
            best_score = score
            best = (x, y, w, h)
    return best


def lbp_histogram(image_gray):
    h, w = image_gray.shape
    lbp = np.zeros((h - 2, w - 2), dtype=np.uint8)
    for dy in range(1, h - 1):
        for dx in range(1, w - 1):
            center = image_gray[dy, dx]
            code = 0
            code |= (image_gray[dy-1, dx-1] > center) << 7
            code |= (image_gray[dy-1, dx] > center) << 6
            code |= (image_gray[dy-1, dx+1] > center) << 5
            code |= (image_gray[dy, dx+1] > center) << 4
            code |= (image_gray[dy+1, dx+1] > center) << 3
            code |= (image_gray[dy+1, dx] > center) << 2
            code |= (image_gray[dy+1, dx-1] > center) << 1
            code |= (image_gray[dy, dx-1] > center) << 0
            lbp[dy-1, dx-1] = code
    hist = cv2.calcHist([lbp], [0], None, [LBP_BINS], [0, 256]).flatten()
    if hist.sum() > 0:
        hist = hist.astype(np.float32) / hist.sum()
    return hist


def preprocess_face(face_gray):
    face_gray = cv2.equalizeHist(face_gray)
    face_gray = cv2.resize(face_gray, EMBED_SIZE, interpolation=cv2.INTER_AREA)
    raw = face_gray.flatten().astype(np.float32) / 255.0
    lbp = lbp_histogram(face_gray)
    return np.concatenate([raw, lbp])


def crop_face_and_embed(bgr_image, x, y, w, h):
    face = bgr_image[y:y+h, x:x+w]
    gray_face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
    return preprocess_face(gray_face)


def extract_embedding_for_image(stream_or_bytes):
    data = stream_or_bytes.read()
    arr = np.frombuffer(data, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        return None

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)
    faces = FACE_CASCADE.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4, minSize=(48, 48))

    if len(faces) == 0:
        return None

    x, y, w, h = choose_best_face(faces, img.shape)
    return crop_face_and_embed(img, x, y, w, h)

# ---- Load model helpers ----
def load_model_if_exists():
    if not os.path.exists(MODEL_PATH):
        return None
    with open(MODEL_PATH, "rb") as f:
        return pickle.load(f)

def predict_with_model(clf, emb):
    # returns label and confidence (max probability)
    proba = clf.predict_proba([emb])[0]
    idx = np.argmax(proba)
    label = clf.classes_[idx]
    conf = float(proba[idx])
    return label, conf

# ---- Training function used in background ----
def train_model_background(dataset_dir, progress_callback=None):
    """
    dataset_dir/
        student_id/
            img1.jpg
            img2.jpg
    progress_callback(progress_percent, message) -> optional
    """
    X = []
    y = []
    student_dirs = [d for d in os.listdir(dataset_dir) if os.path.isdir(os.path.join(dataset_dir, d))]
    total_students = max(1, len(student_dirs))
    processed = 0

    for sid in student_dirs:
        folder = os.path.join(dataset_dir, sid)
        files = [f for f in os.listdir(folder) if f.lower().endswith((".jpg",".jpeg",".png"))]
        for fn in files:
            path = os.path.join(folder, fn)
            img = cv2.imread(path)
            if img is None:
                continue

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            gray = cv2.equalizeHist(gray)
            faces = FACE_CASCADE.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4, minSize=(48, 48))
            if len(faces) == 0:
                continue

            x, y_face, w, h = choose_best_face(faces, img.shape)
            face_gray = gray[y_face:y_face+h, x:x+w]
            emb = preprocess_face(face_gray)
            emb_flip = preprocess_face(cv2.flip(face_gray, 1))
            X.append(emb)
            y.append(int(sid))
            X.append(emb_flip)
            y.append(int(sid))
        processed += 1
        if progress_callback:
            pct = int((processed/total_students)*80)
            progress_callback(pct, f"Processed {processed}/{total_students} students")

    if len(X) == 0:
        if progress_callback:
            progress_callback(0, "No training data found")
        return

    X = np.stack(X)
    y = np.array(y)

    if progress_callback:
        progress_callback(85, "Training recognition pipeline...")

    clf = Pipeline([
        ("scaler", StandardScaler()),
        ("pca", PCA(n_components=min(150, X.shape[0], X.shape[1]), whiten=True, random_state=42)),
        ("knn", KNeighborsClassifier(n_neighbors=3, weights="distance", n_jobs=-1))
    ])
    clf.fit(X, y)

    with open(MODEL_PATH, "wb") as f:
        pickle.dump(clf, f)

    if progress_callback:
        progress_callback(100, "Training complete")
