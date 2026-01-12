import pandas as pd
import numpy as np
from models.svm import SVMModel
from core.preprocessor import Preprocessor
from features.extractors.basic import BasicFeatureExtractor
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

if __name__ == "__main__":
    print("[SVM TRAINING] Loading dataset...")
    
    df = pd.read_parquet("data/train.parquet")
  #  df = pd.read_parquet("data/task_a_trial.parquet")
    df = df.dropna(subset=["code", "label"])
    
    print(f"[SVM TRAINING] Dataset size: {len(df)} samples")
    
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
    
    print("[SVM TRAINING] Extracting features...")
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
                print(f"[SVM TRAINING] Processed {idx + 1}/{len(df)} samples...")
                
        except Exception as e:
            print(f"[SVM TRAINING] Error processing row {idx}: {e}")
            continue
    
    X = np.array(X_list, dtype=np.float32)
    y = np.array(y_list, dtype=np.int32)
    
    print(f"[SVM TRAINING] Final dataset: X shape={X.shape}, y shape={y.shape}")
    
    # Split train/test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"[SVM TRAINING] Train size: {len(X_train)}, Test size: {len(X_test)}")
    
    # Train model with proper calibration
    print("[SVM TRAINING] Training model with calibration...")
    model = SVMModel()
    model.train(X_train, y_train)
    
    print("[SVM TRAINING] Training complete!")
    
    # Evaluate
    print("[SVM TRAINING] Evaluating model...")
    y_pred_proba = model.predict(X_test)
    y_pred = (y_pred_proba > 0.5).astype(int)
    
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    
    print(f"\n[SVM RESULTS]")
    print(f"  Accuracy:  {accuracy:.4f}")
    print(f"  Precision: {precision:.4f}")
    print(f"  Recall:    {recall:.4f}")
    print(f"  F1 Score:  {f1:.4f}")
    
    # Check probability distribution
    print(f"\n[SVM PROBABILITY CHECK]")
    print(f"  Min probability: {y_pred_proba.min():.6f}")
    print(f"  Max probability: {y_pred_proba.max():.6f}")
    print(f"  Mean probability: {y_pred_proba.mean():.6f}")
    print(f"  Median probability: {np.median(y_pred_proba):.6f}")
    
    # Save model
    print("\n[SVM TRAINING] Saving model...")
    model.save("data/svm_model.pkl")
    
    print("[SVM TRAINING] ✓ Training complete! Model saved to data/svm_model.pkl")
