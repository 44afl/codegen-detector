import pandas as pd
from models.transformer import TransformerModel

if __name__ == "__main__":
    df = pd.read_parquet("data/task_a_trial.parquet")
    print("Columns:", df.columns)

    TEXT_COL = "code"
    LABEL_COL = "label"

    texts = df[TEXT_COL].astype(str).tolist()
    labels = df[LABEL_COL].astype(int).tolist()

    # ==== SUBSET PENTRU TEST (ca să nu moară CPU-ul) ====
    subset_size = 1000   # poți crește mai târziu
    texts = texts[:subset_size]
    labels = labels[:subset_size]
    print(f"Using subset of {len(texts)} samples for training.")

    model = TransformerModel()

    batch_size = 32
    num_epochs = 1

    for epoch in range(num_epochs):
        epoch_loss = 0.0
        num_batches = (len(texts) + batch_size - 1) // batch_size
        print(f"[EPOCH {epoch+1}] starting, {num_batches} batches...")

        for batch_idx in range(0, len(texts), batch_size):
            batch_texts = texts[batch_idx:batch_idx + batch_size]
            batch_labels = labels[batch_idx:batch_idx + batch_size]

            loss = model.train(batch_texts, batch_labels)
            epoch_loss += loss

            # progres la fiecare 10 batch-uri
            current_batch = batch_idx // batch_size + 1
            if current_batch % 10 == 0 or current_batch == num_batches:
                print(f"  batch {current_batch}/{num_batches} - last_loss={loss:.4f}")

        print(f"[EPOCH {epoch + 1}] total_loss = {epoch_loss:.4f}")

    import joblib
    joblib.dump(model, "data/transformer_model.pkl")
    print("[FINAL RESULTS TRANSFORMER] saved transformer_model.pkl")
