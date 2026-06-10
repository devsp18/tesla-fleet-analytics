# Tesla Marketing Fleet Analytics

**Which demo drives actually turn into Teslas, and which markets are leaving conversions on the table?**

Tesla's marketing fleet runs demo drives across dozens of markets in the Americas. Every one of those drives is a chance to turn someone curious into someone who buys. After reading how Tesla's North America Business Operations and Analytics team works, I wanted to understand what actually separates a demo drive that converts from one that doesn't, and where the fleet might be underperforming without anyone flagging it. So I built an end-to-end analytics system to dig into that question.

**Live dashboard:** https://tesla-fleet-satyam.streamlit.app/
**Tableau view:** _(link coming once published)_

---

## A note on the data

There is no public dataset of real Tesla demo-drive records, so I simulated 15,000 of them. The simulation is not random noise. It is grounded in real Tesla model pricing, published automotive test-drive-to-purchase conversion benchmarks (roughly 15 to 28 percent), real seasonality in car buying, and documented EV buyer segments. The point of the project is the analytics framework and the way it surfaces decisions, not a claim about Tesla's actual numbers. Everything here would plug into real internal data the moment it was available.

---

## What I found

A few things in the modeled fleet stood out:

- **Conversion ranges widely by market.** Portland, OR leads at 26.3 percent while Las Vegas, NV trails at 11.9 percent — a 14-point gap. That kind of spread is exactly what a fleet team would want flagged automatically rather than discovered by accident.
- **Weekends convert better, and it holds up statistically.** Weekend demos convert about 19 percent higher than weekday demos, significant at p < 0.001 on a two-sample t-test. If that pattern held in real data, it would argue for weighting weekend fleet availability.
- **Longer drives correlate with conversion.** Customers who converted spent measurably longer behind the wheel, and the correlation is statistically significant. Drive duration turned out to be one of the stronger predictors in the model.
- **About $8.9M in addressable revenue.** If the four underperforming markets reached the fleet's 19.7 percent average, the modeled incremental revenue is roughly $8.9M — a way to frame the size of the opportunity, not a forecast.
- **Segment and duration drive conversion most.** A logistic regression (Pseudo R² = 0.155) points to customer segment and drive duration as the strongest signals, with Tech Early Adopter and Fleet/Business buyers showing the highest odds of converting.

---

## What's in here

The project mirrors the kinds of skills the role calls for — SQL, Python, statistics, dashboards, and Excel reporting.

- **Data pipeline** (`src/data/`) — generates 15,000 demo-drive records, writes them to a SQLite database with analytical views, and exports clean CSVs.
- **Statistical analysis** (`src/analysis/`) — market/model/segment breakdowns, weekend vs. weekday t-tests, Pearson correlation on drive duration, underperforming-market detection, and a logistic regression on conversion.
- **Streamlit dashboard** (`src/dashboard/`) — an interactive five-tab dashboard (market performance, vehicle analytics, customer segments, trends and timing, and the statistical model) with live filters. This is what's deployed at the link above.
- **Excel report** (`src/excel/`) — a six-sheet workbook with an executive overview, pivot tables, a model-vs-region heat map, segment analysis, a raw-data sample, and VBA macro instructions.
- **Tableau** — a separate executive view published to Tableau Public _(link above once live)_.

---

## Tech stack

Python (pandas, NumPy, SciPy, statsmodels), SQL (SQLite), Streamlit, Plotly, openpyxl, and Tableau Public.

---

## Running it locally

```bash
git clone https://github.com/devsp18/tesla-fleet-analytics.git
cd tesla-fleet-analytics
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# regenerate the dataset (optional — data is already committed)
python src/data/generate_data.py

# run the analysis
python src/analysis/fleet_analysis.py

# launch the dashboard
streamlit run src/dashboard/app.py
```

---

## What I'd build next

If this were running on real fleet data, the next steps I'd want are: a forecasting layer that flags markets likely to dip before they do, an automated weekly report that lands in stakeholders' inboxes, and a cost-per-conversion view so reallocation decisions weigh spend, not just conversion rate.