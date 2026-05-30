
from datetime import datetime
from dotenv import load_dotenv
import pandas as pd
import pandas_market_calendars as mkt_cal
import time, traceback
import json

from src.llm_trader import LLMStockTrader


load_dotenv()


def main():
    # initialize llm trading agent
    ticker = "AAPL"
    agent = LLMStockTrader(starting_balance=10000.00)

    start_dt = datetime(2025, 1, 1)
    end_dt = datetime(2025, 12, 31)

    validate_llm_agent(agent, ticker, start_dt, end_dt)



def validate_llm_agent(agent, ticker, start_date, end_date, starting_balance=10000.00, shares_per_trade=10):
    portfolio_values = [starting_balance]
    agent_actions = {}
    exceptions = []

    baseline_values = [starting_balance]
    baseline_cash = starting_balance
    baseline_stocks = 0

    dates = [
        pd.Timestamp("2026-04-15", tz="US/Eastern"), # wednesday
        pd.Timestamp("2026-04-17", tz="US/Eastern"), # friday
        pd.Timestamp("2026-04-22", tz="US/Eastern"), # wednesday
        pd.Timestamp("2026-04-24", tz="US/Eastern"), # last friday of the month
        pd.Timestamp("2026-04-25", tz="US/Eastern"), # saturday
        pd.Timestamp("2026-04-30", tz="US/Eastern"), # last day of the month but it's not a friday
        pd.Timestamp("2026-05-01", tz="US/Eastern")  # beginning of next month
    ]

    # get valid nyse market days
    mkt_days = mkt_cal.get_calendar("NYSE").valid_days(start_date, end_date)
    mkt_days = mkt_days.tz_localize(None).tz_localize("US/Eastern").to_list()

    print(f"Validation Begin : Test Window has {len(mkt_days)} days")
    
    trade_simulations = []

    for date in mkt_days:
        trade_simulations.append(date.replace(hour=12)) # 12 AM Trades
        trade_simulations.append(date.replace(hour=18)) # After hour research/reflections

    for trade_simulation_dt in trade_simulations:
        print(f"..........Simulating trade for time={trade_simulation_dt} : BEGIN..........")

        try:
            # STEP 1: Fetch prices and news articles
            context, current_price = agent.observe(
                ticker=ticker,
                now = trade_simulation_dt,
                hourly_lookback_days=1,
                daily_bars=10,
                weekly_bars=6,
                monthly_bars=4,
                news_articles=6,
                trade_history=20,
                action_summaries=5,
                baseline_metrics=f"Buy & Hold; portfolio value=${baseline_values[-1]:.2f}"
            )

            print(context + '\n\n')
            time.sleep(1)

            # STEP 2: Invoke LLM for a trading decision
            decision = agent.reason(
                ticker=ticker,
                now=trade_simulation_dt,
                mkt_context=context,
                max_shares_per_trade=shares_per_trade
            )
            time.sleep(1)

            print(f"LLM Chain of Thoughts: {decision['reasoning'][:300]}...", end='\n\n')

            # STEP 3: Validate Trade and prepare to publish
            action, ticker, shares, rationale = agent.plan(
                tk=ticker,
                now=trade_simulation_dt,
                llm_outout_str=decision["content"],
                current_price=current_price,
                max_shares_per_trade=shares_per_trade
            )

            print(f"Decision: {action}\nticker: {ticker}\nshares: {shares}\nRationale: {rationale}...", end='\n\n')

            if action in agent_actions:
                agent_actions[action] += 1
            else:
                agent_actions[action] = 1

            time.sleep(1)

            # STEP 4: Execute Trade
            portfolio_value = agent.execute(
                action=action,
                ticker=ticker,
                now=trade_simulation_dt,
                qty=shares, 
                current_price=current_price,
                rationale=rationale
            )

            portfolio_values.append(portfolio_value)

            # calculate baseline, buys 1 share at a time if possible
            if current_price <= baseline_cash and trade_simulation_dt.hour < 16:
                baseline_cash -= current_price
                baseline_stocks += 1

            baseline_value = baseline_cash + baseline_stocks * current_price
            baseline_values.append(baseline_value)
            time.sleep(1)

            # STEP 5: Reflection/Summarize on Fridays
            if trade_simulation_dt.weekday() == 4 and trade_simulation_dt.hour >= 16:
                msg, reasoning = agent.reflect(
                    ticker=ticker,
                    now=trade_simulation_dt
                )

                print(f"Reflection: {msg}\n\nTicker: {ticker}\n\nReasoning: {reasoning[:500]}...", end='\n\n')

        except Exception as e:
            exception_txt = traceback.format_exc()
            print(f"Exception occured during execution loop for {trade_simulation_dt}; {exception_txt}..........")
            
            exceptions.append(exception_txt)
            print("Continuing...")
        finally:
            print(f"Loop Completed!\nActions: {agent_actions};\nPortfolio Value: {portfolio_values[-1]}\nBaseline Value: {baseline_values[-1]}\nErrors: {len(exceptions)}")

            validation_results = {
                "portfolio_final": portfolio_values[-1],
                "baseline_final": baseline_values[-1],
                "test_duration": str(len(mkt_days)) + " days",
                "actions": agent_actions,
                "exceptions_count": len(exceptions),
                "exceptions": exceptions,
                "portfolio_trend": portfolio_values,
                "baseline_trend": baseline_values,
            }

            with open("validation_results.json", 'w') as f:
                json.dump(validation_results, f, indent=4)
            
            print(f"..........{trade_simulation_dt} : END..........\n")
            time.sleep(2)

    print("Validation End : Successfully persisted validation results!")


if __name__ == "__main__":
    main()
