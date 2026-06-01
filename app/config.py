SUPPORTED_CURRENCIES = {"GHS", "NGN", "KES", "ZAR", "USD"}
SUPPORTED_PAYMENT_METHODS = {"mobile_money", "bank_transfer"}
# Collection status timing (seconds since it was created).
PROCESSING_AFTER_SECONDS = 10
COMPLETED_AFTER_SECONDS = 20
# How long a quote stays valid.
QUOTE_TTL_SECONDS = 60
# FX fee: 1.2% of the amount, but never less than $0.50.
FEE_RATE = 0.012
MIN_FEE_USD = 0.50

# Exhange rates according to the BoG
EXCHANGE_RATES = {
    "GHS-NGN": 120.8333,      
    "NGN-GHS": 0.008276,    
    "USD-GHS": 11.3400,      
    "USD-NGN": 1370.05,       
    "USD-ZAR": 7.837,         
    "ZAR-USD": 0.1276,        
    "USD-KES": 130.0,
    "KES-USD": 0.007692,
}
