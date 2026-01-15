from datetime import datetime, timedelta

# Get the current date and time
current_datetime = datetime.now()


startDaily = (current_datetime - timedelta(days=5)).strftime('%Y-%m-%d')
endDaily = current_datetime.strftime('%Y-%m-%d')

startHr = (current_datetime - timedelta(days=2)).strftime('%Y-%m-%d')
endHr = (current_datetime - timedelta(days=0)).strftime('%Y-%m-%d')

stockPriceThreashHold = 15000

startW = (current_datetime - timedelta(days=35)).strftime('%Y-%m-%d')
endW = (current_datetime - timedelta(days=0)).strftime('%Y-%m-%d')

startM = (current_datetime - timedelta(days=120)).strftime('%Y-%m-%d')
endM = (current_datetime - timedelta(days=0)).strftime('%Y-%m-%d')

isGoodFVG = True
tickerGroup = "US"

def get_tickers(type):
    if type == "NIFTY100":
        return ["ADANIENT.NS", "ADANIPORTS.NS", "APOLLOHOSP.NS", "ASIANPAINT.NS", "AXISBANK.NS", "BAJAJ-AUTO.NS",
                "BAJFINANCE.NS", "BAJAJFINSV.NS", "BEL.NS", "BPCL.NS", "BHARTIARTL.NS", "BRITANNIA.NS", "CIPLA.NS",
                "COALINDIA.NS", "DRREDDY.NS", "EICHERMOT.NS", "GRASIM.NS", "HCLTECH.NS", "HDFCBANK.NS", "HDFCLIFE.NS",
                "HEROMOTOCO.NS", "HINDALCO.NS", "HINDUNILVR.NS", "ICICIBANK.NS", "INDUSINDBK.NS", "INFY.NS", "ITC.NS",
                "JSWSTEEL.NS", "KOTAKBANK.NS", "LT.NS", "M&M.NS", "MARUTI.NS", "NESTLEIND.NS", "NTPC.NS", "ONGC.NS",
                "POWERGRID.NS", "RELIANCE.NS", "SBILIFE.NS", "SHRIRAMFIN.NS", "SBIN.NS", "SUNPHARMA.NS", "TCS.NS",
                "TATACONSUM.NS", "TATAMOTORS.NS", "TATASTEEL.NS", "TECHM.NS", "TITAN.NS", "TRENT.NS", "ULTRACEMCO.NS",
                "WIPRO.NS",
                "ADANIENSOL.NS", "ADANIGREEN.NS", "ADANIPOWER.NS", "AMBUJACEM.NS", "ATGL.NS", "BAJAJHLDNG.NS",
                "BANKBARODA.NS", "BHEL.NS", "BOSCHLTD.NS", "CANBK.NS", "CHOLAFIN.NS", "DABUR.NS", "DIVISLAB.NS",
                "DLF.NS", "DMART.NS", "GAIL.NS", "GODREJCP.NS", "HAVELLS.NS", "HAL.NS", "ICICIGI.NS", "ICICIPRULI.NS",
                "IOC.NS", "INDIGO.NS", "NAUKRI.NS", "IRCTC.NS", "IRFC.NS", "JINDALSTEL.NS", "JIOFIN.NS", "JSWENERGY.NS",
                "LICI.NS", "LODHA.NS", "LTIM.NS", "NHPC.NS", "PIDILITIND.NS", "PFC.NS", "PNB.NS", "RECLTD.NS",
                "MOTHERSON.NS", "SHREECEM.NS", "SIEMENS.NS", "TATAPOWER.NS", "TORNTPHARM.NS", "TVSMOTOR.NS",
                "UNIONBANK.NS", "UNITDSPR.NS", "VBL.NS", "VEDL.NS", "ZOMATO.NS", "ZYDUSLIFE.NS"]
    elif type == "UNDER500":
        return ["EIEL.NS", "HINDZINC.NS", "LEMONTREE.NS", "SAMHI.NS", "DELHIVERY.NS", "SAPPHIRE.NS", "PNCINFRA.NS",
                "CHEMPLASTS.NS", "CHALET.NS", "MASFIN.NS", "KRBL.NS", "ONGC.NS", "IDFCFIRSTB.NS", "BANKBARODA.NS",
                "GSFC.NS", "ITC.NS", "NTPC.NS", "POWERGRID.NS", "COALINDIA.NS", "BEL.NS", "JIOFIN.NS", "IRFC.NS",
                "ASHOKLEY.NS", "GENUSPOWER.NS", "TEXRAIL.NS", "PARACABLES.NS", "KRISHIVAL.NS", "BCLIND.NS", "IEX.NS",
                "VEDL.NS", "INDUSTOWER.NS", "MANGCHEFER.NS", "CUB.NS", "BANDHANBNK.NS", "CSBBANK.NS", "LTFOODS.NS",
                "MOTHERSON.NS", "NBCC.NS"]
    elif type == "MINE":
        return ["ABSLAMC.NS", "ADANIENSOL.NS", "AFFLE.NS", "ALKEM.NS", "ARE&M.NS", "ANANTRAJ.NS", "APARINDS.NS",
                "APOLLOHOSP.NS", "APOLLOTYRE.NS", "ASIANPAINT.NS", "AVANTIFEED.NS", "AXISBANK.NS", "BAJAJ-AUTO.NS",
                "BAJAJFINSV.NS", "BAJAJHFL.NS", "BAJFINANCE.NS", "BECTORFOOD.NS", "BHARTIARTL.NS", "BLUESTARCO.NS",
                "BRIGADE.NS", "BRITANNIA.NS", "BSOFT.NS", "CANFINHOME.NS", "CASTROLIND.NS", "CDSL.NS", "CEATLTD.NS",
                "CESC.NS", "CHAMBLFERT.NS", "CMSINFO.NS", "COALINDIA.NS", "COFORGE.NS", "COLPAL.NS", "COROMANDEL.NS",
                "CRAFTSMAN.NS", "CROMPTON.NS", "CYIENT.NS", "DATAPATTNS.NS", "DBEIL.NS", "DIVISLAB.NS", "DLF.NS",
                "DMART.NS", "DRREDDY.NS", "EICHERMOT.NS", "EMAMILTD.NS", "EMBASSY.BS", "ENDURANCE.NS", "EQUITASBNK.NS",
                "EXIDEIND.NS", "FSL.NS", "GABRIEL.NS", "GAIL.NS", "GESHIP.NS", "GHCL.NS", "GLS.NS", "GODREJPROP.NS",
                "GOLDBEES.NS", "GRASIM.NS", "HAL.NS", "HAPPSTMNDS.NS", "HCLTECH.NS", "HDFCBANK.NS", "HDFCLIFE.NS",
                "HEROMOTOCO.NS", "HGINFRA.NS", "HINDUNILVR.NS", "HSCL.NS", "ICICIBANK.NS", "IDFCFIRSTB.NS", "IEX.NS",
                "IKS.NS", "INDHOTEL.NS", "INDIAMART.NS", "INDIGO.NS", "INDUSTOWER.NS", "INFY.NS", "IRFC.NS", "ITC.NS",
                "JINDALSAW.NS", "JIOFIN.NS", "JKIL.NS", "JKLAKSHMI.NS", "JKTYRE.NS", "JSL.NS", "JUNIORBEES.NS",
                "KARURVYSYA.NS", "KFINTECH.NS", "KIRLOSBROS.NS", "KIRLOSENG.NS", "KNRCON.NS", "KOTAKBANK.NS",
                "KPITTECH.NS", "LTF.NS", "LIQUIDBEES.NS", "LIQUIDCASE.NS", "LTFOODS.NS", "LTIM.NS", "LUPIN.NS",
                "M&M.NS", "MAHSEAMLES.NS", "MANINFRA.NS", "MANYAVAR.NS", "MAPMYINDIA.NS", "MARICO.NS", "MARKSANS.NS",
                "MAZDOCK.NS", "MID150BEES.NS", "MID150CASE.NS", "MINDACORP.NS", "MINDSPACE.NS", "MON100.NS",
                "MOTHERSON.NS", "MOTILALOFS.NS", "MPHASIS.NS", "MRPL.NS", "MSUMI.NS", "MTARTECH.NS", "MUTHOOTFIN.NS",
                "NATCOPHARM.NS", "NATIONALUM.NS", "NAVINFLUOR.NS", "NCC.NS", "NESTLEIND.NS", "NEWGEN.NS", "NH.NS",
                "NHPC.NS", "NIFTYBEES.NS", "NMDC.NS", "NTPC.NS", "NXST.NS", "OBEROIRLTY.NS", "OFSS.NS", "OLECTRA.NS",
                "ONGC.NS", "PCBL.NS", "PERSISTENT.NS", "PFC.NS", "PHOENIXLTD.NS", "PIDILITIND.NS", "PNBHOUSING.NS",
                "PNCINFRA.NS", "PNGJL.NS", "POWERGRID.NS", "PRESTIGE.NS", "RAYMOND.NS", "REDINGTON.NS", "RELIANCE.NS",
                "RVNL.NS", "SBIN.NS", "SETFNIF50.NS", "SOBHA.NS", "SONACOMS.NS", "SUNDRMFAST.NS", "SUNPHARMA.NS",
                "SUNTV.NS", "SUZLON.NS", "TATACOMM.NS", "TATAMOTORS.NS", "TATAPOWER.NS", "TATASTEEL.NS", "TATATECH.NS",
                "TCS.NS", "TIMETECHNO.NS", "TIPSMUSIC.NS", "TITAN.NS", "TRENT.NS", "TRIDENT.NS", "TRITURBINE.NS",
                "UTIAMC.NS", "VBL.NS", "VEDL.NS", "VGUARD.NS", "VRLLOG.NS", "VSTIND.NS", "WELCORP.NS", "WIPRO.NS",
                "WONDERLA.NS", "ZOMATO.NS", "ZYDUSLIFE.NS"]
    elif type == "FAV":
        return [ "AFFLE.NS",  "ASIANPAINT.NS", "AXISBANK.NS",
                "BAJAJFINSV.NS", "BAJAJHFL.NS", "BAJFINANCE.NS",  "BHARTIARTL.NS", "BLUESTARCO.NS",
               "BSOFT.NS", "CDSL.NS", "COALINDIA.NS", "COFORGE.NS", "COLPAL.NS", "DATAPATTNS.NS","DLF.NS",
                "DMART.NS", "DRREDDY.NS", "EICHERMOT.NS", "EQUITASBNK.NS",
                "EXIDEIND.NS", "HAL.NS", "HAPPSTMNDS.NS","HDFCBANK.NS",
                 "HINDUNILVR.NS",  "ICICIBANK.NS", "IDFCFIRSTB.NS", "IEX.NS",
                 "INDHOTEL.NS", "INDIAMART.NS", "INDIGO.NS", "INFY.NS", "IRFC.NS", "ITC.NS",
               "JIOFIN.NS",  "KOTAKBANK.NS",
                "KPITTECH.NS", "LTF.NS",
                "M&M.NS", "MAHSEAMLES.NS", "MAPMYINDIA.NS", "MARICO.NS",
                "MAZDOCK.NS",  "MINDACORP.NS", "MON100.NS",
                "MOTHERSON.NS", "MOTILALOFS.NS", "MPHASIS.NS", "MRPL.NS", "MSUMI.NS", "MTARTECH.NS", "MUTHOOTFIN.NS",
               "NAVINFLUOR.NS", "NEWGEN.NS",
               "OLECTRA.NS",
                "ONGC.NS", "PCBL.NS","PFC.NS", "PNBHOUSING.NS",
                "PNCINFRA.NS", "PNGJL.NS", "POWERGRID.NS", "REDINGTON.NS", "RELIANCE.NS",
                "RVNL.NS", "SBIN.NS", "SETFNIF50.NS",
                "SUZLON.NS", "TATACOMM.NS", "TATAMOTORS.NS", "TATAPOWER.NS", "TATASTEEL.NS", "TATATECH.NS",
                "TCS.NS", "TIMETECHNO.NS",  "TITAN.NS", "TRENT.NS", "TRIDENT.NS", "TRITURBINE.NS",
                "VBL.NS", "VEDL.NS", "VRLLOG.NS", "WIPRO.NS",
                "WONDERLA.NS", "ZOMATO.NS", "ZYDUSLIFE.NS"
                 # "policy bazar",
                 # "Delhivery",
                 # APL Apollo Tubes,
                 # Max Financial Services:
                 ]
    elif type == "SINGLE":
        return ["INDHOTEL.NS"]
    elif type == "US":
        return ["AAPL", "MSFT", "NVDA", "GOOGL", "GOOG", "AMZN", "META",
    "TSLA", "NFLX", "ADBE", "AMD", "INTC", "AVGO", "QCOM",
    "MU", "COST", "PEP", "PYPL", "PLTR", "SNOW", # Exchanges
    "COIN", "HOOD", "BKKT",

    # Miners
    "MARA", "RIOT", "CLSK", "HUT", "BITF", "WULF",

    # Payments / FinTech
    "PYPL", "SQ", "V", "MA",

    # Tech / Holdings
    "TSLA", "MSTR", "NVDA", "IBM",

    # Financials
    "GS", "JPM", "BLK"]
    elif type == "RAVI":
        return ["TRANSRAILL.NS", "SHAKTIPUMP.NS", "MOTILALOFS.NS", "E2E.NS", "EPACK.NS", "PNGJL.NS", "PCBL.NS",
                "WAAREEENER.NS", "SAHASRA.NS", "TEJASNET.NS", "ORIENTTECH.NS", "KAYNES.NS", "IGIL.NS", "VMM.NS",
                "SAILIFE.NS", "EMSLIMITED.NS", "WABAG.NS", "RAJESH.BS", "EIEL.NS", "PIGL.NS", "THOMASCOTT.NS",
                "TEMBO.NS", "SALZERELEC.NS", "PREMIERENE.NS", "PGEL.NS", "IZMO.NS", "PPLPHARMA.NS", "BSE.NS", "CDSL.NS",
                "ANGELONE.NS", "DIXON.NS", "MCX.NS", "VPRPL.NS", "KRN.NS"]
    elif type == "ALL":
        ticker = get_tickers("MINE") + get_tickers("UNDER500") + get_tickers("NIFTY100") + get_tickers("RAVI")
        return ticker
    return []

print(get_tickers("SINGLE"))



print(f"Current date and time: {startDaily}")
print(f"Yesterday's date and time: {startM}")



