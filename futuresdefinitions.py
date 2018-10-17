# -*- coding: utf-8 -*-

"""Utilities for futures analysis."""

from collections import namedtuple


class futurespecs:
    def known_root(self, root):
        """Return true if this is a known root."""
        return root in root_to_parameters


    def get_contract_info(self, root):
        """get contract specifications for this future."""
        return root_to_parameters[root]


    def get_future_month(self, root):
        """get expiration month for this future."""
        return letter_to_month['x']



parameters = namedtuple('parameters', ['commodity', 'contract_size', 'unit', 'tick',
                        'dollarpertick', 'exchange', 'margin', 'apiname'])

root_to_parameters = {
    'TY':parameters('10-Year T-Note (P)', '1000', '$', '0.015625', '15.625', 'CBOT', '<$2,000', 'TY*1'),
    'TU':parameters('2-Year T-Note (P)', '2000', '$', '0.0078125', '15.625', 'CBOT', '<$2,000', 'TU*1'),
    # 'FF':parameters('30-Day Fed Funds (P)', '4167', '$', '0.005', '20.835', 'CBOT', '<$2,000', 'FF*1'),
    'FF':parameters('30-Day Fed Funds (P)', '4167', '$', '0.0025', '10.4175', 'CBOT', '<$2,000', 'FF*1'),
    'US':parameters('30-Year T-Bond (P)', '1000', '$', '0.03125', '31.25', 'CBOT', '<$2,000', 'US*1'),
    'FV':parameters('5-Year T-Note (P)', '1000', '$', '0.015625', '15.625', 'CBOT', '<$2,000', 'FV*1'),
    'AD':parameters('Australian Dollar (P)', '100000', 'A$', '0.0001', '10', 'CME', '<$2,000', 'AD*1'),
    'BR':parameters('Brazilian Real (P)', '100000', 'Real', '0.00005', '5', 'CME', '>$2,000', 'BR*1'),
    'BP':parameters('British Pound (P)', '62500', 'Pound', '0.0001', '6.25', 'CME', '<$2,000', 'BP*1'),
    'CD':parameters('Canadian Dollar (P)', '100000', 'C$', '0.0001', '10', 'CME', '<$2,000', 'CD*1'),
    'QC':parameters('Copper emiNY', '12500', 'lbs', '0.2', '25', 'COMEX', '>$2,000', 'QC*1'),
    'C':parameters('Corn (P)', '50', 'BU', '0.25', '12.5', 'CBOT', '<$2,000', 'C*1'),
    'CL':parameters('Crude Oil', '1000', 'barrels', '0.01', '10', 'NYMEX', '>$2,000', 'CL*1'),
    'QM':parameters('Crude Oil emiNY', '500', 'barrels', '0.025', '12.5', 'NYMEX', '>$2,000', 'QM*1'),
    'J7':parameters('E-Mini Japanese Yen (P)', '62500', 'Yen', '0.0001', '6.25', 'CME', '<$2,000', 'J7*1'),
    'ED':parameters('Eurodollar (P)', '2500', '$', '0.005', '12.5', 'CME', '<$2,000', 'ED*1'),
    'FC':parameters('Feeder Cattle (P)', '500', 'lbs', '0.025', '12.5', 'CME', '<$2,000', 'FC*1'),
    'QU':parameters('Gas. Unleaded emiNY', '21000', 'gallons', '0.001', '21', 'NYMEX', '>$2,000', 'QU*1'),
    'RB':parameters('Gasoline RBOB', '42000', 'gallons', '0.0001', '4.2', 'NYMEX', '>$2,000', 'RB*1'),
    'GC':parameters('Gold', '100', 'troy oz', '0.1', '10', 'COMEX', '>$2,000', 'GC*1'),
    'QO':parameters('Gold emiNY', '50', 'troy oz', '0.25', '12.5', 'COMEX', '<$2,000', 'QO*1'),
    'HO':parameters('Heating Oil', '42000', 'gallons', '0.0001', '4.2', 'NYMEX', '>$2,000', 'HO*1'),
    'QH':parameters('Heating Oil emiNY', '21000', 'gallons', '0.001', '21', 'NYMEX', '>$2,000', 'QH*1'),
    'LH':parameters('Lean Hogs (P)', '400', 'lbs', '0.025', '10', 'CME', '<$2,000', 'LH*1'),
    'LC':parameters('Live Cattle (P)', '400', 'lbs', '0.025', '10', 'CME', '<$2,000', 'LC*1'),
    'LB':parameters('Lumber (P)', '110', 'Bft', '0.1', '11', 'CME', '<$2,000', 'LB*1'),
    'NG':parameters('Natural Gas', '10000', 'mmbtu', '0.001', '10', 'NYMEX', '>$2,000', 'NG*1'),
    'QG':parameters('Natural Gas emiNY', '2500', 'mmbtu', '0.005', '12.5', 'NYMEX', '>$2,000', 'QG*1'),
    'NE':parameters('New Zealand Dollar (P)', '100000', 'NZ$', '0.0001', '10', 'CME', '>$2,000', 'NE*1'),
    'O':parameters('Oats (P)', '50', 'BU', '0.25', '12.5', 'CBOT', '<$2,000', 'O*1'),
    'PA':parameters('Palladium', '100', 'troy oz', '0.05', '5', 'NYMEX', '>$2,000', 'PA*1'),
    'PL':parameters('Platinum', '50', 'troy oz', '0.1', '5', 'NYMEX', '>$2,000', 'PL*1'),
    'RR':parameters('Rough Rice (P)', '2000', 'CWT', '0.005', '10', 'CBOT', '<$2,000', 'RR*1'),
    'RU':parameters('Russian Ruble (P)', '2500000', 'RU', '0.00001', '25', 'CME', '>$2,000', 'RU*1'),
    'SI':parameters('Silver', '5000', 'troy oz', '0.005', '25', 'COMEX', '>$2,000', 'SI*1'),
    'RA':parameters('South African Rand', '500000', 'SA Rand', '0.000025', '12.5', 'CME', '>$2,000', 'RA*1'),
    'SM':parameters('Soybean Meal (P)', '100', 'Tons', '0.1', '10', 'CBOT', '<$2,000', 'SM*1'),
    'BO':parameters('Soybean Oil (P)', '600', 'lbs', '0.01', '6', 'CBOT', '<$2,000', 'BO*1'),
    'S':parameters('Soybeans (P)', '50', 'bushels', '0.25', '50', 'CBOT', '>$2,000', 'S*1'),
    'SF':parameters('Swiss Franc (P)', '125000', 'Swiss F', '0.0001', '12.5', 'CME', '<$2,000', 'SF*1'),
    'W':parameters('Wheat (P)', '50', 'BU', '0.25', '12.5', 'CBOT', '<$2,000', 'W*1'),
    'ES':parameters('E-Mini S&P 500', '50', '$', '0.25', '12.5', 'CME', '<$2,000', 'ES*1')
}
