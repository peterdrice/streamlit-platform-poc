import pandas as pd
def to_snakecase(name: str) -> str:
    """
    Convert a string into snake_case.

    Parameters:
    name (str): Input string.

    Returns:
    (str): String in snake_case.
    """
    return name.lower().replace(" ", "_")


def to_titlecase(name: str) -> str:
    """
    Convert a string into title case (ex: Hello World).

    Parameters:
    name (str): Input string.

    Returns:
    (str): String in title_case.
    """
    return name.replace("_", " ").title()


def cols_to_snakecase(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert dataframe column names into snake_case by lowercasing all letters and replacing spaces with underscores.

    Parameters:
    df (pd.DataFrame): Input dataframe.

    Returns:
    df (pd.DataFrame): Dataframe with column names in snake_case.
    """
    # Apply this function to each column name
    df.columns = [to_snakecase(col) for col in df.columns]
    return df
