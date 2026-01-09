import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from .service import ModelService


class TransformerModel(ModelService):
    def __init__(self, model_name="distilbert-base-uncased", device=None):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            model_name, num_labels=2
        )
        self.device = device if device else torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )
        self.model.to(self.device)
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=1e-5)
        self.criterion = torch.nn.CrossEntropyLoss()

    def encode(self, texts):
        """Tokenize input texts and move tensors to device."""
        return self.tokenizer(
            texts,
            return_tensors="pt",
            truncation=True,
            padding=True
        ).to(self.device)

    def get_label_from_probs(self, probs):
        """Return label and probability based on model outputs."""
        p_machine = float(probs[0, 1].cpu().item())
        label = "machine" if p_machine >= 0.5 else "human"
        return {"label": label, "probability_machine": p_machine}

    def train(self, batch: list, labels: list):
        self.model.train()
        inputs = self.encode(batch)
        labels_tensor = torch.tensor(labels).to(self.device)

        outputs = self.model(**inputs)
        loss = self.criterion(outputs.logits, labels_tensor)
        loss.backward()
        self.optimizer.step()
        self.optimizer.zero_grad()
        return loss.item()

    def predict(self, seq: str):
        self.model.eval()
        inputs = self.encode([seq])  
        with torch.no_grad():
            outputs = self.model(**inputs)
            probs = torch.softmax(outputs.logits, dim=-1)
        return self.get_label_from_probs(probs) 

    def save(self, path: str):
        import joblib
        joblib.dump(self, path)
        return path

    def load(self, path: str):
        import joblib
        loaded = joblib.load(path)
        self.tokenizer = loaded.tokenizer
        self.model = loaded.model
        self.device = loaded.device
        self.optimizer = loaded.optimizer
        self.criterion = loaded.criterion
        return self
