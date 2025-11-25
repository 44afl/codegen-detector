import torch
from transformers import RobertaTokenizer, RobertaForSequenceClassification
from .service import ModelService

class CodeBERTStrategy(ModelService):
    def __init__(self, model_path="microsoft/codebert-base", device=None):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = RobertaTokenizer.from_pretrained(model_path)
        self.model = RobertaForSequenceClassification.from_pretrained(model_path)
        self.model.to(self.device)
        self.model.eval()

    def train(self, X, y):
        raise NotImplementedError("CodeBERT fine-tuning should be done separately.")

    @torch.no_grad()
    def predict(self, code: str):
        tokens = self.tokenizer(
            code,
            truncation=True,
            padding=True,
            max_length=512,
            return_tensors="pt"
        ).to(self.device)

        outputs = self.model(**tokens)
        probs = torch.softmax(outputs.logits, dim=-1)
        prob_machine = float(probs[0][1].item())  # clasa 1 = machine-generated
        return prob_machine
