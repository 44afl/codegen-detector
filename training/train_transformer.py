import pandas as pd
import numpy as np
from models.transformer import TransformerModel
from core.preprocessor import Preprocessor
from features.extractors.basic import BasicFeatureExtractor
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

if __name__ == "__main__":
    print("[TRANSFORMER TRAINING] Loading dataset...")
    df = pd.read_parquet("data/task_a_trial.parquet")
    df = df.dropna(subset=["code", "label"])
    
    print(f"[TRANSFORMER TRAINING] Dataset size: {len(df)} samples")
    
    # Initialize preprocessor and feature extractor (same as in prediction)
    preprocessor = Preprocessor()
    feature_extractor = BasicFeatureExtractor()
    
    # Feature order must match PredictionFacade
    feature_order = [
        "n_lines",
        "avg_line_len",
        "n_chars",
        "n_tabs",
        "n_spaces",
        "n_keywords"
    ]
    
    print("[TRANSFORMER TRAINING] Preparing text inputs for transformer...")
    X_list = []
    y_list = []

    for idx, row in df.iterrows():
        try:
            code = str(row["code"])
            label = int(row["label"])

            # Process code same way as in prediction and keep text for tokenizer
            processed = preprocessor.clean(code)

            X_list.append(processed)
            y_list.append(label)

            if (idx + 1) % 100 == 0:
                print(f"[TRANSFORMER TRAINING] Processed {idx + 1}/{len(df)} samples...")

        except Exception as e:
            print(f"[TRANSFORMER TRAINING] Error processing row {idx}: {e}")
            continue

    X = np.array(X_list, dtype=object)
    y = np.array(y_list, dtype=np.int32)
    
    print(f"[TRANSFORMER TRAINING] Final dataset: X shape={X.shape}, y shape={y.shape}")
    
    # Split train/test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"[TRANSFORMER TRAINING] Train size: {len(X_train)}, Test size: {len(X_test)}")

    # Train model
    print("[TRANSFORMER TRAINING] Training model...")
    model = TransformerModel()
    model.train(list(X_train), list(y_train))
    
    print("[TRANSFORMER TRAINING] Training complete!")
    
    # Evaluate
    print("[TRANSFORMER TRAINING] Evaluating model...")
    y_pred_proba = model.predict(list(X_test))
    y_pred = (y_pred_proba > 0.5).astype(int)
    
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    
    print(f"\n[TRANSFORMER RESULTS]")
    print(f"  Accuracy:  {accuracy:.4f}")
    print(f"  Precision: {precision:.4f}")
    print(f"  Recall:    {recall:.4f}")
    print(f"  F1 Score:  {f1:.4f}")
    
    # Check probability distribution
    print(f"\n[TRANSFORMER PROBABILITY CHECK]")
    print(f"  Min probability: {y_pred_proba.min():.6f}")
    print(f"  Max probability: {y_pred_proba.max():.6f}")
    print(f"  Mean probability: {y_pred_proba.mean():.6f}")
    print(f"  Median probability: {np.median(y_pred_proba):.6f}")
    print(f"  Class 0 (human) count: {np.sum(y_pred == 0)}")
    print(f"  Class 1 (machine) count: {np.sum(y_pred == 1)}")
    
    # Save model
    print("\n[TRANSFORMER TRAINING] Saving model...")
    model.save("data/transformer_model.pkl")
    
    print("[TRANSFORMER TRAINING] ✓ Training complete! Model saved to data/transformer_model.pkl")
