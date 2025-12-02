# Rugby Dominance Analysis 🏉

This project analyzes more than a century of international rugby match results to understand which countries have consistently dominated the sport.

## Project Goal

The goal of this analysis is to answer a simple question:

> Which countries have been the most dominant in international rugby?

To do that, the notebook evaluates teams using four key metrics:

- **Win percentage** – how often each nation wins.
- **Average point margin per match** – how convincingly they win.
- **Defensive strength** – average points allowed per match (lower is better).
- **Rugby World Cup titles** – performance on the sport’s biggest stage.

These metrics are combined into a single **Dominance Score** that ranks the top international rugby nations.

## What This Repo Contains

- `Rugby_Dominance.ipynb`  
  A Google Colab–friendly Jupyter notebook that:
  - Loads and cleans historical international rugby results  
  - Calculates win %, margins, defensive stats, and World Cup success  
  - Builds a combined Dominance Score with adjustable weights  
  - Generates charts and auto-written text summaries from the data  

## How to View the Notebook

1. Click on `Rugby_Dominance.ipynb` in this repository.
2. If GitHub’s viewer has trouble loading, you can:
   - Download the notebook and open it in [Google Colab](https://colab.research.google.com), or  
   - Use [nbviewer](https://nbviewer.org) to render it.

## Tools & Technologies

- Python  
- pandas  
- NumPy  
- Matplotlib  
- Google Colab  
- Jupyter Notebook (`.ipynb`)

## Author

Created by **Mario R. Negron** as part of a growing data and AI portfolio focused on sports analytics and quantitative thinking.
