import pandas as pd
import numpy as np

class TrendAnalyzer:
    @staticmethod
    def apply_cagr(series, periods_to_project):
        s = pd.to_numeric(series, errors='coerce').dropna()
        if len(s) < 2:
            return [float(s.iloc[-1]) if len(s) > 0 else 0.0] * periods_to_project, 0.0

        val_ini = float(s.iloc[0])
        val_fin = float(s.iloc[-1])
        n = len(s) - 1

        if val_ini <= 0 or val_fin <= 0:
            return TrendAnalyzer.apply_moving_average(s, periods_to_project, window=3)

        cagr = (val_fin / val_ini) ** (1 / n) - 1
        
        projections = []
        last_val = val_fin
        for _ in range(periods_to_project):
            next_val = last_val * (1 + cagr)
            projections.append(float(next_val))
            last_val = next_val
            
        return projections, float(cagr)

    @staticmethod
    def apply_moving_average(series, periods_to_project, window=3):
        s = pd.to_numeric(series, errors='coerce').dropna()
        if len(s) < 1:
            return [0.0] * periods_to_project, 0.0
            
        projections = []
        history = list(s.values)
        
        for _ in range(periods_to_project):
            ma = np.mean(history[-window:]) if len(history) >= window else np.mean(history)
            projections.append(float(ma))
            history.append(float(ma))
            
        growth_rate = 0.0
        if len(s) > 1 and s.iloc[0] != 0:
            val_ini = float(s.iloc[0])
            val_fin = float(s.iloc[-1])
            if val_ini > 0 and val_fin > 0:
                growth_rate = (val_fin / val_ini) ** (1/(len(s)-1)) - 1
            
        return projections, float(growth_rate)

    @staticmethod
    def apply_linear_regression(series, periods_to_project):
        s = pd.to_numeric(series, errors='coerce').dropna()
        if len(s) < 2:
            return [float(s.iloc[-1]) if len(s)>0 else 0.0] * periods_to_project, 0.0, 0.0

        y = s.values
        x = np.arange(len(y))
        
        m, c = np.polyfit(x, y, 1)
        
        y_pred_hist = m * x + c
        ss_res = np.sum((y - y_pred_hist)**2)
        ss_tot = np.sum((y - np.mean(y))**2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 1.0

        projections = []
        last_x = x[-1]
        for i in range(1, periods_to_project + 1):
            val = m * (last_x + i) + c
            projections.append(float(val))
            
        return projections, float(r_squared), float(m)

    @classmethod
    def analyze_and_project(cls, series, periods_to_project, account_nature='debit'):
        s = pd.Series(series)
        s = pd.to_numeric(s, errors='coerce').dropna()
        if len(s) < 3:
            proj, gr = cls.apply_moving_average(s, periods_to_project)
            return proj, 'Promedio Móvil (Falta Histórico)', 0.0, gr

        proj_lr, r2, m = cls.apply_linear_regression(s, periods_to_project)
        
        # Calculate implicit growth rate for regression
        growth_rate_lr = 0.0
        if len(s) > 0 and s.iloc[-1] != 0:
            growth_rate_lr = (m * 12 / s.iloc[-1]) # Annualized roughly
            
        if r2 > 0.65:
            return proj_lr, 'Regresión Lineal', r2, growth_rate_lr
            
        if all(v > 0 for v in s):
            proj_cagr, cagr_rate = cls.apply_cagr(s, periods_to_project)
            return proj_cagr, 'Tasa CAGR', cagr_rate, cagr_rate
            
        proj_ma, gr = cls.apply_moving_average(s, periods_to_project)
        return proj_ma, 'Promedio Móvil', gr, gr

    @classmethod
    def generate_scenarios(cls, base_projections, volatility=0.02):
        base = np.array(base_projections)
        optimistic = base * (1 + volatility * np.arange(1, len(base) + 1))
        pessimistic = base * (1 - volatility * np.arange(1, len(base) + 1))
    @classmethod
    def apply_montecarlo(cls, series, periods_to_project, iterations=1000, base_annual_rate=None):
        s = pd.to_numeric(pd.Series(series), errors='coerce').dropna()
        if len(s) < 2:
            val = float(s.iloc[-1]) if len(s) > 0 else 0.0
            return [val]*periods_to_project, [val]*periods_to_project, [val]*periods_to_project
            
        # Calculate historical percentage returns
        returns = s.pct_change().dropna()
        if len(returns) < 1:
            val = float(s.iloc[-1])
            return [val]*periods_to_project, [val]*periods_to_project, [val]*periods_to_project
            
        if base_annual_rate is not None:
            mu = base_annual_rate / 12.0
        else:
            mu = returns.mean()
            
        sigma = returns.std()
        
        last_val = float(s.iloc[-1])
        
        # Initialize simulation array: shape (iterations, periods_to_project)
        simulations = np.zeros((iterations, periods_to_project))
        
        for i in range(iterations):
            # Generate random shocks from normal distribution
            shocks = np.random.normal(mu, sigma, periods_to_project)
            
            # Calculate price path
            path = [last_val]
            for shock in shocks:
                path.append(path[-1] * (1 + shock))
            
            simulations[i, :] = path[1:]
            
        # Calculate percentiles for Pessimistic (10%), Base (50%), Optimistic (90%)
        pesimista = np.percentile(simulations, 10, axis=0)
        base = np.percentile(simulations, 50, axis=0)
        optimista = np.percentile(simulations, 90, axis=0)
        
        return [round(float(x), 2) for x in pesimista], [round(float(x), 2) for x in base], [round(float(x), 2) for x in optimista]

# Test
if __name__ == "__main__":
    series_cartera = [100, 105, 110, 116, 122, 130] # Clear upward trend
    proj, method, metric, gr = TrendAnalyzer.analyze_and_project(series_cartera, 12)
    b, o, p = TrendAnalyzer.generate_scenarios(proj)
    print("Method:", method)
    print("Metric:", metric)
    print("Growth Rate:", gr)
    print("Base[0]:", b[0])
    
