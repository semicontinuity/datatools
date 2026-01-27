#!/usr/bin/env python3
"""
Travel Calculator - 90/180 Visa Rule Validator

This tool validates travel logs against the 90/180 visa rule, which states that
non-EU citizens can stay in the Schengen area for a maximum of 90 days within
any 180-day period.

Usage:
    python calc.py < travel_log.txt
    python calc.py --now 01.02.2026 < travel_log.txt

Input Format:
    Each line represents a border crossing with format:
    [date] [direction] [country] [optional: page number]
    
    Where:
    - date: DD.MM.YY format
    - direction: '>' for entry, '<' for exit
    - country: 2-letter country code (RU, TR, CH, BG, etc.)
    - page: optional passport page number (e.g., p24)
    
    Lines starting with whitespace are ignored (comments).

Country Rules:
    - RU: No limits (home country)
    - TR: 90/180 rule, but first stay limited to 60 days max
    - Others: Standard 90/180 rule

Example Input:
    27.06.25 < RU
    27.06.25 > TR       p24
    27.06.25 < TR       p25
    27.06.25 > CH
    
    04.07.25 < CH
    04.07.25 > TR       p26

The tool will:
1. Parse the travel log
2. Calculate stay durations in each country
3. Validate against visa rules
4. Report any inconsistencies or missing records
5. Provide advice on allowed stay duration

Note: The date mentioned counts as a stay day in both countries during transit.
"""

import sys
import re
import argparse
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional, NamedTuple
from collections import defaultdict


class TravelEntry(NamedTuple):
    """Represents a single travel log entry."""
    date: datetime
    direction: str  # '>' for entry, '<' for exit
    country: str
    page: Optional[str] = None


class CountryStay(NamedTuple):
    """Represents a stay period in a country."""
    country: str
    entry_date: datetime
    exit_date: Optional[datetime]
    days: int


class TravelCalculator:
    """Main calculator for travel visa rule validation."""
    
    def __init__(self, now_date: Optional[datetime] = None):
        self.entries: List[TravelEntry] = []
        self.stays: List[CountryStay] = []
        self.inconsistencies: List[str] = []
        self.now_date = now_date or datetime.now()
    
    def parse_date(self, date_str: str) -> datetime:
        """Parse date string in DD.MM.YY format."""
        try:
            return datetime.strptime(date_str, "%d.%m.%y")
        except ValueError:
            raise ValueError(f"Invalid date format: {date_str}. Expected DD.MM.YY")
    
    def parse_line(self, line: str) -> Optional[TravelEntry]:
        """Parse a single line from the travel log."""
        original_line = line
        line = line.strip()
        
        # Skip empty lines and comments (lines starting with whitespace in original)
        if not line or original_line.startswith(' '):
            return None
        
        # Pattern: date direction country [optional: page or ?]
        pattern = r'^(\d{2}\.\d{2}\.\d{2})\s*([<>])\s*([A-Z]{2})(?:\s+([p\d]+|\?))?'
        match = re.match(pattern, line)
        
        if not match:
            self.inconsistencies.append(f"Invalid line format: {line}")
            return None
        
        date_str, direction, country, page = match.groups()
        date = self.parse_date(date_str)
        
        return TravelEntry(date, direction, country, page)
    
    def parse_log(self, log_lines: List[str]) -> None:
        """Parse the entire travel log."""
        for line_num, line in enumerate(log_lines, 1):
            try:
                entry = self.parse_line(line)
                if entry:
                    self.entries.append(entry)
            except ValueError as e:
                self.inconsistencies.append(f"Line {line_num}: {e}")
    
    def calculate_stays(self) -> None:
        """Calculate stay periods from travel entries."""
        # Sort all entries by date to process chronologically
        sorted_entries = sorted(self.entries, key=lambda x: x.date)
        
        # Track current location and entry dates
        current_country = None
        entry_date = None
        
        for entry in sorted_entries:
            if entry.direction == '>':  # Entry into country
                if current_country is not None:
                    # We were in another country, this is inconsistent
                    self.inconsistencies.append(
                        f"Entry to {entry.country} on {entry.date.strftime('%d.%m.%y')} "
                        f"while already in {current_country} (missing exit record)"
                    )
                    # Create stay for previous country (incomplete)
                    if entry_date and current_country:
                        days = (entry.date - entry_date).days
                        if days > 0:
                            stay = CountryStay(current_country, entry_date, entry.date, days)
                            self.stays.append(stay)
                
                current_country = entry.country
                entry_date = entry.date
                
            elif entry.direction == '<':  # Exit from country
                if current_country != entry.country:
                    if current_country is None:
                        self.inconsistencies.append(
                            f"Exit from {entry.country} on {entry.date.strftime('%d.%m.%y')} "
                            f"without corresponding entry"
                        )
                    else:
                        self.inconsistencies.append(
                            f"Exit from {entry.country} on {entry.date.strftime('%d.%m.%y')} "
                            f"but currently in {current_country}"
                        )
                    continue
                
                # Valid exit - create stay record
                if entry_date and current_country:
                    days = (entry.date - entry_date).days + 1  # Include both days
                    if days > 0:
                        stay = CountryStay(current_country, entry_date, entry.date, days)
                        self.stays.append(stay)
                
                current_country = None
                entry_date = None
        
        # Handle case where still in a country
        if current_country and entry_date:
            days = (self.now_date - entry_date).days + 1
            stay = CountryStay(current_country, entry_date, None, days)
            self.stays.append(stay)
            # Don't report as inconsistency - user is currently staying there
            # Visa violations will be caught in validation phase
    
    def get_days_in_period(self, country: str, end_date: datetime, days_back: int = 180) -> int:
        """Calculate total days spent in a country within the last N days."""
        start_date = end_date - timedelta(days=days_back - 1)
        total_days = 0
        
        for stay in self.stays:
            if stay.country != country:
                continue
            
            # Check if stay overlaps with the period
            stay_start = max(stay.entry_date, start_date)
            stay_end = min(stay.exit_date or self.now_date, end_date)
            
            if stay_start <= stay_end:
                overlap_days = (stay_end - stay_start).days + 1
                total_days += overlap_days
        
        return total_days
    
    def validate_turkey_rule(self) -> List[str]:
        """Validate Turkey-specific rules (90/180 + first stay max 60 days)."""
        warnings = []
        turkey_stays = [s for s in self.stays if s.country == 'TR']
        
        if not turkey_stays:
            return warnings
        
        # Check first stay limit (60 days)
        first_stay = min(turkey_stays, key=lambda x: x.entry_date)
        if first_stay.days > 60:
            warnings.append(
                f"Turkey first stay violation: {first_stay.days} days "
                f"(max 60 days allowed for first visit)"
            )
        
        # Check 90/180 rule
        for stay in turkey_stays:
            check_date = stay.exit_date or self.now_date
            days_in_180 = self.get_days_in_period('TR', check_date, 180)
            
            if days_in_180 > 90:
                period_start = check_date - timedelta(days=179)
                warnings.append(
                    f"Turkey 90/180 rule violation: {days_in_180} days in 180-day period "
                    f"from {period_start.strftime('%d.%m.%y')} to {check_date.strftime('%d.%m.%y')}"
                )
        
        return warnings
    
    def validate_schengen_rule(self, country: str) -> List[str]:
        """Validate 90/180 rule for Schengen countries."""
        warnings = []
        country_stays = [s for s in self.stays if s.country == country]
        
        for stay in country_stays:
            check_date = stay.exit_date or self.now_date
            days_in_180 = self.get_days_in_period(country, check_date, 180)
            
            if days_in_180 > 90:
                period_start = check_date - timedelta(days=179)
                warnings.append(
                    f"{country} 90/180 rule violation: {days_in_180} days in 180-day period "
                    f"from {period_start.strftime('%d.%m.%y')} to {check_date.strftime('%d.%m.%y')}"
                )
        
        return warnings
    
    def get_remaining_days(self, country: str) -> Optional[int]:
        """Calculate remaining allowed days in a country. Returns None for unlimited."""
        if country == 'RU':
            return None  # No limits for Russia
        
        days_used = self.get_days_in_period(country, self.now_date, 180)
        return max(0, 90 - days_used)
    
    def get_next_allowed_entry_date(self, country: str) -> Optional[datetime]:
        """Calculate when entry to country is allowed again after 180-day reset."""
        if country == 'RU':
            return None  # No limits for Russia
        
        country_stays = [s for s in self.stays if s.country == country]
        if not country_stays:
            return None
        
        # Find the earliest stay that contributes to current 180-day period
        earliest_relevant_stay = None
        
        for stay in country_stays:
            # Check if this stay overlaps with current 180-day period
            period_start = self.now_date - timedelta(days=179)
            stay_start = max(stay.entry_date, period_start)
            stay_end = min(stay.exit_date or self.now_date, self.now_date)
            
            if stay_start <= stay_end:
                if earliest_relevant_stay is None or stay.entry_date < earliest_relevant_stay.entry_date:
                    earliest_relevant_stay = stay
        
        if earliest_relevant_stay:
            # Entry allowed 180 days after the start of earliest relevant stay
            return earliest_relevant_stay.entry_date + timedelta(days=180)
        
        return None
    
    def generate_report(self) -> str:
        """Generate a comprehensive travel report."""
        report = []
        report.append("=== TRAVEL CALCULATOR REPORT ===\n")
        
        # Inconsistencies
        if self.inconsistencies:
            report.append("⚠️  INCONSISTENCIES FOUND:")
            for issue in self.inconsistencies:
                report.append(f"   • {issue}")
            report.append("")
        
        # Stays summary
        report.append("📍 STAYS SUMMARY:")
        countries = set(stay.country for stay in self.stays)
        
        for country in sorted(countries):
            country_stays = [s for s in self.stays if s.country == country]
            total_days = sum(s.days for s in country_stays)
            
            report.append(f"   {country}: {len(country_stays)} stays, {total_days} total days")
            
            for stay in sorted(country_stays, key=lambda x: x.entry_date):
                exit_str = stay.exit_date.strftime('%d.%m.%y') if stay.exit_date else "ongoing"
                report.append(
                    f"      {stay.entry_date.strftime('%d.%m.%y')} - {exit_str}: {stay.days} days"
                )
        
        report.append("")
        
        # Visa rule validation
        report.append("🛂 VISA RULE VALIDATION:")
        
        all_warnings = []
        
        for country in countries:
            if country == 'RU':
                continue  # No limits for Russia
            elif country == 'TR':
                all_warnings.extend(self.validate_turkey_rule())
            else:
                all_warnings.extend(self.validate_schengen_rule(country))
        
        if all_warnings:
            for warning in all_warnings:
                report.append(f"   ❌ {warning}")
        else:
            report.append("   ✅ No visa rule violations detected")
        
        report.append("")
        
        # Remaining days advice
        report.append("📅 REMAINING ALLOWED DAYS:")
        for country in sorted(countries):
            remaining = self.get_remaining_days(country)
            if remaining is None:
                report.append(f"   {country}: Unlimited (home country)")
            elif remaining == 0:
                next_entry_date = self.get_next_allowed_entry_date(country)
                if next_entry_date:
                    report.append(f"   {country}: 0 days (entry allowed again from {next_entry_date.strftime('%d.%m.%y')})")
                else:
                    report.append(f"   {country}: 0 days (must wait for 180-day period to reset)")
            else:
                report.append(f"   {country}: {remaining} days in current 180-day period")
        
        return "\n".join(report)


def main():
    """Main function to process travel log from stdin."""
    try:
        # Parse command line arguments
        parser = argparse.ArgumentParser(description='Travel Calculator - 90/180 Visa Rule Validator')
        parser.add_argument('--now', type=str, help='Current date in DD.MM.YYYY format (default: today)')
        args = parser.parse_args()
        
        # Parse the now date if provided
        now_date = None
        if args.now:
            try:
                now_date = datetime.strptime(args.now, "%d.%m.%Y")
            except ValueError:
                print(f"Error: Invalid date format '{args.now}'. Expected DD.MM.YYYY", file=sys.stderr)
                sys.exit(1)
        
        # Read input from stdin
        log_lines = sys.stdin.readlines()
        
        # Create calculator and process log
        calculator = TravelCalculator(now_date)
        calculator.parse_log(log_lines)
        calculator.calculate_stays()
        
        # Generate and print report
        report = calculator.generate_report()
        print(report)
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
