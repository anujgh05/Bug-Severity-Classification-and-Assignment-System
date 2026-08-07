import os

import matplotlib.pyplot as plt
import numpy as np
from sklearn.base import clone
from sklearn.calibration import CalibrationDisplay
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    auc,
    accuracy_score,
    brier_score_loss,
    confusion_matrix,
    precision_recall_curve,
    precision_recall_fscore_support,
    roc_curve,
    average_precision_score,
)
from sklearn.preprocessing import label_binarize

from src.components.data_transformation import DataTransformation
from src.utils import load_object


def load_data_and_model():
    artifacts_dir = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'artifacts')
    train_path = os.path.join(artifacts_dir, 'train.csv')
    test_path = os.path.join(artifacts_dir, 'test.csv')
    model_path = os.path.join(artifacts_dir, 'model.pkl')
    svd_path = os.path.join(artifacts_dir, 'svd.pkl')

    model = load_object(model_path)
    data_transformer = DataTransformation()

    X_train, X_test, y_train, y_test, _ = data_transformer.initiate_data_transformation(
        train_path, test_path
    )

    if os.path.exists(svd_path):
        svd = load_object(svd_path)
        X_train = svd.transform(X_train)
        X_test = svd.transform(X_test)

    return model, X_train, X_test, y_train, y_test


def plot_confusion_matrix(model, X_test, y_test):
    y_pred = model.predict(X_test)
    cm = confusion_matrix(y_test, y_pred)
    labels = getattr(model, 'classes_', None)

    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=labels)
    disp.plot(cmap='Blues', xticks_rotation=45)

    plt.title('Confusion Matrix')
    plt.tight_layout()
    plt.show()


def plot_training_accuracy(model, X_train, y_train):
    y_train_pred = model.predict(X_train)
    train_accuracy = accuracy_score(y_train, y_train_pred)

    plt.figure(figsize=(6, 4))
    plt.bar(['Training Accuracy'], [train_accuracy], color='#4c8cff')
    plt.ylim([0.0, 1.0])
    plt.ylabel('Accuracy')
    plt.title('Training Dataset Accuracy')
    plt.text(0, train_accuracy + 0.02, f'{train_accuracy:.3f}', ha='center', va='bottom', fontsize=12)
    plt.tight_layout()
    plt.show()
    print(train_accuracy)


def plot_calibration_curves(model, X_train, X_test, y_train, y_test):
    artifacts_dir = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'artifacts')
    os.makedirs(artifacts_dir, exist_ok=True)

    base_estimator = clone(model.estimator)
    base_estimator.fit(X_train, y_train)

    probs_uncalibrated = base_estimator.predict_proba(X_test)
    probs_calibrated = model.predict_proba(X_test)

    labels = getattr(model, 'classes_', None)
    if labels is None:
        raise ValueError('Model does not expose classes_ for calibration plotting.')

    n_classes = probs_calibrated.shape[1]
    axes = np.atleast_1d(plt.subplots(1, n_classes, figsize=(6 * n_classes, 5))[1])

    for i, label in enumerate(labels):
        y_true_binary = (y_test == label).astype(int)

        CalibrationDisplay.from_predictions(
            y_true_binary,
            probs_uncalibrated[:, i],
            n_bins=10,
            name='Uncalibrated RF',
            ax=axes[i]
        )
        CalibrationDisplay.from_predictions(
            y_true_binary,
            probs_calibrated[:, i],
            n_bins=10,
            name='Calibrated RF',
            ax=axes[i]
        )

        brier_uncal = brier_score_loss(y_true_binary, probs_uncalibrated[:, i])
        brier_cal = brier_score_loss(y_true_binary, probs_calibrated[:, i])

        axes[i].set_title(
            f"Class {label} ({i})\n"
            f"Brier: uncal={brier_uncal:.4f} | cal={brier_cal:.4f}"
        )
        axes[i].legend(loc='lower right')

    fig_path = os.path.join(artifacts_dir, 'calibration_curves.png')
    plt.tight_layout()
    plt.savefig(fig_path, dpi=150)
    plt.show()
    print(f'[INFO] Calibration curves saved to artifacts folder at {fig_path}')


def plot_roc_curve(model, X_test, y_test):
    labels = getattr(model, 'classes_', None)
    if labels is None:
        raise ValueError('Model does not expose classes_ for ROC plotting.')

    y_score = model.predict_proba(X_test)
    y_test_bin = label_binarize(y_test, classes=labels)
    n_classes = y_test_bin.shape[1]

    plt.figure(figsize=(8, 6))
    for i in range(n_classes):
        fpr, tpr, _ = roc_curve(y_test_bin[:, i], y_score[:, i])
        roc_auc = auc(fpr, tpr)
        plt.plot(fpr, tpr, lw=2, label=f'Class {labels[i]} (AUC = {roc_auc:.3f})')

    if n_classes > 1:
        fpr, tpr, _ = roc_curve(y_test_bin.ravel(), y_score.ravel())
        plt.plot(fpr, tpr, color='navy', linestyle='--', lw=2, label='Micro-average ROC')

    plt.plot([0, 1], [0, 1], color='gray', linestyle='--', lw=1)
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver Operating Characteristic (ROC) Curve')
    plt.legend(loc='lower right')
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def plot_precision_recall_curve(model, X_test, y_test):
    labels = getattr(model, 'classes_', None)
    if labels is None:
        raise ValueError('Model does not expose classes_ for precision-recall plotting.')

    y_score = model.predict_proba(X_test)
    y_test_bin = label_binarize(y_test, classes=labels)
    n_classes = y_test_bin.shape[1]

    plt.figure(figsize=(8, 6))
    for i in range(n_classes):
        precision, recall, _ = precision_recall_curve(y_test_bin[:, i], y_score[:, i])
        ap = average_precision_score(y_test_bin[:, i], y_score[:, i])
        plt.plot(recall, precision, lw=2, label=f'Class {labels[i]} (AP = {ap:.3f})')

    if n_classes > 1:
        precision, recall, _ = precision_recall_curve(y_test_bin.ravel(), y_score.ravel())
        ap = average_precision_score(y_test_bin, y_score, average='micro')
        plt.plot(recall, precision, color='navy', linestyle='--', lw=2, label=f'Micro-average PR (AP = {ap:.3f})')

    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.title('Precision-Recall Curve')
    plt.legend(loc='lower left')
    plt.grid(True)
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    model, X_train, X_test, y_train, y_test = load_data_and_model()
    plot_calibration_curves(model, X_train, X_test, y_train, y_test)
   
