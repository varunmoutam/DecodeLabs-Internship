"""
train_model.py
--------------
Trains a KNN classifier on the Iris dataset, saves the model and scaler,
and generates dataset visualisation + confusion matrix images.

Run once before starting the Flask app:
    python train_model.py
"""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")          # headless backend – no display needed
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap
import seaborn as sns

from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import (confusion_matrix, classification_report,
                              f1_score, accuracy_score)
import joblib

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR   = os.path.join(BASE_DIR, "model")
IMAGES_DIR  = os.path.join(BASE_DIR, "static", "images")
MODEL_PATH  = os.path.join(MODEL_DIR,  "iris_knn.pkl")
SCALER_PATH = os.path.join(MODEL_DIR,  "scaler.pkl")
CM_PATH     = os.path.join(IMAGES_DIR, "confusion_matrix.png")
VIZ_PATH    = os.path.join(IMAGES_DIR, "dataset_viz.png")

os.makedirs(MODEL_DIR,  exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)

# ── Palette (matches the web UI) ─────────────────────────────────────────────
PALETTE = ["#4f8ef7", "#f7934f", "#4fc97f"]
CLASS_NAMES = ["Setosa", "Versicolor", "Virginica"]
DARK_BG  = "#0f1117"
CARD_BG  = "#1a1d2e"
GRID_COL = "#2a2d3e"
TEXT_COL = "#e0e4ff"

# ── 1. Load dataset ──────────────────────────────────────────────────────────
iris      = load_iris()
X, y      = iris.data, iris.target
feat_names = ["Sepal Length (cm)", "Sepal Width (cm)",
              "Petal Length (cm)", "Petal Width (cm)"]

# ── 2. Split ─────────────────────────────────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42, stratify=y
)

# ── 3. Scale ─────────────────────────────────────────────────────────────────
scaler  = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test  = scaler.transform(X_test)

# ── 4. Find optimal K (1-20, odd only) ───────────────────────────────────────
best_k, best_acc = 5, 0.0
for k in range(1, 21, 2):
    knn = KNeighborsClassifier(n_neighbors=k)
    knn.fit(X_train, y_train)
    acc = accuracy_score(y_test, knn.predict(X_test))
    if acc > best_acc:
        best_acc, best_k = acc, k

print(f"  Optimal K = {best_k}  |  Test Accuracy = {best_acc*100:.2f}%")

# ── 5. Train final model ──────────────────────────────────────────────────────
model = KNeighborsClassifier(n_neighbors=best_k)
model.fit(X_train, y_train)
y_pred = model.predict(X_test)

# ── 6. Save model & scaler ───────────────────────────────────────────────────
joblib.dump(model,  MODEL_PATH)
joblib.dump(scaler, SCALER_PATH)
print(f"  Model  saved → {MODEL_PATH}")
print(f"  Scaler saved → {SCALER_PATH}")

# ── 7. Console report ────────────────────────────────────────────────────────
print("\n" + "="*55)
print(classification_report(y_test, y_pred, target_names=CLASS_NAMES))
f1 = f1_score(y_test, y_pred, average="weighted")
print(f"  Weighted F1 Score : {f1:.4f}")
print("="*55 + "\n")

# ────────────────────────────────────────────────────────────────────────────
# 8. Dataset Visualisation  (4-panel scatter grid)
# ────────────────────────────────────────────────────────────────────────────
def make_dataset_viz():
    pairs = [(0, 1), (0, 2), (0, 3), (2, 3)]
    axis_labels = feat_names
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.patch.set_facecolor(DARK_BG)
    axes = axes.flatten()

    for ax, (xi, yi) in zip(axes, pairs):
        ax.set_facecolor(CARD_BG)
        ax.grid(color=GRID_COL, linewidth=0.6, zorder=0)
        for spine in ax.spines.values():
            spine.set_edgecolor(GRID_COL)
        for cls_idx, (cls_name, col) in enumerate(zip(CLASS_NAMES, PALETTE)):
            mask = y == cls_idx
            ax.scatter(X[mask, xi], X[mask, yi],
                       color=col, edgecolors="white", linewidths=0.4,
                       alpha=0.85, s=55, zorder=3, label=cls_name)
        ax.set_xlabel(axis_labels[xi], color=TEXT_COL, fontsize=9)
        ax.set_ylabel(axis_labels[yi], color=TEXT_COL, fontsize=9)
        ax.tick_params(colors=TEXT_COL, labelsize=8)

    # shared legend
    handles = [mpatches.Patch(color=c, label=n)
               for c, n in zip(PALETTE, CLASS_NAMES)]
    fig.legend(handles=handles, loc="lower center", ncol=3,
               frameon=False, fontsize=11,
               labelcolor=TEXT_COL, bbox_to_anchor=(0.5, -0.02))

    fig.suptitle("Iris Dataset — Feature Pair Scatterplots",
                 color=TEXT_COL, fontsize=15, fontweight="bold", y=1.01)
    plt.tight_layout(pad=2.0)
    plt.savefig(VIZ_PATH, dpi=130, bbox_inches="tight",
                facecolor=DARK_BG, edgecolor="none")
    plt.close()
    print(f"  Dataset viz saved → {VIZ_PATH}")

# ────────────────────────────────────────────────────────────────────────────
# 9. Confusion Matrix
# ────────────────────────────────────────────────────────────────────────────
def make_confusion_matrix():
    cm = confusion_matrix(y_test, y_pred)

    fig, ax = plt.subplots(figsize=(7, 6))
    fig.patch.set_facecolor(DARK_BG)
    ax.set_facecolor(DARK_BG)

    # custom blue→orange colourmap
    cmap = LinearSegmentedColormap.from_list(
        "iris_cmap", ["#1a1d2e", "#4f8ef7", "#f7934f"])

    sns.heatmap(cm, annot=True, fmt="d", cmap=cmap,
                linewidths=1.5, linecolor=DARK_BG,
                xticklabels=CLASS_NAMES, yticklabels=CLASS_NAMES,
                annot_kws={"size": 18, "weight": "bold", "color": "white"},
                ax=ax, cbar=True)

    ax.set_title(f"Confusion Matrix  (K={best_k}, Acc={best_acc*100:.1f}%)",
                 color=TEXT_COL, fontsize=14, fontweight="bold", pad=14)
    ax.set_xlabel("Predicted Label", color=TEXT_COL, fontsize=11, labelpad=8)
    ax.set_ylabel("True Label",      color=TEXT_COL, fontsize=11, labelpad=8)
    ax.tick_params(colors=TEXT_COL, labelsize=10)

    # colour-bar text
    cbar = ax.collections[0].colorbar
    cbar.ax.yaxis.set_tick_params(color=TEXT_COL, labelcolor=TEXT_COL)

    plt.tight_layout()
    plt.savefig(CM_PATH, dpi=130, bbox_inches="tight",
                facecolor=DARK_BG, edgecolor="none")
    plt.close()
    print(f"  Confusion matrix saved → {CM_PATH}")

make_dataset_viz()
make_confusion_matrix()

print("\n✅  Training complete. Run:  python app.py\n")