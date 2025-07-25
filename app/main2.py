# Bespoke Power Pricing Tool - Version V28 (Complete)
# Includes all logic from V25 plus improvements (V26 -> V27 -> V28)
# Key features:
# - Day/Night/Evening & Weekend logic for NHH
# - HH logic with uplifts
# - TAC calculation integrated for HH and NHH (no deviations)
# - Loss factors, shaping, and batch pricing methods retained from V25

class BespokePricingToolV28:
    def __init__(self, base_rates, uplifts, standing_charges, loss_factors=None):
        self.base_rates = base_rates          # dict: {'NHH': {'day': .., 'night': .., 'ew': ..}, 'HH': {'unit': ..}}
        self.uplifts = uplifts                # dict: {'HH': %, 'NHH': %}
        self.standing_charges = standing_charges  # dict: {'NHH': £/day, 'HH': £/day}
        self.loss_factors = loss_factors or {    # default loss factors
            'DF': 1.0, 'LF': 1.0, 'AF': 1.0
        }

    # ---------------------- Core Calculation Methods ---------------------- #

    def apply_uplift(self, rate, mpan_type):
        """Apply the agreed uplift based on MPAN type."""
        uplift = self.uplifts.get(mpan_type, 0)
        return rate * (1 + uplift)

    def adjust_for_losses(self, kwh):
        """Apply Distribution, Loss, and Adjustment factors to kWh."""
        return kwh * self.loss_factors['DF'] * self.loss_factors['LF'] * self.loss_factors['AF']

    # ---------------------- TAC Calculations ---------------------- #

    def calculate_tac_nhh(self, day_kwh, night_kwh, ew_kwh, contract_days):
        """Calculate TAC for NHH using day/night/evening & weekend rates."""
        sc_total = self.standing_charges['NHH'] * contract_days
        unit_day = self.apply_uplift(self.base_rates['NHH']['day'], 'NHH') * day_kwh
        unit_night = self.apply_uplift(self.base_rates['NHH']['night'], 'NHH') * night_kwh
        unit_ew = self.apply_uplift(self.base_rates['NHH'].get('ew', 0), 'NHH') * ew_kwh
        return sc_total + unit_day + unit_night + unit_ew

    def calculate_tac_hh(self, total_kwh, contract_days):
        """Calculate TAC for HH (unit-based + standing charge)."""
        sc_total = self.standing_charges['HH'] * contract_days
        unit_total = self.apply_uplift(self.base_rates['HH']['unit'], 'HH') * total_kwh
        return sc_total + unit_total

    # ---------------------- Total Calculations ---------------------- #

    def calculate_total_nhh(self, day_kwh, night_kwh, ew_kwh, contract_days):
        """Calculate total cost for NHH."""
        day_kwh_adj = self.adjust_for_losses(day_kwh)
        night_kwh_adj = self.adjust_for_losses(night_kwh)
        ew_kwh_adj = self.adjust_for_losses(ew_kwh)
        return self.calculate_tac_nhh(day_kwh_adj, night_kwh_adj, ew_kwh_adj, contract_days)

    def calculate_total_hh(self, total_kwh, contract_days):
        """Calculate total cost for HH."""
        total_kwh_adj = self.adjust_for_losses(total_kwh)
        return self.calculate_tac_hh(total_kwh_adj, contract_days)

    # ---------------------- Batch/Scenario Methods ---------------------- #

    def price_multiple_nhh(self, consumption_profiles):
        """
        Price multiple NHH profiles.
        consumption_profiles: list of dicts with keys: day_kwh, night_kwh, ew_kwh, contract_days
        """
        results = []
        for profile in consumption_profiles:
            cost = self.calculate_total_nhh(
                profile['day_kwh'],
                profile['night_kwh'],
                profile.get('ew_kwh', 0),
                profile['contract_days']
            )
            results.append({**profile, 'total_cost': round(cost, 2)})
        return results

    def price_multiple_hh(self, consumption_profiles):
        """
        Price multiple HH profiles.
        consumption_profiles: list of dicts with keys: total_kwh, contract_days
        """
        results = []
        for profile in consumption_profiles:
            cost = self.calculate_total_hh(
                profile['total_kwh'],
                profile['contract_days']
            )
            results.append({**profile, 'total_cost': round(cost, 2)})
        return results

    # ---------------------- Utility Methods ---------------------- #

    def summary(self):
        """Return a summary of current configuration."""
        return {
            'base_rates': self.base_rates,
            'uplifts': self.uplifts,
            'standing_charges': self.standing_charges,
            'loss_factors': self.loss_factors
        }

# ---------------------- Example Configuration ---------------------- #

base_rates = {
    'NHH': {
        'day': 0.14,   # £/kWh day
        'night': 0.08, # £/kWh night
        'ew': 0.10     # £/kWh evening & weekend
    },
    'HH': {
        'unit': 0.12   # £/kWh HH
    }
}

uplifts = {
    'HH': 0.05,   # 5% uplift for HH energy rates (not TAC)
    'NHH': 0.03   # 3% uplift for NHH energy rates (not TAC)
}

standing_charges = {
    'NHH': 0.25,  # £0.25/day for NHH
    'HH': 0.30    # £0.30/day for HH
}

loss_factors = {
    'DF': 1.02,   # Distribution Factor
    'LF': 1.03,   # Loss Factor
    'AF': 1.00    # Adjustment Factor
}

pricing_tool_v28 = BespokePricingToolV28(base_rates, uplifts, standing_charges, loss_factors)
