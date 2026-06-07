# 🌸 Iris Flower Classification AI
**DecodeLabs Industrial Training — Batch 2026 · Project 2**

A full supervised-learning pipeline that classifies Iris flowers into three species
(*Setosa*, *Versicolor*, *Virginica*) using a K-Nearest Neighbours model, served
through a Flask web application.

---

## 📁 Project Structure

```
IRIS-CLASSIFICATION-AI/
│
├── model/
│   ├── iris_knn.pkl          ← trained KNN model
│   └── scaler.pkl            ← fitted StandardScaler
│
├── static/
│   ├── images/
│   │   ├── confusion_matrix.png
│   │   └── dataset_viz.png
│   └── style.css
│
├── templates/
│   ├── index.html            ← prediction page
│   └── about.html            ← project info page
│
├── app.py                    ← Flask application
├── train_model.py            ← training script
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup & Run

### 1. Clone / Download
```bash
git clone <your-repo-url>
cd IRIS-CLASSIFICATION-AI
```

### 2. Create a virtual environment (recommended)
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Train the model *(run once)*
```bash
python train_model.py
```
This will:
- Train and auto-tune a KNN classifier (K selected from 1–20)
- Save `model/iris_knn.pkl` and `model/scaler.pkl`
- Generate `static/images/dataset_viz.png` and `static/images/confusion_matrix.png`

### 5. Start the Flask server
```bash
python app.py
```
Open your browser at **http://127.0.0.1:5000**

---

## 🧠 How It Works

| Stage | Details |
|---|---|
| **Dataset** | Fisher's Iris — 150 samples, 3 classes, 4 features |
| **Split** | 80 % train / 20 % test (stratified, shuffled) |
| **Scaling** | `StandardScaler` — zero mean, unit variance |
| **Algorithm** | K-Nearest Neighbours (`sklearn.neighbors.KNeighborsClassifier`) |
| **K-tuning** | Odd values 1–20 tested; best test-accuracy K is selected |
| **Evaluation** | Confusion matrix · Classification report · Weighted F1 |
| **Serving** | Flask REST endpoint `/predict` (POST, form data) |

---

## 🌐 Pages

| URL | Description |
|---|---|
| `/` | Input form + live prediction with probability bars |
| `/predict` | POST endpoint — returns JSON result |
| `/about` | Project documentation, pipeline, model config |

---

## 📊 Sample Inputs

| Species | Sepal L | Sepal W | Petal L | Petal W |
|---|---|---|---|---|
| Setosa | 5.1 | 3.5 | 1.4 | 0.2 |
| Versicolor | 6.0 | 2.7 | 4.2 | 1.3 |
| Virginica | 6.7 | 3.1 | 5.6 | 2.4 |

---

## 🛠️ Tech Stack

`Python` · `Flask` · `Scikit-Learn` · `NumPy` · `Matplotlib` · `Seaborn` · `Joblib` · `HTML5` · `CSS3` · `Vanilla JS`

---

## 📄 License
MIT — free to use for educational and portfolio purposes.