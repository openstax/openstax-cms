def school_year_base_year(date):
    """School years roll over on July 1; the base year is the year the school year starts."""
    if date.month < 7:
        return date.year - 1
    return date.year
