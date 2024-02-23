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
