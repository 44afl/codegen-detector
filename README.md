# 🧠 SemEval 2026 Task 13: Detecting Machine-Generated Code

**Team 6 - UAIC Faculty of Computer Science (FII)**  
Professor: Adrian Iftene · Coordinator: Diana Trandabăț  
GitHub: [codegen-detector](https://github.com/44afl/codegen-detector) · Trello: [bit.ly/472lMw0](http://bit.ly/472lMw0)

---

## 📘 Overview
Project developed for **SemEval 2026 Task 13**, aiming to detect **machine-generated code** across multiple programming languages and LLM families.  
Our system combines **CodeBERT-based transformers** with **classical ML models** (SVM, AdaBoost) to classify code as *human*, *AI-generated*, or *hybrid*.

---

## 🎯 Objectives
- Detect AI-generated vs human-written code with high accuracy.  
- Identify authorship across LLM families (Qwen, Meta-LLaMA, etc.).  
- Support multiple languages (Python, C++, Java).  
- Provide evaluation metrics (Accuracy, F1, AUC).

---

## 🧱 Architecture
| Component | Description |
|------------|--------------|
| **Frontend (React)** | Upload interface and result visualization |
| **Backend (Flask)** | API for model execution |
| **Preprocessing Module** | Tokenization & feature extraction |
| **Model Pipeline** | SVM, AdaBoost, LSTM, Transformer |
| **Evaluator** | Accuracy, F1, AUC, confusion matrix |
| **Database (MariaDB)** | Store results and metadata |

---

## 🧩 Design Patterns
- **Singleton** – configuration management  
- **Factory Method** – dataset/code loader  
- **Template Method** – feature extraction steps  
- **Strategy** – interchangeable ML models  
- **Builder + Observer** – training progress tracking  
- **Decorator** – extend feature extraction dynamically  
- **Facade** – unify the end-to-end prediction pipeline  

---

## ⚙️ Technologies
**Languages:** Python, JavaScript  
**Frameworks:** Flask, React, PyTorch, Hugging Face, Scikit-learn  
**Database:** MariaDB  
**Collaboration:** GitHub & Trello

---

## 📊 Datasets & Models
- **Datasets:** SemEval Task 13, CodeNet, CodeSearchNet, AIGCode, Kaggle  
- **Models:** CodeBERT, CodeT5, DetectGPT, SVM, AdaBoost  
- **Metrics:** Accuracy, F1, AUC, FPR/FNR


## 🧾 License
Academic research use only. Based on the [SemEval 2026 Task 13](https://github.com/mbzuai-nlp/SemEval-2026-Task13) dataset and challenge.

