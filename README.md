# Expected Goals (xG) Model

A scikit-learn pipeline that turns [Squawka](https://en.wikipedia.org/wiki/Squawka)
shot-event data into an **expected goals (xG)** model for football, and compares
each team's / player's actual goals against their xG.

Expected goals is a metric that estimates the probability that a given shot
results in a goal, based on features such as shot location, build-up play, game
state and player attributes. Summing the xG of every shot a team takes gives a
measure of how many goals they "should" have scored.

You can read the original write-up (Spanish) here:
[Toma de decisiones en el fútbol usando big data](https://medium.com/@andrebrener/toma-de-decisiones-en-el-f%C3%BAtbol-usando-big-data-41ee82c3466f).

> **Status:** this is a 2016–2017 project kept for reference. See
> [Known limitations](#known-limitations) before trying to run it end to end.

## Getting Started

The scripts target **Python 3**.

### 1. Clone the repo

```bash
git clone https://github.com/andrebrener/expected_goals.git
cd expected_goals
```

### 2. Install the dependencies

```bash
pip install -r requirements.txt
```

### 3. Provide the data

The pipeline expects raw Squawka match HTML files saved under
`data/{competition}/{season}/`. The crawler that produced these files was
removed from the repo (see [Known limitations](#known-limitations)), so this
data must be supplied separately.

## Pipeline / run order

The scripts are standalone and are meant to be run in this order. Each one reads
the output of the previous step from hardcoded relative paths:

1. `match_processing.py` – parse raw match files into per-game / per-player CSVs
   under `data/{competition}/{season}/processed_*` (depends on `dataset.py`).
2. `build_database_season.py` – concatenate processed games/players into
   `database/{competition}/{season}/`.
3. `build_shots_database.py` – extract shot events into
   `shots_database/{competition}/shots_database.csv`.
4. `total_shots_database.py` – merge per-competition shot files into a single
   `shots_database/shots_database.csv`.
5. `shots_analysis.py` – clean / feature-engineer shots into
   `shots_database/train_table_processed.csv`.
6. `xg_model.py` – train a `RandomForestRegressor` (grid search) and pickle it
   to `random_forest.pkl`.
7. `xg_validation.py` – load the model, score the test table and write per-team
   / per-player xG CSVs.
8. `xg_graph.py` – plot actual goals vs. xG.

The `transfermarkt_crawler/` directory contains a separate, best-effort scraper
for Transfermarkt transfer data + Google Trends. It is **unmaintained**:
Transfermarkt's markup has changed since 2017 and `pytrends` no longer supports
the login flow it uses. If you do run it, supply Google credentials via the
`GOOGLE_USERNAME` and `GOOGLE_PASSWORD` environment variables (never hardcode
them).

## Known limitations

- **The data-build pipeline does not run as-is.** `dataset.py` (and therefore
  `match_processing.py`) imports `SquawkaReport` from a `utils.py` module that
  was deleted in an earlier commit (`8249bbe "delete crawler"`) and is **not
  recoverable from this repository**. Steps 1–2 above cannot run until an
  equivalent Squawka parser is supplied. The downstream steps (3–8) only work if
  you already have the intermediate CSVs.
- **`random_forest.pkl` is a large (~67 MB) committed binary.** It is now listed
  in `.gitignore` so it won't be re-added, but it still exists in the repo and
  in git history. Pickled scikit-learn models are tied to a specific library
  version and execute arbitrary code on load, so regenerate it with `xg_model.py`
  rather than trusting the committed file.
- The Squawka data source itself was discontinued, so fresh data cannot be
  collected with the original tooling.

## License

Released under the [MIT License](LICENSE).
