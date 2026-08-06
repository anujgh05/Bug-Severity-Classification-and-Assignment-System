import os

import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    auc,
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

    model = load_object(model_path)
    data_transformer = DataTransformation()

    _, X_test, _, y_test, _ = data_transformer.initiate_data_transformation(
        train_path, test_path
    )
    return model, X_test, y_test


def plot_confusion_matrix(model, X_test, y_test):
    y_pred = model.predict(X_test)
    cm = confusion_matrix(y_test, y_pred)
    labels = getattr(model, 'classes_', None)

    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=labels)
    disp.plot(cmap='Blues', xticks_rotation=45)

    plt.title('Confusion Matrix')
    plt.tight_layout()
    plt.show()


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
    model, X_test, y_test = load_data_and_model()
    plot_confusion_matrix(model, X_test, y_test)
    plot_roc_curve(model, X_test, y_test)
    plot_precision_recall_curve(model, X_test, y_test)

