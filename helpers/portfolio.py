from datetime import datetime, timedelta
from extensions import db
from models import Listing, Transaction
from .myFinance50_helpers import company_data, fmp_key

# Defines a class called portfolio, used for /index and /index_detail
class Portfolio:

    def __init__(self):
        # Below are portfolio totals
        self._portfolio_data = {}
        self.cash_initial = 0
        self.cash = 0
        self.portfolio_total_transaction_shares = 0
        self.portfolio_total_shares_outstanding = 0
        self.portfolio_cost_basis_total = 0
        self.portfolio_cost_basis_per_share = 0
        self.portfolio_STCG_unrealized = 0
        self.portfolio_LTCG_unrealized = 0
        self.portfolio_CG_unrealized = 0
        self.portfolio_CG_total_unrealized = 0
        self.portfolio_market_value_total_pre_tax = 0
        self.portfolio_market_value_total_pre_tax_incl_cash = 0
        self.portfolio_market_value_per_share = 0
        self.portfolio_gain_or_loss_pre_tax_percent = 0
        self.portfolio_STCG_tax_unrealized = 0
        self.portfolio_LTCG_tax_unrealized = 0
        self.portfolio_CG_tax_offset_unrealized = 0
        self.portfolio_market_value_post_tax = 0
        self.portfolio_market_value_post_tax_incl_cash = 0
        self.portfolio_return_percent_post_tax = 0
        self.cash_return_percent = 0
    
        # This metric holds the SLD transactions
        self.sell_transactions = []

        # Below are metrics for completed sales
        self.sld_transaction_shares_total = 0
        self.sld_transaction_cost_basis_total = 0
        self.sld_transaction_STCG_total = 0
        self.sld_transaction_LTCG_total = 0
        self.sld_transaction_CG_total_realized_total = 0
        self.sld_transaction_market_value_pre_tax_total = 0
        self.sld_transaction_gain_or_loss_pre_tax_percent = 0
        self.sld_transaction_STCG_tax_total = 0
        self.sld_transaction_LTCG_tax_total = 0
        self.sld_transaction_tax_offset_total = 0
        self.sld_transaction_market_value_post_tax_total = 0
        self.sld_transaction_return_percent_post_tax = 0

        # Below are metrics for open portfolio+cash+sales
        self.total_portfolio_transaction_shares = 0
        self.total_portfolio_STCG = 0
        self.total_portfolio_LTCG = 0
        self.total_portfolio_CG = 0
        self.total_portfolio_market_value_pre_tax = 0
        self.total_portfolio_gain_or_loss_pre_tax_percent = 0
        self.total_portfolio_STCG_tax = 0
        self.total_portfolio_LTCG_tax = 0
        self.total_portfolio_CG_tax_total = 0
        self.total_portfolio_tax_offset = 0
        self.total_portfolio_market_value_post_tax = 0
        self.total_portfolio_market_value_post_tax_percent = 0

    # Adds the symbol to portfolio
    def add_symbol(self, symbol, data):
        self._portfolio_data[symbol] = data

    # Adds symbol-level data
    def get_symbol_data(self, symbol):
        return self._portfolio_data.get(symbol, None)


# Creates an item of the portfolio class and populates it
def process_user_transactions(user):
    print(f'running /process_user_transactions(user) ...  for user { user.id } ...  function started')
    
    # Create an instance of the Portfolio class
    portfolio = Portfolio()
    print(f'running /process_user_transactions(user) ...  for user { user.id } ...  object created')

    # Initialize tax rates and whether cap loss offset is turned on
    tax_rate_STCG = user.tax_rate_STCG / 100
    tax_rate_LTCG = user.tax_rate_LTCG / 100
    tax_offset_coefficient = 1 if user.tax_loss_offsets == 'On' else 0
    cutoff_date = datetime.now() - timedelta(days=365)

    # Query transactions DB to see if user has transactions
    transactions = db.session.query(Transaction).filter_by(user_id= user.id).all()
    
    # If user doesn't have transactions (e.g. a new user, return an empty portfolio object)
    if not transactions:
        return portfolio
    
    # Loop for each transaction record in user_data
    for transaction in transactions:

        # All the metrics below this indent pertain to open positions.         
        if transaction.type == 'BOT':  

            # Establish symbol as the point on which rows will be consolidated
            symbol = transaction.symbol
            
            # If a symbol is new to the portfolio, initialize it to the portfolio
            if symbol not in portfolio._portfolio_data:
                
                # When a new symbol is encountered, set up a new row with the following columns
                portfolio.add_symbol(symbol, {
                    'symbol': symbol,
                    'transaction_shares': 0,
                    'shares_outstanding': 0, 
                    'cost_basis_per_share' : 0,
                    'cost_basis_total' : 0,
                    'market_value_per_share': company_data(symbol, fmp_key)['price'],
                    'market_value_total_pre_tax': 0,
                    'gain_or_loss_pre_tax_percent': 0,
                    'STCG_unrealized': 0,
                    'LTCG_unrealized': 0,
                    'CG_total_unrealized': 0,
                    'STCG_tax_unrealized': 0,
                    'LTCG_tax_unrealized': 0,
                    'CG_tax_offset_unrealized': 0,
                    'CG_total_tax_unrealized': 0,
                    'CG_total_post_tax': 0,
                    'market_value_post_tax': 0,
                    'return_percent_post_tax': 0,
                })

            # Attach the new data fields listed above to portfolio.symbol
            symbol_data = portfolio.get_symbol_data(symbol)

            # Transaction-level metrics: not shown on index b/b it is rolled up into 
            # symbol-level data
            transaction_cost_basis_total = transaction.shares_outstanding * transaction.transaction_value_per_share
            transaction_gain_or_loss = (transaction.shares_outstanding * symbol_data['market_value_per_share']) - transaction_cost_basis_total

            # If ST, then...
            if transaction.timestamp > cutoff_date:
                transaction_STCG_unrealized = transaction_gain_or_loss
                transaction_LTCG_unrealized = 0
                # If a ST gain, then...
                if transaction_STCG_unrealized > 0:
                    transaction_STCG_tax_unrealized = transaction_STCG_unrealized *  tax_rate_STCG
                    transaction_LTCG_tax_unrealized = 0
                    transaction_CG_tax_offset_unrealized = 0
                # If a ST loss, then...
                else:
                    transaction_STCG_tax_unrealized = 0
                    transaction_LTCG_tax_unrealized = 0
                    transaction_CG_tax_offset_unrealized = abs(transaction_STCG_unrealized *  tax_rate_STCG * tax_offset_coefficient)
            # If LT, then...
            else:
                transaction_STCG_unrealized = 0
                transaction_LTCG_unrealized = transaction_gain_or_loss
                # If a LT gain, then...
                if transaction_LTCG_unrealized > 0:
                    transaction_STCG_tax_unrealized = 0
                    transaction_LTCG_tax_unrealized = transaction_LTCG_unrealized *  tax_rate_LTCG
                    transaction_CG_tax_offset_unrealized = 0
                # If a LT loss, then...
                else:
                    transaction_STCG_tax_unrealized = 0
                    transaction_LTCG_tax_unrealized = 0
                    transaction_CG_tax_offset_unrealized = abs(transaction_LTCG_unrealized *  tax_rate_LTCG * tax_offset_coefficient)
                
            transaction_CG_total_unrealized = transaction_STCG_unrealized + transaction_LTCG_unrealized  
            transaction_CG_total_tax_unrealized = transaction_STCG_tax_unrealized + transaction_LTCG_tax_unrealized  
            transaction_market_value_total_pre_tax =  transaction.shares_outstanding * symbol_data['market_value_per_share']
            transaction_gain_or_loss_pre_tax_percent = transaction_market_value_total_pre_tax / transaction_cost_basis_total

            transaction_CG_total_post_tax = transaction_CG_total_unrealized - transaction_CG_total_tax_unrealized
            transaction_market_value_post_tax = transaction_market_value_total_pre_tax - transaction_CG_total_tax_unrealized  
            transaction_return_percent_post_tax = (transaction_market_value_post_tax / transaction_cost_basis_total) - 1 

            # Symbol-level metrics: This is symbol-level data shown on index
            symbol_data['transaction_shares'] += transaction.transaction_shares
            symbol_data['shares_outstanding'] += transaction.shares_outstanding
            symbol_data['cost_basis_total'] += transaction_cost_basis_total
            symbol_data['cost_basis_per_share'] = symbol_data['cost_basis_total'] / symbol_data['shares_outstanding']  

            symbol_data['STCG_unrealized'] += transaction_STCG_unrealized
            symbol_data['LTCG_unrealized'] += transaction_LTCG_unrealized
            symbol_data['CG_total_unrealized'] += transaction_CG_total_unrealized        

            symbol_data['market_value_total_pre_tax'] += transaction_market_value_total_pre_tax
            symbol_data['gain_or_loss_pre_tax_percent'] = symbol_data['CG_total_unrealized'] / symbol_data['cost_basis_total']  
            
            symbol_data['STCG_tax_unrealized'] += transaction_STCG_tax_unrealized
            symbol_data['LTCG_tax_unrealized'] += transaction_LTCG_tax_unrealized    
            symbol_data['CG_total_tax_unrealized'] += transaction_CG_total_tax_unrealized
            symbol_data['CG_tax_offset_unrealized'] += transaction_CG_tax_offset_unrealized
            
            symbol_data['market_value_post_tax'] += transaction_market_value_post_tax
            symbol_data['return_percent_post_tax'] = (symbol_data['market_value_post_tax']/symbol_data['cost_basis_total']) - 1 

        # All the metrics below this indent pertain to open positions. 
        # See 'else' for metrics pertaining to closed trades.        
        else:
            portfolio.sld_transaction_shares_total += transaction.transaction_shares
            
            transaction.cost_basis_total = transaction.transaction_value_total - transaction.STCG - transaction.LTCG
            
            portfolio.sld_transaction_cost_basis_total += transaction.cost_basis_total 

            portfolio.sld_transaction_STCG_total += transaction.STCG
            
            portfolio.sld_transaction_LTCG_total += transaction.LTCG
            
            transaction.CG_total_realized = transaction.STCG + transaction.LTCG
            
            portfolio.sld_transaction_CG_total_realized_total += transaction.CG_total_realized  
            
            #transaction.cost_basis_per_share = transaction.cost_basis_total / transaction.transaction_shares 
            
            portfolio.sld_transaction_market_value_pre_tax_total += transaction.transaction_value_total
            
            # See below for cals. pertaining to: portfolio.sld_transaction_gain_or_loss_pre_tax_percent

            transaction.gain_or_loss_pre_tax_percent = transaction.CG_total_realized / transaction.cost_basis_total
            
            transaction.STCG_tax_realized = max(transaction.STCG_tax, 0)
            
            portfolio.sld_transaction_STCG_tax_total += transaction.STCG_tax_realized 
            
            transaction.LTCG_tax_realized = max(transaction.LTCG_tax, 0)
            
            portfolio.sld_transaction_LTCG_tax_total += transaction.LTCG_tax_realized
            
            transaction.CG_total_tax_realized = max(transaction.STCG * tax_rate_STCG + transaction.LTCG * tax_rate_LTCG, 0)
            
            transaction.CG_tax_offset_unrealized = max(-(transaction.STCG_tax + transaction.LTCG_tax), 0)
            
            portfolio.sld_transaction_tax_offset_total += transaction.CG_tax_offset_unrealized
            
            transaction.market_value_post_tax = transaction.transaction_value_total - transaction.CG_total_tax_realized
            
            portfolio.sld_transaction_market_value_post_tax_total += transaction.market_value_post_tax 

            transaction.return_percent_post_tax = (transaction.market_value_post_tax / transaction.cost_basis_total) - 1
            
            portfolio.sell_transactions.append(transaction) 
            
    # PORTFOLIO-LEVEL METRICS: This is total portfolio data shown at bottom of index tables    
    portfolio.sld_transaction_gain_or_loss_pre_tax_percent = ((portfolio.sld_transaction_market_value_pre_tax_total / portfolio.sld_transaction_cost_basis_total) - 1) if portfolio.sld_transaction_cost_basis_total else "-"
    portfolio.sld_transaction_return_percent_post_tax = ((portfolio.sld_transaction_market_value_post_tax_total / portfolio.sld_transaction_cost_basis_total) - 1) if portfolio.sld_transaction_cost_basis_total else "-"
    
    portfolio.cash = user.cash 
    portfolio.cash_initial = user.cash_initial
    print(f'running /process_user_transactions(user) ...  portfolio.cash is: { portfolio.cash }')

    # Step 3.5: Derive total portfolio cost basis, market value, and returns, all ex cash.
    for symbol, symbol_data in portfolio._portfolio_data.items():
        portfolio.portfolio_total_transaction_shares += symbol_data['transaction_shares']
        portfolio.portfolio_total_shares_outstanding += symbol_data['shares_outstanding']
        portfolio.portfolio_cost_basis_total += symbol_data['cost_basis_total']
        portfolio.portfolio_STCG_unrealized += symbol_data['STCG_unrealized']
        portfolio.portfolio_LTCG_unrealized += symbol_data['LTCG_unrealized']
        portfolio.portfolio_CG_unrealized += portfolio.portfolio_STCG_unrealized + portfolio.portfolio_LTCG_unrealized  
        portfolio.portfolio_market_value_total_pre_tax += symbol_data['market_value_total_pre_tax']
        portfolio.portfolio_STCG_tax_unrealized += symbol_data['STCG_tax_unrealized']
        portfolio.portfolio_LTCG_tax_unrealized += symbol_data['LTCG_tax_unrealized']
        portfolio.portfolio_total_tax_unrealized = portfolio.portfolio_STCG_tax_unrealized + portfolio.portfolio_LTCG_tax_unrealized
        portfolio.portfolio_CG_tax_offset_unrealized += symbol_data['CG_tax_offset_unrealized']

    portfolio.portfolio_cost_basis_per_share = portfolio.portfolio_cost_basis_total / portfolio.portfolio_total_shares_outstanding
    portfolio.portfolio_CG_total_unrealized = portfolio.portfolio_STCG_unrealized + portfolio.portfolio_LTCG_unrealized
    portfolio.portfolio_market_value_per_share = portfolio.portfolio_market_value_total_pre_tax / portfolio.portfolio_total_shares_outstanding
    portfolio.portfolio_market_value_total_pre_tax_incl_cash = portfolio.portfolio_market_value_total_pre_tax + user.cash
    portfolio.portfolio_gain_or_loss_pre_tax_percent = (portfolio.portfolio_market_value_total_pre_tax / portfolio.portfolio_cost_basis_total) -1
    portfolio.portfolio_market_value_post_tax = portfolio.portfolio_market_value_total_pre_tax + min((-portfolio.portfolio_total_tax_unrealized + portfolio.portfolio_CG_tax_offset_unrealized),0)
    portfolio.portfolio_market_value_post_tax_incl_cash = portfolio.portfolio_market_value_post_tax + user.cash
    portfolio.portfolio_return_percent_post_tax = (portfolio.portfolio_market_value_post_tax / portfolio.portfolio_cost_basis_total) -1
    
    # Below are calculations for total portfolio performance, incl. 
    # open positions + cash + sld transactions.
    portfolio.total_portfolio_transaction_shares = portfolio.portfolio_total_transaction_shares + portfolio.sld_transaction_shares_total
    portfolio.total_portfolio_STCG = portfolio.portfolio_STCG_unrealized + portfolio.sld_transaction_STCG_total
    portfolio.total_portfolio_LTCG = portfolio.portfolio_LTCG_unrealized + portfolio.sld_transaction_LTCG_total
    portfolio.total_portfolio_CG = portfolio.portfolio_CG_total_unrealized + portfolio.sld_transaction_CG_total_realized_total
    portfolio.total_portfolio_market_value_pre_tax = portfolio.portfolio_market_value_total_pre_tax_incl_cash + portfolio.sld_transaction_CG_total_realized_total
    portfolio.total_portfolio_gain_or_loss_pre_tax_percent = portfolio.total_portfolio_CG / portfolio.cash_initial  
    portfolio.total_portfolio_STCG_tax =  portfolio.portfolio_STCG_tax_unrealized + portfolio.sld_transaction_STCG_tax_total
    portfolio.total_portfolio_LTCG_tax =  portfolio.portfolio_LTCG_tax_unrealized + portfolio.sld_transaction_LTCG_tax_total
    portfolio.total_portfolio_CG_tax_total = portfolio.total_portfolio_STCG_tax + portfolio.total_portfolio_LTCG_tax  
    portfolio.total_portfolio_tax_offset = portfolio.portfolio_CG_tax_offset_unrealized + portfolio.sld_transaction_tax_offset_total 
    portfolio.total_portfolio_market_value_post_tax =  portfolio.total_portfolio_market_value_pre_tax + min((-portfolio.total_portfolio_CG_tax_total + portfolio.total_portfolio_tax_offset),0)
    portfolio.total_portfolio_market_value_post_tax_percent = (portfolio.total_portfolio_market_value_post_tax /  portfolio.cash_initial) - 1

    # return the portfolio object
    return portfolio
