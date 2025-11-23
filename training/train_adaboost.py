from data.dataset import Dataset
from models.adaboost import AdaBoostStrategy
from training.trainer import Trainer
from events.observer import ConsoleProgressObserver, LogProgressObserver

if __name__ == "__main__":
    dataset = Dataset.from_parquet("data/task_a/task_a_training_set_1.parquet")

    trainer = Trainer()

    
    trainer.attach(ConsoleProgressObserver())
    trainer.attach(LogProgressObserver())

    model, results = (
        trainer
        .prepareData(dataset)
        .setModel(AdaBoostStrategy())
        .initializeModel()
        .fitModel()
        .evaluateModel()
        .build()
    )

    print("[FINAL RESULTS]", results)
