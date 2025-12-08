from data.dataset import Dataset
from models.svm import SVMModel
from training.trainer import Trainer
from events.observer import ConsoleProgressObserver, LogProgressObserver

if __name__ == "__main__":
    dataset = Dataset.from_parquet("data/task_a_trial.parquet")

    trainer = Trainer()

    trainer.attach(ConsoleProgressObserver())
    trainer.attach(LogProgressObserver())

    model, results = (
        trainer.prepareData(dataset)
        .setModel(SVMModel())
        .initializeModel()
        .fitModel()
        .evaluateModel()
        .build()
    )

    model.save("data/svm_model.pkl")

    print("[FINAL RESULTS SVM]", results)
