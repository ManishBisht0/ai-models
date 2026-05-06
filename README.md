# 🚀 GenAI Investor Intelligence & Content Generation System

------------------------------------------------------------------------
## 📌 Overview

An end-to-end **Generative AI system** that transforms structured
investment data into:

✨ Investor Biographies\
✨ Investor Theses\
✨ Company Profiles\
✨ Funding-Based Blogs

------------------------------------------------------------------------

## 🧠 Architecture

``` mermaid
graph TD
A[Azure Cosmos DB] --> B[Data Processing]
B --> C[Rule-Based Templates]
C --> D[Prompt Engineering]
D --> E[LLM - Mistral 7B]
E --> F[Final Output]
```

------------------------------------------------------------------------

## ⚙️ Tech Stack

  Category       Tools
  -------------- -------------------
  🧠 LLM         Mistral 7B (GPTQ)
  ⚙️ Framework   Transformers
  ☁️ Database    Azure Cosmos DB
  🐍 Language    Python
  📊 Data        Pandas, NumPy

------------------------------------------------------------------------

## 📂 Project Structure

    .
    ├── model_1_article_generation.py
    ├── model_2_investor_bio_pipeline.py
    ├── model_3_investor_thesis_generator.py
    ├── requirements.txt
    └── README.md

------------------------------------------------------------------------

## 🧠 Modules

### 🔹 Article Generator

-   Intro, summaries, outro generation

### 🔹 Investor Bio Pipeline

-   Data processing + template generation + LLM refinement

### 🔹 Investor Thesis Generator

-   Investor summary, thesis, and title generation

------------------------------------------------------------------------

## 🧪 Sample Output

### Investor Bio

    XYZ Ventures invests in fintech and SaaS sectors...

### Investor Thesis

    Best suited for early-stage scalable startups...

------------------------------------------------------------------------


------------------------------------------------------------------------

## 📊 Highlights

✅ End-to-end GenAI pipeline\
✅ Hybrid system (Data + Rules + LLM)\
✅ Scalable architecture\
✅ Optimized inference (GPTQ)

------------------------------------------------------------------------

## ⚠️ Disclaimer

This project is for demonstration purposes only.

------------------------------------------------------------------------

## 👨‍💻 Author

Manish Bisht
