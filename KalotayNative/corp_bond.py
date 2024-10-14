from Kalotay_python.interface.imuni_analytics_client_wrapper import IMuniAnalyticsClientWrapper
import KalotayNative.AkaApi as AkaApi
import pandas as pd
from KalotayNative.utils import get_holidays_list


class CorpBond:
    """
    Class to create an AkaApi.Bond for a corporate bond
    """
    def __init__(self, **kwargs):
        self.cusip = kwargs.get("cusip")
        self.settle_date = (pd.to_datetime(self.trade_date) + pd.offsets.CustomBusinessDay(1)).strftime("%Y-%m-%d")
        self.issue_date = kwargs.get("issue_date")
        self.issue_price = kwargs.get("issue_price")
        self.coupon = kwargs.get("coupon")
        self.treat_as_prerefunded = False
        self.refunding_info = None
        self.maturity_date = kwargs.get("maturity_date")
        self.coupon_freq = kwargs.get("coupon_freq")
        self.day_count = None
        self.first_coupon_date = kwargs.get("first_coupon_date")

        self.value_date = self.trade_date
        self.bond = self.create_bond()

        self.bond.SetDaycount(AkaApi.Bond.DC_ACT_365)
        self.set_coupon_freq()


    def get_bond(self):
        return self.bond

    def get_value_date(self):
        return self.value_date
    
    def get_coupon(self):
        return self.coupon
    
    def get_matuirty_date(self):
        return self.maturity_date
    
    def get_prerefunded_treatment(self):
        return self.treat_as_prerefunded
    
    def get_issue_date(self):
        return self.issue_date
    
    def get_coupon_freq(self):
        return self.coupon_freq
    
    def get_day_count(self):
        return self.day_count
    
    def check_pre_refund_status(self):
        return False
    
    def create_bond(self, maturity_date=None, redemption_price=None):
        if maturity_date is None:
            self.maturity_date = maturity_date

        issue_date_year, issue_date_month, issue_date_day = str(self.issue_date.split("-")[0]), str(self.issue_date.split("-")[1]), str(self.issue_date.split("-")[2])
        issue_date_integer = int(issue_date_year + issue_date_month + issue_date_day)
        bond = AkaApi.Bond(self.cusip, AkaApi.Date(issue_date_integer), AkaApi.Date(self.maturity_date), self.coupon)

        # add holidays
        holidays_start_date = (pd.to_datetime(self.issue_date) - pd.DateOffset(months=12)).strftime("%Y-%m-%d")
        holidays_end_date = (pd.to_datetime(self.maturity_date) + pd.DateOffset(months=12)).strftime("%Y-%m-%d")
        holidays_list = [str(i) for i in list(get_holidays_list(holidays_start_date, holidays_end_date)["DATE"])]
        for holiday in holidays_list:
            bond.SetHoliday(AkaApi.Date(int(holiday[:4] + holiday[5:7] + holiday[8:])))

        bond.SetIssuePrice(self.issue_price)

        first_coupon_date_year, first_coupon_date_month, first_coupon_date_day = str(self.first_coupon_date.split("-")[0]), str(self.first_coupon_date.split("-")[1]), str(self.first_coupon_date.split("-")[2])
        bond.SetFirstCoupon(AkaApi.Date(int(first_coupon_date_year + first_coupon_date_month + first_coupon_date_day)))

        if redemption_price is not None:
            bond.SetRedemptionPrice(redemption_price)

        return bond
    
    def set_coupon_freq(self):
        if self.coupon_freq == "1":
            self.bond.SetCouponFreq(AkaApi.Bond.FREQ_ANNUAL)
        elif self.coupon_freq == "2":
            self.bond.SetCouponFreq(AkaApi.Bond.FREQ_SEMIANNUAL)
        elif self.coupon_freq == "4":
            self.bond.SetCouponFreq(AkaApi.Bond.FREQ_QUARTERLY)            
        elif self.coupon_freq == "12":
            self.bond.SetCouponFreq(AkaApi.Bond.FREQ_MONTHLY)

    def add_call_schedule(self):
        zero_coupon = self.muni_security.IsZeroCoupon
        call_schedule = self.muni_security.CallSchedule.split("|")

        if len(call_schedule) > 0:
            for call in call_schedule:
                self.bond.SetCall(AkaApi.Date(int(call.split("@")[0][6:] + call.split("@")[0][:2] + call.split("@")[0][3:5])), float(call.split("@")[-1]))

        if self.muni_security.CallFrequency == "T" and not zero_coupon:
            self.bond.SetCallAmerican(True)
        else:
            self.bond.SetCallAmerican(False)

        self.bond.SetNoticePeriod(self.muni_security.CallDaysNotice)

    def set_put_schedule(self):
        put_schedule = self.muni_security.PutSchedule.split("|")

        for put in put_schedule:
            self.bond.SetCall(AkaApi.Date(int(put.split("@")[0][6:] + put.split("@")[0][:2] + put.split("@")[0][3:5])), float(put.split("@")[-1]))

    def set_sink_schedule(self):
        self.bond.SetFaceAmount(self.muni_security.AmountOutstanding)
        sink_schedule = self.muni_security.SinkSchedule.split("^")
        for sink in sink_schedule:
            sink = sink.split("|")
            self.bond.SetSink(AkaApi.Date(int(sink[0][6:] + sink[0][:2] + sink[0][3:5])), float(sink[2]), float(sink[1]))

    def set_coupon_schedule(self):
        step_schedule = self.muni_security.StepSchedule.split("|")
        for step in step_schedule:
            step = step.split("@")
            self.bond.SetCoupon(AkaApi.Date(int(step[0][6:] + step[0][:2] + step[0][3:5])), float(step[1]))
