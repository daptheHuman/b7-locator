import array
from datetime import timedelta


def add_years_and_months(start_date, years, months=0):
    try:
        # Calculate the total number of months to add
        total_months = int(years * 12) + months
        # Calculate the end date by adding the total months to the start date
        end_date = start_date + timedelta(
            days=total_months * 31  # mean month length
        )

        return end_date
    except ValueError:
        # Handle the case where the resulting date is invalid
        return None  # Or raise an error depending on your requirement


def format_batch_numbers(batch_numbers: array):
    """
    Formats a list of batch numbers into a string with the first and last batch number separated by a hyphen.

    Args:
      batch_numbers: A list of batch numbers.

    Returns:
      A string with the first and last batch number separated by a hyphen, or an empty string if the list is empty.
    """

    if not batch_numbers:
        return ""

    sorted_batch = sorted(batch_numbers)

    if len(sorted_batch) > 1:
        return f"{sorted_batch[0]} - {sorted_batch[-1]}"

    return f"{sorted_batch[-1]}"
