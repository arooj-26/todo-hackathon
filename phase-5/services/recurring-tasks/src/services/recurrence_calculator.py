"""Recurrence calculator service using python-dateutil rrule."""

from datetime import datetime
from typing import Optional

from dateutil import rrule


class RecurrenceCalculator:
    """Calculate next due dates for recurring tasks using rrule."""

    @staticmethod
    def calculate_next_due_date(
        pattern_type: str,
        interval: int,
        current_due_date: datetime,
        days_of_week: Optional[list[int]] = None,
        day_of_month: Optional[int] = None,
        end_condition: str = "never",
        end_date: Optional[datetime] = None,
        occurrence_count: Optional[int] = None,
        current_occurrence: int = 0,
    ) -> Optional[datetime]:
        """
        Calculate the next due date based on recurrence pattern.

        Args:
            pattern_type: Type of recurrence (daily, weekly, monthly)
            interval: Repeat every N days/weeks/months
            current_due_date: Current task due date to calculate from
            days_of_week: Days of week for weekly pattern (0=Monday, 6=Sunday)
            day_of_month: Day of month for monthly pattern
            end_condition: When to stop (never, after_occurrences, by_date)
            end_date: End date for by_date condition
            occurrence_count: Max occurrences for after_occurrences condition
            current_occurrence: Current occurrence number

        Returns:
            Next due date, or None if recurrence should end
        """
        # Check if recurrence should end
        if not RecurrenceCalculator._should_continue(
            end_condition=end_condition,
            end_date=end_date,
            occurrence_count=occurrence_count,
            current_occurrence=current_occurrence,
        ):
            return None

        # Build rrule based on pattern type
        freq_map = {
            "daily": rrule.DAILY,
            "weekly": rrule.WEEKLY,
            "monthly": rrule.MONTHLY,
        }

        freq = freq_map[pattern_type]

        # Configure rrule parameters
        rrule_kwargs = {
            "freq": freq,
            "interval": interval,
            "dtstart": current_due_date,
            "count": 2,  # Current + next occurrence
        }

        # Add weekly-specific parameters
        if pattern_type == "weekly" and days_of_week:
            # Convert from 0=Monday to rrule format (0=Monday)
            rrule_kwargs["byweekday"] = days_of_week

        # Add monthly-specific parameters
        if pattern_type == "monthly" and day_of_month:
            rrule_kwargs["bymonthday"] = day_of_month

        # Generate recurrence instances
        rule = rrule.rrule(**rrule_kwargs)
        occurrences = list(rule)

        # Return next occurrence (skip first as it's current)
        if len(occurrences) > 1:
            next_date = occurrences[1]

            # Check against end_date if specified
            if end_condition == "by_date" and end_date and next_date > end_date:
                return None

            return next_date

        return None

    @staticmethod
    def _should_continue(
        end_condition: str,
        end_date: Optional[datetime],
        occurrence_count: Optional[int],
        current_occurrence: int,
    ) -> bool:
        """
        Check if recurrence should continue creating instances.

        Args:
            end_condition: When to stop (never, after_occurrences, by_date)
            end_date: End date for by_date condition
            occurrence_count: Max occurrences for after_occurrences condition
            current_occurrence: Current occurrence number

        Returns:
            True if should continue, False otherwise
        """
        # NEVER: Always continue
        if end_condition == "never":
            return True

        # AFTER_OCCURRENCES: Check count
        if end_condition == "after_occurrences":
            if occurrence_count is None:
                return False
            return current_occurrence < occurrence_count

        # BY_DATE: Check end date
        if end_condition == "by_date":
            if end_date is None:
                return False
            return datetime.utcnow() < end_date

        return False
