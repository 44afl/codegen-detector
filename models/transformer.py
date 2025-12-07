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

    def train(self, batch: list, labels: list):
        self.model.train()
        inputs = self.tokenizer(
            batch, padding=True, truncation=True, return_tensors="pt"
        ).to(self.device)
        labels_tensor = torch.tensor(labels).to(self.device)

        outputs = self.model(**inputs)
        loss = self.criterion(outputs.logits, labels_tensor)
        loss.backward()
        self.optimizer.step()
        self.optimizer.zero_grad()
        return loss.item()

    def predict(self, seq: str) -> str:
        self.model.eval()
        inputs = self.tokenizer(seq, return_tensors="pt", truncation=True, padding=True).to(self.device)
        with torch.no_grad():
            outputs = self.model(**inputs)
        pred = torch.argmax(outputs.logits, dim=-1).item()
        return "human" if pred == 0 else "AI"