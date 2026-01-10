"""Recurrence calculator service using python-dateutil rrule."""

from datetime import datetime, timedelta
from typing import Optional

from dateutil import rrule

from ..models.recurrence import EndCondition, PatternType, RecurrencePattern


class RecurrenceCalculator:
    """Calculate next due dates for recurring tasks using rrule."""

    @staticmethod
    def calculate_next_due_date(
        pattern: RecurrencePattern,
        current_due_date: datetime,
    ) -> Optional[datetime]:
        """
        Calculate the next due date based on recurrence pattern.

        Args:
            pattern: Recurrence pattern configuration
            current_due_date: Current task due date to calculate from

        Returns:
            Next due date, or None if recurrence should end
        """
        # Check if recurrence should end
        if not RecurrenceCalculator._should_continue(pattern):
            return None

        # Build rrule based on pattern type
        freq_map = {
            PatternType.DAILY: rrule.DAILY,
            PatternType.WEEKLY: rrule.WEEKLY,
            PatternType.MONTHLY: rrule.MONTHLY,
        }

        freq = freq_map[pattern.pattern_type]

        # Configure rrule parameters
        rrule_kwargs = {
            "freq": freq,
            "interval": pattern.interval,
            "dtstart": current_due_date,
            "count": 2,  # Current + next occurrence
        }

        # Add weekly-specific parameters
        if pattern.pattern_type == PatternType.WEEKLY and pattern.days_of_week:
            # Convert from 0=Monday to rrule format (0=Monday)
            rrule_kwargs["byweekday"] = pattern.days_of_week

        # Add monthly-specific parameters
        if pattern.pattern_type == PatternType.MONTHLY and pattern.day_of_month:
            rrule_kwargs["bymonthday"] = pattern.day_of_month

        # Generate recurrence instances
        rule = rrule.rrule(**rrule_kwargs)
        occurrences = list(rule)

        # Return next occurrence (skip first as it's current)
        if len(occurrences) > 1:
            next_date = occurrences[1]

            # Check against end_date if specified
            if (
                pattern.end_condition == EndCondition.BY_DATE
                and pattern.end_date
                and next_date > pattern.end_date
            ):
                return None

            return next_date

        return None

    @staticmethod
    def _should_continue(pattern: RecurrencePattern) -> bool:
        """
        Check if recurrence should continue creating instances.

        Args:
            pattern: Recurrence pattern to check

        Returns:
            True if should continue, False otherwise
        """
        # NEVER: Always continue
        if pattern.end_condition == EndCondition.NEVER:
            return True

        # AFTER_OCCURRENCES: Check count
        if pattern.end_condition == EndCondition.AFTER_OCCURRENCES:
            if pattern.occurrence_count is None:
                return False
            return pattern.current_occurrence < pattern.occurrence_count

        # BY_DATE: Check end date
        if pattern.end_condition == EndCondition.BY_DATE:
            if pattern.end_date is None:
                return False
            return datetime.utcnow() < pattern.end_date

        return False

    @staticmethod
    def calculate_next_n_dates(
        pattern: RecurrencePattern,
        start_date: datetime,
        count: int = 10,
    ) -> list[datetime]:
        """
        Calculate the next N due dates for preview purposes.

        Args:
            pattern: Recurrence pattern configuration
            start_date: Starting date to calculate from
            count: Number of future dates to generate

        Returns:
            List of future due dates (may be less than count if recurrence ends)
        """
        freq_map = {
            PatternType.DAILY: rrule.DAILY,
            PatternType.WEEKLY: rrule.WEEKLY,
            PatternType.MONTHLY: rrule.MONTHLY,
        }

        freq = freq_map[pattern.pattern_type]

        # Configure rrule parameters
        rrule_kwargs = {
            "freq": freq,
            "interval": pattern.interval,
            "dtstart": start_date,
            "count": count + 1,  # +1 to include start date
        }

        # Add weekly-specific parameters
        if pattern.pattern_type == PatternType.WEEKLY and pattern.days_of_week:
            rrule_kwargs["byweekday"] = pattern.days_of_week

        # Add monthly-specific parameters
        if pattern.pattern_type == PatternType.MONTHLY and pattern.day_of_month:
            rrule_kwargs["bymonthday"] = pattern.day_of_month

        # Add end date constraint if specified
        if pattern.end_condition == EndCondition.BY_DATE and pattern.end_date:
            rrule_kwargs["until"] = pattern.end_date

        # Generate recurrence instances
        rule = rrule.rrule(**rrule_kwargs)
        occurrences = list(rule)[1:]  # Skip first as it's the start date

        # Limit by occurrence count if specified
        if (
            pattern.end_condition == EndCondition.AFTER_OCCURRENCES
            and pattern.occurrence_count
        ):
            remaining = pattern.occurrence_count - pattern.current_occurrence
            occurrences = occurrences[:remaining]

        return occurrences
