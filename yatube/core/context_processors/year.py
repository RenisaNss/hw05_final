from datetime import date


def year(request):
    """Добавляет переменную с текущим годом."""
    date_year = date.today().year
    return {
        'year': date_year,
    }
