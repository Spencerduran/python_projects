import numpy as np
import pandas as pd


def format_csv_percentages(input_file: str, output_file: str, round_digits: int = 1):
    """
    Read a CSV, detect numeric columns that look like percentages,
    and format them with % symbol.

    Args:
        input_file: Path to input CSV
        output_file: Path to output CSV
        round_digits: Number of decimal places for rounding
    """
    # Read CSV
    df = pd.read_csv(input_file)

    # Function to detect if a column looks like percentages
    def is_percentage_column(series):
        if not np.issubdtype(series.dtype, np.number):
            return False
        # Check if values are typically between 0 and 100
        return (series.dropna() <= 100).all() and (series.dropna() >= 0).all()

    # Process each column
    for column in df.columns:
        if is_percentage_column(df[column]):
            # Format the percentage values
            df[column] = df[column].round(round_digits).astype(str) + "%"
            print(f"Formatted column as percentage: {column}")
        else:
            print(f"Left as-is: {column}")

    # Save formatted CSV
    df.to_csv(output_file, index=False)
    print(f"\nSaved formatted data to: {output_file}")


# Example usage
if __name__ == "__main__":
    input_file = "~/Code_Repos/quant-futures-analytics-py/TheStrat/sss50_percent_stats/retracement_analysis_results.csv"
    output_file = "~/Code_Repos/quant-futures-analytics-py/TheStrat/sss50_percent_stats/retracement_analysis_resultsFMT.csv"
    format_csv_percentages(input_file, output_file)
