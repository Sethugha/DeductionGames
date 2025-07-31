# 📚 Generator for deduction games based on your favorite books

A **Deduction Game Generator** built with **Python**, featuring a Flask-based REST API and SQLAlchemy for ORM-backed database access. 
The frontend is still primitive  but allows playing.
Currently the frontend is not separated from the backend thus it is at time not necessary to implement CORS.
---

### 🛠️ Technologies Used

* **Backend:** Python, Flask, Flask-SQLAlchemy
* **Frontend:** Vanilla JavaScript, HTML5, CSS3
* **Database:** SQLite

---

### ✨ Features

Text import via copy & paste or file upload.
Should be able to create a deduction game from every story but for texting purposes I used detective short stories which work well.

---

### 🚀 Getting Started

#### Prerequisites

* Python 3.x
* pip / venv
  

#### Installation

```bash
git clone https://github.com/Sethugha/Deductor.git
cd Deductor
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

#### Running the Application

```bash
python3 backend/app.py
```

Frontend files are located in `/static` and served directly via Flask.

---
### Setting Difficulty 

To get a grip on the difficulty settings You might need the next paragraph.
The difficulty is determined by Generation_config as described below: 

The generation_config is a set of parameters that control the behavior of the generation process in Gemini. 
By fine-tuning these parameters, you can influence the quality, diversity, and randomness of the generated content
thus the overall difficulty of the deduction games.
and .

The most important parameters in the generation_config are:

#### *temperature* (Random Factor): 

This parameter controls the randomness of the generated content. 
A higher temperature will result in more diverse content, but it may also be less coherent. 
The temperature parameter is a *value between 0 and 1*, where 0 means deterministic generation
and 1 means maximum randomness. The default value is 0.7, which balances diversity and coherence.

#### *top_p* (Content Diversity):

This parameter controls the diversity of the generated content. 
A higher top_p will result in more diverse content, but it may also be less fluent.
The top_p parameter is a *value between 0 and 1*, where 0 means only the most 
probable token is considered and 1 means all tokens are considered. 
The default value is 0.9, which allows for some diversity while filtering out low-probability tokens.

#### *top_k* (Token/Step):

This parameter controls the number of tokens that are considered at each step of the generation process. 
A higher top_k will result in more fluent content, but it may also be less diverse.
The top_k parameter is a positive integer, where 0 means all tokens are considered
and any positive value means only the top k tokens are considered. 
The default value is 50, which ensures fluency while allowing for some diversity.
    
#### *max_output_tokens* (Max Token):

This parameter controls the maximum number of tokens that will be generated. 
The max_output_tokens parameter is a positive integer, where 0 means no limit 
and any positive value means the generation will stop after that many tokens. 
The default value is 0, which means the generation will continue until the end-of-text token is reached.

The optimal values for these parameters will vary depending on your specific use case. 
For example, if you are generating text for a creative writing task, 
you may want to use a higher temperature to encourage diversity. 
However, if you are generating text for a technical document, 
you may want to use a lower temperature to ensure accuracy.

#### *Some Examples*:

Here are some examples of how the generation_config parameters can be used to achieve specific results:

To generate more *diverse* content, you can increase the *temperature* or *top_p* parameters. 
For example, if you set the temperature to 0.9 and the top_p to 0.95, 
you will get more varied and creative content, but it may also be less coherent and fluent.
    
To generate more *fluent* content, you can increase the top_k parameter. 
For example, if you set the top_k to 100, you will get more fluent and coherent content, 
but it may also be less diverse and creative.
    
To generate a *specific number of tokens*, you can set the max_output_tokens parameter. 
For example, if you set the max_output_tokens to 200, you will get a content that is 200 tokens long,
regardless of the other parameters.

It might be important to experiment with the generation_config parameters to find the optimal settings 
for every case to be able to win the game without beating it on first guess.

### Evaluation
    
Start with the default values and adjust them gradually. You can use the Gemini interface to easily change the parameters and see the results in real time.
Experiment with different values to see how they affect the generated content. You can use the Gemini interface to compare the generated content with different parameter settings and see the differences.
Use evaluation metrics to measure the quality of the generated content and fine-tune the parameters accordingly. You can use the Gemini interface to see the evaluation metrics such as perplexity, diversity, and coherence for the generated content and use them as feedback.
Consider the trade-offs between fluency, diversity, and accuracy when choosing the parameter values. You can use the Gemini interface to see the trade-offs graph that shows how the parameters affect the quality of the generated content and find the optimal balance.
