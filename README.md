# FDA - Health tracker Data Analysis

Comparing sleep, recovery, and stress metrics between a **high exercise** week and a **low exercise** week using your data.

## Setup

```bash
uv sync
```

## Usage

```bash
uv run python main.py
```

This runs each person's analysis and saves graphs to `graphs/<name>/`.

## Project Structure

```
main.py              # Entry point — calls each person's run()
vansh.py             # Vansh's analysis module
pepijn.py            # Pepijn's analysis module (TODO)
ruben.py             # Ruben's analysis module (TODO)
graphs/
  vansh/             # Vansh's output graphs
  pepijn/            # Pepijn's output graphs
  ruben/             # Ruben's output graphs
Data .../            # Raw CSV exports
pyproject.toml       # Dependencies
```

## Adding Your Analysis

1. Create `<yourname>.py` in the project root
2. Put your CSV export folder in the repo
3. Expose a `run()` function that loads data, generates graphs, and saves to `graphs/<yourname>/`
4. Import and call it from `main.py`:
   ```python
   import yourname
   yourname.run()
   ```

## Dependencies

- pandas
- matplotlib
- seaborn