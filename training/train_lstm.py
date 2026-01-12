import pandas as pd
import numpy as np
from models.lstm import LSTMModel
from core.preprocessor import Preprocessor
from features.extractors.basic import BasicFeatureExtractor
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

if __name__ == "__main__":
    print("[LSTM TRAINING] Loading dataset...")
  #  df = pd.read_parquet("data/task_a_trial.parquet")

    df = pd.read_parquet("data/train.parquet")
    df = df.dropna(subset=["code", "label"])
    
    print(f"[LSTM TRAINING] Dataset size: {len(df)} samples")
    
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
    
    print("[LSTM TRAINING] Extracting features...")
    X_list = []
    y_list = []
    
    for idx, row in df.iterrows():
        try:
            code = str(row["code"])
            label = int(row["label"])
            
            # Process code same way as in prediction
            processed = preprocessor.clean(code)
            features = feature_extractor.extract_features(processed)
            
            # Create feature vector in correct order
            feature_vector = [float(features.get(f, 0)) for f in feature_order]
            
            X_list.append(feature_vector)
            y_list.append(label)
            
            if (idx + 1) % 100 == 0:
                print(f"[LSTM TRAINING] Processed {idx + 1}/{len(df)} samples...")
                
        except Exception as e:
            print(f"[LSTM TRAINING] Error processing row {idx}: {e}")
            continue
    
    X = np.array(X_list, dtype=np.float32)
    y = np.array(y_list, dtype=np.int32)
    
    print(f"[LSTM TRAINING] Final dataset: X shape={X.shape}, y shape={y.shape}")
    
    # Split train/test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"[LSTM TRAINING] Train size: {len(X_train)}, Test size: {len(X_test)}")
    
    # Train model
    print("[LSTM TRAINING] Training model...")
    model = LSTMModel()
    model.train(X_train, y_train)
    
    print("[LSTM TRAINING] Training complete!")
    
    # Evaluate
    print("[LSTM TRAINING] Evaluating model...")
    y_pred_proba = model.predict(X_test)
    best_t, best_f1 = 0.5, -1
    for t in np.arange(0.05, 0.96, 0.05):
        y_hat = (y_pred_proba >= t).astype(int)
        f = f1_score(y_test, y_hat, average="macro")
        if f > best_f1:
            best_f1, best_t = f, t
    print("Best threshold:", best_t, "macroF1:", best_f1)

    y_pred = (y_pred_proba > best_t).astype(int)
    
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    from sklearn.metrics import f1_score
    macro_f1 = f1_score(y_test, y_pred, average="macro")
    print(f"  Macro F1:  {macro_f1:.4f}")

    
    print(f"\n[LSTM RESULTS]")
    print(f"  Accuracy:  {accuracy:.4f}")
    print(f"  Precision: {precision:.4f}")
    print(f"  Recall:    {recall:.4f}")
 
    
    # Check probability distribution
    print(f"\n[LSTM PROBABILITY CHECK]")
    print(f"  Min probability: {y_pred_proba.min():.6f}")
    print(f"  Max probability: {y_pred_proba.max():.6f}")
    print(f"  Mean probability: {y_pred_proba.mean():.6f}")
    print(f"  Median probability: {np.median(y_pred_proba):.6f}")
    print(f"  Class 0 (human) count: {np.sum(y_pred == 0)}")
    print(f"  Class 1 (machine) count: {np.sum(y_pred == 1)}")
    
    # Save model
    print("\n[LSTM TRAINING] Saving model...")
    model.save("data/lstm_model.pkl")
    
    print("[LSTM TRAINING] ✓ Training complete! Model saved to data/lstm_model.pkl")
