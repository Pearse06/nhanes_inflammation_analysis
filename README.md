# Diet and Inflammation in Young Men: An NHANES Analysis
 
A multiple regression analysis, followed by a random forest model, concerning how different macronutrients correlate with higher or lower levels of inflammation among adult men. The data comes from the NHANES 2015 to 2016 and 2017 to 2020 survey cycles.
 
## Overview
 
Originally, I embarked on this project to answer one question that I thought was quite simple and straightforward: what is the most optimal diet to reduce inflammation in young men? I like to consider myself a dedicated weightlifter, and I have always wondered what would be the best diet for me to eat consistently to support muscle growth. Inflammation gives a lot of information about an individual's health, and having low chronic inflammation on average supports hypertrophy, or in simple terms, muscle growth. It's important to distinguish between temporary and chronic inflammation. Temporary inflammation occurs on a day to day basis, such as when you are sick or right after exercise, while chronic inflammation is the lower, constant level that stays in the background. Controlling the factors I can, such as diet, is critical to improving my muscle growth as much as possible. Before the project, while researching the question, it surprised me that there wasn't a clear consensus on which diet actually achieved this. Some would say it's carnivore, others would say it's eating vegan. Because there was no clear answer to this question, I decided to take matters into my own hands by analyzing CDC health survey data.
 
## Data
 
The data came from the CDC's National Health and Nutrition Examination Survey, or NHANES, a national study that collects health data on thousands of Americans every two years through interviews, physical exams, and lab tests. I chose it because it's one of the few sources where the same people have both a blood test for inflammation and a detailed record of what they ate, and it's free, publicly available, and designed to represent the U.S. population. From it, I used eight types of files across the 2015 to 2016 and 2017 to 2020 cycles: blood test results for C-reactive protein (CRP), a protein the liver releases when there's inflammation in the body; two days of diet records; demographics like age and sex; body measurements like BMI; and questionnaires on sleep, physical activity, and smoking.
 
| File type | 2015 to 2016 | 2017 to 2020 |
| --- | --- | --- |
| CRP blood test | HSCRP_I.xpt | P_HSCRP.xpt |
| Diet, Day 1 | DR1TOT_I.xpt | P_DR1TOT.xpt |
| Diet, Day 2 | DR2TOT_I.xpt | P_DR2TOT.xpt |
| Demographics | DEMO_I.xpt | P_DEMO.xpt |
| Body measurements | BMX_I.xpt | P_BMX.xpt |
| Sleep | SLQ_I.xpt | P_SLQ.xpt |
| Physical activity | PAQ_I.xpt | P_PAQ.xpt |
| Smoking | SMQ_I.xpt | P_SMQ.xpt |
 
All files are free to download from the [NHANES website](https://wwwn.cdc.gov/nchs/nhanes/). They aren't included in this repository because of their size. The one exception is `combined.csv`, the cleaned dataset that `Health.py` creates, which is included so Part 2 can be run directly.
 
## Approach
 
After pulling the data into a Python script, I ran a multiple regression on the relevant factors within the datasets, and I also ran the same multiple regression with the same factors on only young men, so the results would be more applicable to me personally. The first attempt didn't provide many significant results, for what I believe were two reasons. First, the diet information only covered one day for each individual, and second, the sample size was only around 3,000 men, which is potentially not enough to tell whether things like protein or monounsaturated fats have an effect on inflammation. Therefore, I expanded the years I was taking data from, and I filtered to only include men who had two days of eating records, averaging the two days. I did this so it would give a better sense of what the diets of the people I was analyzing actually looked like. I then ran the multiple regression again for both adult men and only young men.
 
## Findings
 
Several findings stood out. First, overall lifestyle mattered much more than any single nutrient. BMI was by far the strongest factor, with a typical heavier man having roughly 70% higher CRP than a typical lighter man. Current smokers had about 27% higher CRP, while men who did vigorous exercise had about 10% lower. For diet, monounsaturated fat was the most consistent finding, linked to about 7% lower CRP per 100 calories among all men and about 16% lower among young men. Starch and protein were also linked to lower CRP among all men, while omega-6 was linked to about 21% higher CRP among young men. Sugar and fish, which looked significant in my first attempt, didn't hold up once I improved the data. After documenting the findings, I displayed the key results with horizontal bar charts.
 
### All men (4,477)
 
![Factors linked to inflammation in all men](crp_factors_chart.png)
 
### Young men aged 18 to 29 (843)
 
![Factors linked to inflammation in young men](crp_factors_chart_young_men.png)
 
Bars to the right are linked to higher CRP, and bars to the left are linked to lower CRP. Each bar is labeled with the amount it represents, and the error bars show 95% confidence intervals.
 
## Limitations
 
- The data concerning the diets of the participants isn't as reliable as it could be, because it was self reported. People aren't always honest about what they eat in a given day, they also tend to underestimate the amount they ate, and it's quite easy to forget things that you ate when attempting to give the report.
- The participants had their BMI measured rather than their body fat. BMI only looks at a person's weight compared to their height, so it can't tell the difference between muscle and fat, which can make muscular people look less healthy than they actually are.
- Each participant was only given one CRP test, rather than multiple, so only taking one test does not paint the whole picture of a person's average inflammation.
- All of the findings uncovered in this project are associations, not causes. The data is a single snapshot rather than a record of people over time, so it can't show what came first. On top of that, some relevant factors, like genetics and stress, weren't measured in the NHANES data at all.
- The multiple regression model holds the underlying assumption that each factor would increase or decrease a person's inflammation by the same percentage for everyone, and would continue at the same rate indefinitely. Neither is likely true.
- Since the regression tests 16 factors, a factor could potentially have passed the 5% cutoff just by chance rather than because it actually has a real link to inflammation.
## Conclusion
 
This project has taught me that the reason there isn't a consensus is that the question is extremely complicated and likely highly individualized, meaning the best diet for one person might not be exactly the best diet for another. I also learned that while the approach you take to analyzing the data is important, understanding the data you're working with, its quality, and how it will help you draw conclusions is just as critical. I saw this firsthand when two findings that looked clear in my first attempt disappeared once I improved the quality of the data. I didn't end up fully answering my question, in part because I couldn't control for genetics, which play a huge role in how the body deals with inflammation. Still, between my analysis and outside research, I think some of these findings are reasonable to apply to my own life. Following this project, I have started trying to get more of my daily calories from monounsaturated fats, starches from whole grains and legumes, and protein, while cutting back on omega-6 fats. If I were to expand on this project, I would add more NHANES cycles to increase the sample size, and I would replace BMI with body fat measurements to better tell whether it's weight itself or higher levels of body fat that drives higher inflammation.
 
## Files
 
| File | What it is |
| --- | --- |
| `Health.py` | Final analysis: combines both cycles, averages two days of diet records, runs both regressions, and creates both charts |
| `Health_v1.py` | First analysis: one cycle with one day of diet records, kept so the original results can be reproduced |
| `crp_factors_chart.png` | Chart of results for all men |
| `crp_factors_chart_young_men.png` | Chart of results for men aged 18 to 29 |
| `Health_Part2.py` | Part 2 analysis: trains a random forest to predict CRP in men, compares three sets of factors, and creates the importance chart |
| `crp_model_importance.png` | Chart of the factors the random forest relied on to predict CRP |
| `combined.csv` | Cleaned dataset that `Health.py` creates, included so Part 2 can be run without downloading the NHANES files |
 
## How to run
 
1. Download the 16 `.xpt` files listed above from the NHANES website and put them in the same folder as `Health.py`.
2. Install the required packages:
```
pip install pandas numpy statsmodels matplotlib
```
3. Run the script:
```
python Health.py
```
 
The script prints the cleaning steps and both regression summaries, then saves both charts as images.
 
## Part 2: How Much of Inflammation Do These Factors Explain?
 
A few weeks after completing my analysis, I began to think about how much variables outside of the dataset actually affect inflammation. This is critical to have an understanding of because having a rough answer to this question would help me get a rough idea of how much of inflammation the factors I chose actually explained. From this thought, I decided it made sense to run a random forest, a machine learning method that allows the coder to use factors to predict values of an outcome. I trained the random forest on 80% of the adult male records and tasked it with predicting the CRP values of the other 20% based on what it had learned from the 80%. I did this in order to see how well the variables I chose could predict inflammation levels, which would give me a very rough gauge on how much outside variables were involved.
 
### Approach
 
I started by establishing the settings for the Random Forest, that being an 80:20 training to testing ratio and 300 decision trees. To put it briefly, a decision tree is basically a very rudimentary machine learning model in its own right, for instance, you train the model and then test it on data it hasn't seen, but a single decision tree can be very statistically unreliable. This is because, due to just random chance, the tree might memorize unuseful patterns known as noise that distort its predictions of the rest of the data. To combat this, that is why we need a random forest of 300 decision trees, so that if some trees memorize noise, the sheer volume of decision trees will balance it out.
 
Before the final Random Forest was tested, through the use of cross validation the models were trained separately 5 times, each time leaving out a different fifth of the training men to check on, and then the scores were averaged. This made sure the results were steady and not a fluke of one particular split.
 
The models I specifically ran through this process were all 16 factors from Part 1 of my analysis, to see how much all of the factors I worked with could explain inflammation, only the diet factors I worked with, in order to get an idea of how much of the differences in inflammation among men diet alone can explain rather than other factors, and finally all of my factors besides diet, to see how well they could predict inflammation without diet, which let me compare it to the full set and see how much diet added.
 
### Results
 
The results of the software showed that the Random Forest, trained on the data within my analysis, found that my factors explained about 20% of the differences in CRP among men it had not seen, which is an R² of 0.197. R² is a score where 0 means the model did no better than guessing the average man's CRP for everyone and 1 means a perfect prediction. Furthermore, the model leaned heavily on BMI for its predictions, with age a distant second. The diet factors on their own scored about 0, and adding them to the other factors only raised the score from 0.182 to 0.197. I believe this is because the differences in CRP among men from things like BMI and age are large compared to the small effects of individual nutrients, so diet alone could not stand out.
 
| Factors used | Cross validated R² (training men) | Test R² (hidden men) |
|---|---|---|
| Diet factors only | -0.001 | -0.007 |
| Age, BMI, sleep, exercise, smoking only | 0.224 | 0.182 |
| All factors | 0.243 | 0.197 |
 
On the hidden men, the random forest's guesses missed by about 1.38 mg/L on average. Guessing 1.48 mg/L, the typical (median) CRP of the training men, for every man would have missed by about 1.56 mg/L.
 
![Factors the random forest relies on to predict CRP in men](crp_model_importance.png)
 
Each bar shows how much the model's score dropped when the values of that factor were randomly shuffled among the hidden men, repeated 20 times and averaged. The longer the bar, the more the model relied on that factor. Bars near zero, including the slightly negative ones, mean the model barely used that factor, and differences that small are just noise.
 
Moving from this, it starts to get kind of murky in regards to whether or not other factors within the analysis actually explained inflammation, and I believe this to be the case for two reasons. First, due to the nature of machine learning, factors that heavily associate with the outcome have a tendency to be favored by the models and essentially tune out the subtle differences from other factors. Second, due to the models only being trained on a few thousand records, I think it is possible that if the models were trained on more records, those subtle differences might become more apparent, as it gains more knowledge on how to make more accurate predictions due to more training data.
 
### Limitations
 
- The data comes from a survey, so the diets were self reported, and each man only had one CRP test.
- A random forest shows what predicts CRP, not what causes it, so the 20% is only a rough estimate of what my factors can predict, not a precise measure of cause.
- Shuffling one factor at a time can make closely related factors, like the diet factors, look less important than they actually are.
- The results come from one random split of the men, so a different split would give a slightly different number.
### Conclusion
 
Overall, this part of my greater project sufficiently answered my question, that being that about 20% of the differences in inflammation among men can be explained by my factors from my first analysis, although it is important to keep the limitations above in mind. In addition, I found that both the process and results strengthened my understanding of the foundations of machine learning along with a better understanding of the data I'm working with. This is consistent with my underlying assumption that things outside of my analysis such as genetics heavily affect inflammation. Obviously, even though the diet factors did not explain much of CRP among men as a whole, it is critical to be aware that, after taking into account things like genetics and weight, diet is one of the few things an individual can control to potentially lower inflammation compared to people who are overall similar to them, although these are associations and not proof of cause.
 
### How to run Part 2
 
1. Make sure `combined.csv` is in the same folder as `Health_Part2.py`. It is included in this repository, and `Health.py` also creates it.
2. Install scikit-learn:
```
pip install scikit-learn
```
3. Run the script:
```
python Health_Part2.py
```
 
The script prints the results table and saves the chart as `crp_model_importance.png`.
 
## Tools
 
Python, pandas, NumPy, statsmodels, scikit-learn, matplotlib
 
