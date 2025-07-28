import streamlit as st

# ---------------------- BespokePricingToolV28 Class ---------------------- #

class BespokePricingToolV28:
    def __init__(self, base_rates, uplifts, standing_charges, loss_factors=None):
        self.base_rates = base_rates
        self.uplifts = uplifts
        self.standing_charges = standing_charges
        self.loss_factors = loss_factors or {
            'DF': 1.0, 'LF': 1.0, 'AF': 1.0
        }

    def apply_uplift(self, rate, mpan_type):
        uplift = self.uplifts.get(mpan_type, 0)
        return rate * (1 + uplift)

    def adjust_for_losses(self, kwh):
        return kwh * self.loss_factors['DF'] * self.loss_factors['LF'] * self.loss_factors['AF']

    def calculate_tac_nhh(self, day_kwh, night_kwh, ew_kwh, contract_days):
        sc_total = self.standing_charges['NHH'] * contract_days
        unit_day = self.apply_uplift(self.base_rates['NHH']['day'], 'NHH') * day_kwh
        unit_night = self.apply_uplift(self.base_rates['NHH']['night'], 'NHH') * night_kwh
        unit_ew = self.apply_uplift(self.base_rates['NHH'].get('ew', 0), 'NHH') * ew_kwh
        return sc_total + unit_day + unit_night + unit_ew

    def calculate_tac_hh(self, total_kwh, contract_days):
        sc_total = self.standing_charges['HH'] * contract_days
        unit_total = self.apply_uplift(self.base_rates['HH']['unit'], 'HH') * total_kwh
        return sc_total + unit_total

    def calculate_total_nhh(self, day_kwh, night_kwh, ew_kwh, contract_days):
        day_kwh_adj = self.adjust_for_losses(day_kwh)
        night_kwh_adj = self.adjust_for_losses(night_kwh)
        ew_kwh_adj = self.adjust_for_losses(ew_kwh)
        return self.calculate_tac_nhh(day_kwh_adj, night_kwh_adj, ew_kwh_adj, contract_days)

    def calculate_total_hh(self, total_kwh, contract_days):
        total_kwh_adj = self.adjust_for_losses(total_kwh)
        return self.calculate_tac_hh(total_kwh_adj, contract_days)

    def price_multiple_nhh(self, consumption_profiles):
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
        results = []
        for profile in consumption_profiles:
            cost = self.calculate_total_hh(
                profile['total_kwh'],
                profile['contract_days']
            )
            results.append({**profile, 'total_cost': round(cost, 2)})
        return results

    def summary(self):
        return {
            'base_rates': self.base_rates,
            'uplifts': self.uplifts,
            'standing_charges': self.standing_charges,
            'loss_factors': self.loss_factors
        }

# ---------------------- Default Configuration ---------------------- #

base_rates = {
    'NHH': {
        'day': 0.14,
        'night': 0.08,
        'ew': 0.10
    },
    'HH': {
        'unit': 0.12
    }
}

uplifts = {
    'HH': 0.05,
    'NHH': 0.03
}

standing_charges = {
    'NHH': 0.25,
    'HH': 0.30
}

loss_factors = {
    'DF': 1.02,
    'LF': 1.03,
    'AF': 1.00
}

pricing_tool_v28 = BespokePricingToolV28(base_rates, uplifts, standing_charges, loss_factors)

# ---------------------- Streamlit Interface ---------------------- #

st.title("🔌 Bespoke Power Pricing Tool – V28")

st.subheader("Non-Half-Hourly (NHH) Calculator")

with st.form("nhh_form"):
    day_kwh = st.number_input("Day kWh", value=1000.0)
    night_kwh = st.number_input("Night kWh", value=500.0)
    ew_kwh = st.number_input("Evening & Weekend kWh", value=300.0)
    contract_days = st.number_input("Contract Length (days)", value=365, step=1)

    submitted = st.form_submit_button("Calculate NHH Total Cost")
    if submitted:
        total = pricing_tool_v28.calculate_total_nhh(day_kwh, night_kwh, ew_kwh, contract_days)
        st.success(f"Total NHH Cost: £{round(total, 2)}")

st.divider()

st.subheader("Half-Hourly (HH) Calculator")

with st.form("hh_form"):
    total_kwh = st.number_input("Total kWh", value=15000.0)
    contract_days_hh = st.number_input("Contract Length (days)", value=365, step=1)

    submitted_hh = st.form_submit_button("Calculate HH Total Cost")
    if submitted_hh:
        total_hh = pricing_tool_v28.calculate_total_hh(total_kwh, contract_days_hh)
        st.success(f"Total HH Cost: £{round(total_hh, 2)}")
