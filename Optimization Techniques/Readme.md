# Optimizer Analysis

This project builds a Turkish question–answer ranking system using sentence embeddings and compares different optimization algorithms (GD, SGD, Adam).

## Features
- Reads training and test data from structured TXT files
- Generates separate **question** and **answer** embeddings using `turkish-e5-large`
- Trains a simple neural classifier for answer quality (+1 / -1)
- Compares GD, SGD, and Adam optimizers
- Plots accuracy, loss, and training dynamics
- Visualizes weight trajectories with **t-SNE**

## Technologies
- Python, PyTorch
- SentenceTransformers
- NumPy, Matplotlib, scikit-learn

## Data Format
- Each pair contains one good (+1) and one bad (-1) answer

## Outputs
- CSV datasets (train/test)
- Saved embeddings (`.pt`, `.npy`)
- Performance comparison plots
- t-SNE visualization of weight evolution (in 2 diemensions)
