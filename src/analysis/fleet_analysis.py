import pandas as pd
import numpy as np
import sqlite3
from scipy import stats
from scipy.stats import chi2_contingency, pearsonr
import statsmodels.api as sm
from statsmodels.formula.api import logit
import warnings
warnings.filterwarnings('ignore')

DB_PATH = 'data/tesla_fleet.db'

def load_data():
    conn = sqlite3.connect(DB_PATH)
    demo_df = pd.read_sql("SELECT * FROM demo_drives", conn)
    vehicle_df = pd.read_sql("SELECT * FROM vehicle_inventory", conn)
    market_df = pd.read_sql("SELECT * FROM market_summary", conn)
    conn.close()
    demo_df['demo_date'] = pd.to_datetime(demo_df['demo_date'])
    return demo_df, vehicle_df, market_df


def conversion_by_segment(demo_df):
    result = demo_df.groupby('customer_segment').agg(
        total_demos=('demo_id', 'count'),
        conversions=('converted', 'sum'),
        avg_satisfaction=('satisfaction_score', 'mean'),
        avg_drive_duration=('drive_duration_mins', 'mean')
    ).reset_index()
    result['conversion_rate'] = (result['conversions'] / result['total_demos']).round(4)
    result['conversion_pct'] = (result['conversion_rate'] * 100).round(2)
    return result.sort_values('conversion_rate', ascending=False)


def conversion_by_model(demo_df):
    result = demo_df.groupby('vehicle_model').agg(
        total_demos=('demo_id', 'count'),
        conversions=('converted', 'sum'),
        avg_satisfaction=('satisfaction_score', 'mean'),
        avg_drive_duration=('drive_duration_mins', 'mean'),
        avg_price=('vehicle_price', 'mean')
    ).reset_index()
    result['conversion_rate'] = (result['conversions'] / result['total_demos']).round(4)
    result['revenue_per_demo'] = (
        result['conversions'] * result['avg_price'] / result['total_demos']
    ).round(2)
    return result.sort_values('conversion_rate', ascending=False)


def conversion_by_market(demo_df):
    result = demo_df.groupby(['market', 'region', 'market_size']).agg(
        total_demos=('demo_id', 'count'),
        conversions=('converted', 'sum'),
        avg_satisfaction=('satisfaction_score', 'mean'),
        avg_utilization=('utilization_rate', 'mean'),
        total_revenue=('revenue_generated', 'sum')
    ).reset_index()
    result['conversion_rate'] = (result['conversions'] / result['total_demos']).round(4)
    result['revenue_per_demo'] = (result['total_revenue'] / result['total_demos']).round(2)

    # Performance tier
    median_conv = result['conversion_rate'].median()
    result['performance_tier'] = result['conversion_rate'].apply(
        lambda x: 'High Performer' if x >= median_conv * 1.15
        else ('Needs Attention' if x <= median_conv * 0.85 else 'Average')
    )
    return result.sort_values('conversion_rate', ascending=False)


def weekend_vs_weekday_analysis(demo_df):
    weekend = demo_df[demo_df['is_weekend'] == 1]['converted']
    weekday = demo_df[demo_df['is_weekend'] == 0]['converted']

    weekend_rate = weekend.mean()
    weekday_rate = weekday.mean()

    t_stat, p_value = stats.ttest_ind(weekend, weekday)

    return {
        'weekend_conversion_rate': round(weekend_rate, 4),
        'weekday_conversion_rate': round(weekday_rate, 4),
        'lift': round((weekend_rate - weekday_rate) / weekday_rate * 100, 2),
        't_statistic': round(t_stat, 4),
        'p_value': round(p_value, 6),
        'statistically_significant': p_value < 0.05,
        'weekend_demos': len(weekend),
        'weekday_demos': len(weekday)
    }


def drive_duration_impact(demo_df):
    converted = demo_df[demo_df['converted'] == 1]['drive_duration_mins']
    not_converted = demo_df[demo_df['converted'] == 0]['drive_duration_mins']

    t_stat, p_value = stats.ttest_ind(converted, not_converted)
    correlation, corr_p = pearsonr(
        demo_df['drive_duration_mins'],
        demo_df['converted']
    )

    bins = [0, 30, 45, 60, 75, 200]
    labels = ['<30min', '30-45min', '45-60min', '60-75min', '75min+']
    demo_df['duration_bucket'] = pd.cut(
        demo_df['drive_duration_mins'],
        bins=bins, labels=labels
    )

    by_duration = demo_df.groupby('duration_bucket', observed=True).agg(
        demos=('demo_id', 'count'),
        conversions=('converted', 'sum')
    ).reset_index()
    by_duration['conversion_rate'] = (
        by_duration['conversions'] / by_duration['demos']
    ).round(4)

    return {
        'avg_duration_converted': round(converted.mean(), 1),
        'avg_duration_not_converted': round(not_converted.mean(), 1),
        'correlation': round(correlation, 4),
        'correlation_p_value': round(corr_p, 6),
        'p_value': round(p_value, 6),
        'statistically_significant': p_value < 0.05,
        'by_duration_bucket': by_duration
    }


def hourly_conversion_analysis(demo_df):
    by_hour = demo_df.groupby('hour_of_day').agg(
        demos=('demo_id', 'count'),
        conversions=('converted', 'sum')
    ).reset_index()
    by_hour['conversion_rate'] = (
        by_hour['conversions'] / by_hour['demos']
    ).round(4)

    peak_hour = by_hour.loc[by_hour['conversion_rate'].idxmax()]
    low_hour = by_hour.loc[by_hour['conversion_rate'].idxmin()]

    return {
        'by_hour': by_hour,
        'peak_hour': int(peak_hour['hour_of_day']),
        'peak_conversion_rate': round(float(peak_hour['conversion_rate']), 4),
        'lowest_hour': int(low_hour['hour_of_day']),
        'lowest_conversion_rate': round(float(low_hour['conversion_rate']), 4)
    }


def seasonal_trend_analysis(demo_df):
    by_month = demo_df.groupby(['demo_year', 'demo_month', 'demo_month_name']).agg(
        demos=('demo_id', 'count'),
        conversions=('converted', 'sum'),
        revenue=('revenue_generated', 'sum'),
        avg_satisfaction=('satisfaction_score', 'mean')
    ).reset_index()
    by_month['conversion_rate'] = (
        by_month['conversions'] / by_month['demos']
    ).round(4)
    by_month = by_month.sort_values(['demo_year', 'demo_month'])

    by_quarter = demo_df.groupby(['demo_year', 'demo_quarter']).agg(
        demos=('demo_id', 'count'),
        conversions=('converted', 'sum'),
        revenue=('revenue_generated', 'sum')
    ).reset_index()
    by_quarter['conversion_rate'] = (
        by_quarter['conversions'] / by_quarter['demos']
    ).round(4)

    return {
        'by_month': by_month,
        'by_quarter': by_quarter,
        'best_month': by_month.loc[by_month['conversion_rate'].idxmax(), 'demo_month_name'],
        'worst_month': by_month.loc[by_month['conversion_rate'].idxmin(), 'demo_month_name'],
    }


def underperforming_market_analysis(demo_df):
    market_perf = conversion_by_market(demo_df)
    overall_avg = demo_df['converted'].mean()
    threshold = overall_avg * 0.85

    underperforming = market_perf[
        market_perf['conversion_rate'] < threshold
    ][['market', 'region', 'conversion_rate', 'total_demos',
       'avg_utilization', 'revenue_per_demo', 'performance_tier']]

    opportunity = underperforming.copy()
    opportunity['gap_to_average'] = (
        overall_avg - opportunity['conversion_rate']
    ).round(4)
    opportunity['revenue_opportunity'] = (
        opportunity['gap_to_average'] *
        opportunity['total_demos'] *
        45000
    ).round(0)

    return {
        'overall_avg_conversion': round(overall_avg, 4),
        'threshold': round(threshold, 4),
        'underperforming_markets': underperforming,
        'opportunity_analysis': opportunity,
        'total_revenue_opportunity': opportunity['revenue_opportunity'].sum()
    }


def logistic_regression_model(demo_df):
    features = demo_df[[
        'drive_duration_mins', 'is_weekend', 'hour_of_day',
        'utilization_rate', 'satisfaction_score', 'converted'
    ]].copy()

    model_dummies = pd.get_dummies(
        demo_df['vehicle_model'], prefix='model', drop_first=True
    )
    segment_dummies = pd.get_dummies(
        demo_df['customer_segment'], prefix='seg', drop_first=True
    )

    features = pd.concat([features, model_dummies, segment_dummies], axis=1)
    features.columns = features.columns.str.replace(' ', '_').str.replace('/', '_')

    X = features.drop('converted', axis=1).astype(float)
    y = features['converted']

    X_sm = sm.add_constant(X)
    model = sm.Logit(y, X_sm).fit(disp=0)

    feature_importance = pd.DataFrame({
        'feature': X.columns,
        'coefficient': model.params[1:].values,
        'odds_ratio': np.exp(model.params[1:].values),
        'p_value': model.pvalues[1:].values
    }).sort_values('odds_ratio', ascending=False)

    return {
        'model': model,
        'feature_importance': feature_importance,
        'pseudo_r2': round(model.prsquared, 4),
        'aic': round(model.aic, 2),
        'significant_features': feature_importance[
            feature_importance['p_value'] < 0.05
        ]
    }


def run_full_analysis(demo_df, vehicle_df, market_df):
    print("Running full fleet analysis...")

    results = {
        'by_segment': conversion_by_segment(demo_df),
        'by_model': conversion_by_model(demo_df),
        'by_market': conversion_by_market(demo_df),
        'weekend_analysis': weekend_vs_weekday_analysis(demo_df),
        'duration_impact': drive_duration_impact(demo_df),
        'hourly_analysis': hourly_conversion_analysis(demo_df),
        'seasonal_trends': seasonal_trend_analysis(demo_df),
        'underperforming': underperforming_market_analysis(demo_df),
        'regression_model': logistic_regression_model(demo_df)
    }

    print("\nKey Findings:")
    print(f"  Overall conversion rate: {demo_df['converted'].mean():.1%}")
    print(f"  Best market: {results['by_market'].iloc[0]['market']} ({results['by_market'].iloc[0]['conversion_rate']:.1%})")
    print(f"  Worst market: {results['by_market'].iloc[-1]['market']} ({results['by_market'].iloc[-1]['conversion_rate']:.1%})")
    print(f"  Weekend lift: {results['weekend_analysis']['lift']}%")
    print(f"  Revenue opportunity: ${results['underperforming']['total_revenue_opportunity']:,.0f}")
    print(f"  Regression Pseudo R²: {results['regression_model']['pseudo_r2']}")

    return results


if __name__ == "__main__":
    demo_df, vehicle_df, market_df = load_data()
    results = run_full_analysis(demo_df, vehicle_df, market_df)
    print("\nAnalysis complete.")