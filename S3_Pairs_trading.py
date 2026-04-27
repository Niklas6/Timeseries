
import pandas as pd
from dataclasses import dataclass


@dataclass(slots=True)
class PairModel:
    left: str
    right: str
    gamma: float =1/2
    threshold_entry: float =1/100
    #threshold_exit: float =1/10
    #max_exposure: float =200


@dataclass(slots=True)
class Position:
    left: float = 0.0
    right: float = 0.0




def run_strategy(prices: pd.DataFrame,model: PairModel) -> tuple[ float, int, PairModel]:
    '''This function runes the pair trading stategy over a data frame and returns the revenue, trades, updated model'''

    pos = Position()
    left = model.left
    right = model.right
    revenue=0
    trades=0
    for t in prices.index:
        npos = build_target_position( prices.loc[t,left], prices.loc[t,right], model.gamma,model.threshold_entry,pos)
        if npos != pos:
            revenue += prices.loc[t,left] * (pos.left - npos.left) + prices.loc[t,right] * (pos.right - npos.right)
            pos = npos
            trades += 1
        model.gamma=49/50*model.gamma+ 1/50 * prices.loc[t,left]/prices.loc[t,right]
    revenue += prices.loc[t, left] * pos.left  + prices.loc[t, right] * pos.right

    return revenue, trades,model




def build_target_position(y1: float, y2: float, gamma: float, thresh: float, pos: Position) -> Position:
    '''This model updates the position applied to each time stamp.'''
    npos=Position()
    if pos.left > 0:
        if y1 - gamma * y2 < 0:
            return pos
    elif pos.left < 0:
        if y1 - gamma * y2 > 0:
            return pos
    capital = 100

    if y1 - gamma * y2 > thresh * (y1 + gamma * y2):  # y1 is overvalued
        if pos.left >= 0:
            npos.left = -capital/y1
            npos.right = capital/y2
    elif y1 - gamma * y2 < - thresh * (y1 + gamma * y2):  # y2 is overvalued
        if pos.left <= 0:
            npos.left = capital/y1
            npos.right= -capital/y2
    return npos

def build_model(prices_analysis: pd.DataFrame, left: str, right: str):
    '''This function builds the model using the mean.'''
    gamma = (prices_analysis.loc[:,left] / prices_analysis.loc[:,right]).mean()
    return PairModel(left,right, gamma)


def run_analysis_test_model(prices_analysis: pd.DataFrame,prices_test: pd.DataFrame, left: str, right: str):
    '''This function runs the analysis and test.'''

    model=build_model(prices_analysis,left,right)

    revenue_analysis, trades_analysis,model_analysis=run_strategy(prices_analysis,model)
    revenue_test, trades_test,model_test=run_strategy(prices_test,model_analysis)

    return(revenue_analysis, trades_analysis,revenue_test, trades_test)




def main(left: str = 'LRCX',right: str = 'AMAT'):

    prices_analysis = pd.read_csv("Data/semiconductor_close_analysis.csv", index_col="date", parse_dates=True).sort_index().loc[:,[left, right ]]
    prices_test = pd.read_csv("Data/semiconductor_close_trade.csv", index_col="date", parse_dates=True).sort_index().loc[:,[left, right ]]
    revenue_analysis, trades_analysis,revenue_test, trades_test=run_analysis_test_model(prices_analysis,prices_test,left, right )




    return(revenue_analysis, trades_analysis,revenue_test, trades_test)







if __name__ == "__main__":
    main()