import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta
import sqlite3
import os

fake = Faker()
np.random.seed(42)
random.seed(42)

# ── Constants ─────────────────────────────────────────────────
TESLA_MODELS = {
    'Model 3': {'base_price': 40240, 'demo_appeal': 0.72, 'avg_drive_duration': 45},
    'Model Y': {'base_price': 43990, 'demo_appeal': 0.85, 'avg_drive_duration': 50},
    'Model S': {'base_price': 74990, 'demo_appeal': 0.61, 'avg_drive_duration': 55},
    'Model X': {'base_price': 79990, 'demo_appeal': 0.58, 'avg_drive_duration': 60},
    'Cybertruck': {'base_price': 49890, 'demo_appeal': 0.91, 'avg_drive_duration': 65},
}

MARKETS = {
    'Los Angeles, CA':    {'region': 'West',      'market_size': 'Large',  'base_conversion': 0.23, 'avg_weekly_demos': 85},
    'San Francisco, CA':  {'region': 'West',      'market_size': 'Large',  'base_conversion': 0.26, 'avg_weekly_demos': 72},
    'Phoenix, AZ':        {'region': 'Southwest', 'market_size': 'Medium', 'base_conversion': 0.19, 'avg_weekly_demos': 48},
    'Dallas, TX':         {'region': 'South',     'market_size': 'Large',  'base_conversion': 0.21, 'avg_weekly_demos': 63},
    'Austin, TX':         {'region': 'South',     'market_size': 'Medium', 'base_conversion': 0.24, 'avg_weekly_demos': 55},
    'Miami, FL':          {'region': 'Southeast', 'market_size': 'Large',  'base_conversion': 0.18, 'avg_weekly_demos': 58},
    'New York, NY':       {'region': 'Northeast', 'market_size': 'Large',  'base_conversion': 0.22, 'avg_weekly_demos': 91},
    'Chicago, IL':        {'region': 'Midwest',   'market_size': 'Large',  'base_conversion': 0.17, 'avg_weekly_demos': 67},
    'Seattle, WA':        {'region': 'Northwest', 'market_size': 'Medium', 'base_conversion': 0.28, 'avg_weekly_demos': 44},
    'Denver, CO':         {'region': 'Mountain',  'market_size': 'Medium', 'base_conversion': 0.25, 'avg_weekly_demos': 39},
    'Atlanta, GA':        {'region': 'Southeast', 'market_size': 'Medium', 'base_conversion': 0.16, 'avg_weekly_demos': 51},
    'Boston, MA':         {'region': 'Northeast', 'market_size': 'Medium', 'base_conversion': 0.23, 'avg_weekly_demos': 46},
    'Portland, OR':       {'region': 'Northwest', 'market_size': 'Small',  'base_conversion': 0.27, 'avg_weekly_demos': 31},
    'Las Vegas, NV':      {'region': 'West',      'market_size': 'Medium', 'base_conversion': 0.15, 'avg_weekly_demos': 42},
    'San Diego, CA':      {'region': 'West',      'market_size': 'Medium', 'base_conversion': 0.24, 'avg_weekly_demos': 38},
}

CUSTOMER_SEGMENTS = {
    'Tech Early Adopter':    {'conversion_multiplier': 1.45, 'weight': 0.22},
    'Eco Conscious':         {'conversion_multiplier': 1.28, 'weight': 0.18},
    'Luxury Buyer':          {'conversion_multiplier': 1.15, 'weight': 0.15},
    'Cost Conscious':        {'conversion_multiplier': 0.72, 'weight': 0.20},
    'First Time EV':         {'conversion_multiplier': 0.95, 'weight': 0.15},
    'Fleet/Business Buyer':  {'conversion_multiplier': 1.35, 'weight': 0.10},
}

SEASONALITY = {
    1: 0.82, 2: 0.85, 3: 0.95, 4: 1.05,
    5: 1.12, 6: 1.08, 7: 1.03, 8: 1.06,
    9: 1.04, 10: 1.02, 11: 0.88, 12: 0.90
}

def generate_demo_drives(n_records=15000):
    records = []
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2025, 12, 31)

    for i in range(n_records):
        market = random.choice(list(MARKETS.keys()))
        market_info = MARKETS[market]
        model = random.choices(
            list(TESLA_MODELS.keys()),
            weights=[0.28, 0.35, 0.12, 0.10, 0.15]
        )[0]
        model_info = TESLA_MODELS[model]
        segment = random.choices(
            list(CUSTOMER_SEGMENTS.keys()),
            weights=[s['weight'] for s in CUSTOMER_SEGMENTS.values()]
        )[0]
        segment_info = CUSTOMER_SEGMENTS[segment]

        demo_date = start_date + timedelta(
            days=random.randint(0, (end_date - start_date).days)
        )
        month = demo_date.month
        day_of_week = demo_date.weekday()
        hour = random.choices(
            range(9, 20),
            weights=[0.05,0.07,0.10,0.12,0.13,0.12,0.11,0.10,0.09,0.07,0.04]
        )[0]

        # Weekend boost
        weekend_multiplier = 1.18 if day_of_week >= 5 else 1.0

        # Calculate conversion probability
        base_conv = market_info['base_conversion']
        conversion_prob = (
            base_conv *
            segment_info['conversion_multiplier'] *
            model_info['demo_appeal'] *
            SEASONALITY[month] *
            weekend_multiplier *
            random.uniform(0.85, 1.15)
        )
        conversion_prob = min(max(conversion_prob, 0.05), 0.65)
        converted = 1 if random.random() < conversion_prob else 0

        # Drive duration with noise
        base_duration = model_info['avg_drive_duration']
        drive_duration = max(15, int(np.random.normal(base_duration, 8)))

        # Days to purchase after demo
        days_to_purchase = None
        if converted:
            days_to_purchase = int(np.random.exponential(12)) + 1

        # Vehicle utilization
        vehicle_id = f"{market[:3].upper()}-{model[:3].upper()}-{random.randint(1,8):02d}"
        utilization_rate = random.uniform(0.45, 0.95)

        # Satisfaction score
        satisfaction = round(random.uniform(3.2, 5.0), 1)
        if converted:
            satisfaction = round(min(5.0, satisfaction + random.uniform(0.3, 0.8)), 1)

        records.append({
            'demo_id': f'DEMO-{i+1:06d}',
            'demo_date': demo_date.strftime('%Y-%m-%d'),
            'demo_year': demo_date.year,
            'demo_month': month,
            'demo_month_name': demo_date.strftime('%B'),
            'demo_quarter': f'Q{(month-1)//3+1}',
            'day_of_week': demo_date.strftime('%A'),
            'hour_of_day': hour,
            'is_weekend': 1 if day_of_week >= 5 else 0,
            'market': market,
            'region': market_info['region'],
            'market_size': market_info['market_size'],
            'vehicle_model': model,
            'vehicle_id': vehicle_id,
            'vehicle_price': model_info['base_price'],
            'customer_segment': segment,
            'drive_duration_mins': drive_duration,
            'utilization_rate': round(utilization_rate, 3),
            'converted': converted,
            'conversion_probability': round(conversion_prob, 4),
            'days_to_purchase': days_to_purchase,
            'satisfaction_score': satisfaction,
            'revenue_generated': model_info['base_price'] if converted else 0,
            'demo_cost': round(random.uniform(45, 85), 2),
        })

    df = pd.DataFrame(records)
    df['demo_date'] = pd.to_datetime(df['demo_date'])
    return df


def generate_vehicle_inventory(demo_df):
    vehicle_stats = demo_df.groupby('vehicle_id').agg(
        total_demos=('demo_id', 'count'),
        avg_utilization=('utilization_rate', 'mean'),
        total_conversions=('converted', 'sum'),
        market=('market', 'first'),
        vehicle_model=('vehicle_model', 'first'),
        avg_satisfaction=('satisfaction_score', 'mean')
    ).reset_index()

    vehicle_stats['conversion_rate'] = (
        vehicle_stats['total_conversions'] / vehicle_stats['total_demos']
    ).round(4)
    vehicle_stats['vehicle_age_months'] = np.random.randint(1, 36, len(vehicle_stats))
    vehicle_stats['maintenance_flag'] = (
        vehicle_stats['avg_utilization'] > 0.88
    ).astype(int)
    vehicle_stats['underperforming'] = (
        vehicle_stats['conversion_rate'] < vehicle_stats['conversion_rate'].quantile(0.25)
    ).astype(int)

    return vehicle_stats


def generate_market_summary(demo_df):
    summary = demo_df.groupby(['market', 'region', 'market_size']).agg(
        total_demos=('demo_id', 'count'),
        total_conversions=('converted', 'sum'),
        avg_satisfaction=('satisfaction_score', 'mean'),
        avg_drive_duration=('drive_duration_mins', 'mean'),
        avg_utilization=('utilization_rate', 'mean'),
        total_revenue=('revenue_generated', 'sum'),
        total_demo_cost=('demo_cost', 'sum'),
        unique_vehicles=('vehicle_id', 'nunique')
    ).reset_index()

    summary['conversion_rate'] = (
        summary['total_conversions'] / summary['total_demos']
    ).round(4)
    summary['revenue_per_demo'] = (
        summary['total_revenue'] / summary['total_demos']
    ).round(2)
    summary['cost_per_conversion'] = (
        summary['total_demo_cost'] / summary['total_conversions'].replace(0, 1)
    ).round(2)
    summary['roi'] = (
        (summary['total_revenue'] - summary['total_demo_cost']) /
        summary['total_demo_cost']
    ).round(3)

    return summary


def save_to_database(demo_df, vehicle_df, market_df, db_path='data/tesla_fleet.db'):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)

    demo_df.to_sql('demo_drives', conn, if_exists='replace', index=False)
    vehicle_df.to_sql('vehicle_inventory', conn, if_exists='replace', index=False)
    market_df.to_sql('market_summary', conn, if_exists='replace', index=False)

    # Create useful views
    conn.execute("""
        CREATE VIEW IF NOT EXISTS v_market_performance AS
        SELECT
            market,
            region,
            market_size,
            total_demos,
            conversion_rate,
            avg_utilization,
            revenue_per_demo,
            roi,
            CASE
                WHEN conversion_rate >= 0.22 THEN 'High Performer'
                WHEN conversion_rate >= 0.17 THEN 'Average'
                ELSE 'Needs Attention'
            END as performance_tier
        FROM market_summary
        ORDER BY conversion_rate DESC
    """)

    conn.execute("""
        CREATE VIEW IF NOT EXISTS v_weekly_trends AS
        SELECT
            demo_year,
            demo_month,
            demo_month_name,
            demo_quarter,
            vehicle_model,
            region,
            COUNT(*) as total_demos,
            SUM(converted) as conversions,
            ROUND(AVG(CAST(converted AS FLOAT)), 4) as conversion_rate,
            ROUND(AVG(satisfaction_score), 2) as avg_satisfaction,
            SUM(revenue_generated) as total_revenue
        FROM demo_drives
        GROUP BY demo_year, demo_month, vehicle_model, region
    """)

    conn.commit()
    conn.close()
    print(f"Database saved to {db_path}")
    print(f"  demo_drives: {len(demo_df):,} records")
    print(f"  vehicle_inventory: {len(vehicle_df):,} vehicles")
    print(f"  market_summary: {len(market_df):,} markets")


def save_to_csv(demo_df, vehicle_df, market_df):
    os.makedirs('data', exist_ok=True)
    demo_df.to_csv('data/demo_drives.csv', index=False)
    vehicle_df.to_csv('data/vehicle_inventory.csv', index=False)
    market_df.to_csv('data/market_summary.csv', index=False)
    print("CSV files saved to data/")


if __name__ == "__main__":
    print("Generating Tesla Fleet Analytics dataset...")
    print("Simulating 15,000 demo drive records across 15 markets...")

    demo_df = generate_demo_drives(15000)
    vehicle_df = generate_vehicle_inventory(demo_df)
    market_df = generate_market_summary(demo_df)

    save_to_database(demo_df, vehicle_df, market_df)
    save_to_csv(demo_df, vehicle_df, market_df)

    print("\nDataset Summary:")
    print(f"  Total demos: {len(demo_df):,}")
    print(f"  Overall conversion rate: {demo_df['converted'].mean():.1%}")
    print(f"  Total revenue: ${demo_df['revenue_generated'].sum():,.0f}")
    print(f"  Markets covered: {demo_df['market'].nunique()}")
    print(f"  Vehicle models: {demo_df['vehicle_model'].nunique()}")
    print(f"  Date range: {demo_df['demo_date'].min().date()} to {demo_df['demo_date'].max().date()}")
    print("\nDone.")